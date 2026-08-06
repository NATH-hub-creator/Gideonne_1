"""
Implementation du backend OpenAI (et API compatibles : Groq, Azure, Ollama...).

Utilise la librairie officielle `openai` >= 1.30.0.
La base URL est configurable pour pointer vers n'importe quelle API compatible.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

from gideonne.models.base import BaseModel
from gideonne.utils.config import Config

logger = logging.getLogger(__name__)


class OpenAIModel(BaseModel):
    """
    Backend LLM base sur l'API OpenAI.

    Compatible avec tout fournisseur qui expose une API OpenAI-like
    (Groq, Azure OpenAI, Ollama avec le flag `--api openai`, etc.).

    Args:
        config: Configuration du projet.
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self._client = AsyncOpenAI(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
        )
        logger.info(
            "OpenAIModel initialise | base_url=%s | modele=%s",
            config.openai_base_url,
            config.model,
        )

    async def generate(
        self,
        messages: list[dict],
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> tuple[str, list[dict]]:
        """
        Appelle l'API OpenAI et retourne (texte, tool_calls).

        Args:
            messages: Liste de messages au format OpenAI.
            max_tokens: Tokens max pour la reponse.
            temperature: Parametre de creativite.

        Returns:
            (texte_reponse, liste_tool_calls) - liste vide si pas d'outil.
        """
        # TODO: injecter les schemas d'outils dans `tools=` si le registre en contient
        response = await self._client.chat.completions.create(
            model=self.config.model,
            messages=messages,  # type: ignore[arg-type]
            max_tokens=max_tokens,
            temperature=temperature,
        )

        choice = response.choices[0]
        message = choice.message

        # Extraction du texte
        text = message.content or ""

        # Extraction des appels d'outils (si le modele en a fait)
        tool_calls: list[dict] = []
        if message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append(
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                )

        logger.debug(
            "Reponse recue | finish_reason=%s | tool_calls=%d",
            choice.finish_reason,
            len(tool_calls),
        )
        return text, tool_calls
