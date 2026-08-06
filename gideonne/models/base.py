"""
Interface abstraite pour les modeles LLM.

Tout nouveau backend (Anthropic, Mistral, modele local via Ollama...)
doit implementer cette interface pour etre utilisable par GideonneAgent.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseModel(ABC):
    """
    Interface commune pour tous les backends LLM.

    Methodes a implementer :
      - generate : appel au modele, retourne (texte, tool_calls)
    """

    @abstractmethod
    async def generate(
        self,
        messages: list[dict],
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> tuple[str, list[dict]]:
        """
        Genere une reponse a partir d'une liste de messages.

        Args:
            messages: Historique + message courant au format OpenAI.
            max_tokens: Nombre maximum de tokens dans la reponse.
            temperature: Creativite du modele (0 = deterministhe, 1 = creatif).

        Returns:
            Un tuple (texte_reponse, liste_tool_calls).
            liste_tool_calls est vide si le modele n'a demande aucun outil.
        """
        ...
