"""
Agent principal de Gideonne.

L'agent orchestre le cycle complet :
  1. Reception du message utilisateur
  2. Construction du contexte (systeme + historique + message)
  3. Appel au modele LLM
  4. Detection et execution des outils si necessaire
  5. Mise a jour de la memoire
  6. Retour de la reponse
"""

from __future__ import annotations

import logging
from typing import Optional

from gideonne.core.memory import ConversationMemory
from gideonne.core.prompt import PromptBuilder
from gideonne.models.base import BaseModel
from gideonne.tools.registry import ToolRegistry
from gideonne.utils.config import Config

logger = logging.getLogger(__name__)


class GideonneAgent:
    """
    Agent conversationnel Gideonne.

    Usage:
        config = Config.from_env()
        model = OpenAIModel(config)
        agent = GideonneAgent(config=config, model=model)
        response = await agent.chat("Bonjour Gideonne !")
    """

    def __init__(
        self,
        config: Config,
        model: BaseModel,
        tool_registry: Optional[ToolRegistry] = None,
    ) -> None:
        """
        Initialise l'agent.

        Args:
            config: Configuration du projet (variables d'env).
            model: Instance du modele LLM a utiliser.
            tool_registry: Registre des outils disponibles (optionnel).
        """
        self.config = config
        self.model = model
        self.memory = ConversationMemory(max_turns=config.memory_size)
        self.prompt_builder = PromptBuilder(config=config)
        self.tool_registry = tool_registry or ToolRegistry()

        logger.info(
            "GideonneAgent initialise | modele=%s | memoire=%d tours",
            config.model,
            config.memory_size,
        )

    async def chat(self, user_message: str) -> str:
        """
        Traite un message utilisateur et retourne la reponse de l'agent.

        Args:
            user_message: Le message saisi par l'utilisateur.

        Returns:
            La reponse generee par Gideonne.
        """
        logger.debug("Message recu : %s", user_message[:80])

        # Construction du contexte complet a envoyer au LLM
        messages = self.prompt_builder.build(
            history=self.memory.get_history(),
            user_message=user_message,
            tools=self.tool_registry.get_tool_schemas(),
        )

        # Appel au modele
        response_text, tool_calls = await self.model.generate(
            messages=messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
        )

        # Execution des appels d'outils si le modele en a demande
        if tool_calls:
            tool_results = await self._execute_tool_calls(tool_calls)
            # On re-injecte les resultats pour que le modele formule la reponse finale
            messages_with_results = self.prompt_builder.build_with_tool_results(
                messages=messages,
                tool_calls=tool_calls,
                tool_results=tool_results,
            )
            response_text, _ = await self.model.generate(
                messages=messages_with_results,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )

        # Mise a jour de la memoire
        self.memory.add_turn(user=user_message, assistant=response_text)

        logger.debug("Reponse generee : %s", response_text[:80])
        return response_text

    async def _execute_tool_calls(
        self, tool_calls: list[dict]
    ) -> list[dict]:
        """
        Execute une liste d'appels d'outils demandes par le modele.

        Args:
            tool_calls: Liste des appels d'outils au format OpenAI.

        Returns:
            Liste des resultats, au format attendu par l'API.
        """
        results = []
        for call in tool_calls:
            tool_name = call.get("function", {}).get("name", "")
            tool_args = call.get("function", {}).get("arguments", "{}")

            logger.info("Execution de l'outil : %s", tool_name)
            result = await self.tool_registry.execute(tool_name, tool_args)
            results.append(
                {
                    "tool_call_id": call.get("id", ""),
                    "role": "tool",
                    "name": tool_name,
                    "content": str(result),
                }
            )
        return results

    def reset(self) -> None:
        """Reinitialise la memoire conversationnelle (nouvelle session)."""
        self.memory.clear()
        logger.info("Memoire de l'agent reinitisalisee.")
