"""
Construction des prompts systeme pour Gideonne.

Ce module centralise la definition du prompt systeme et l'assemblage
du contexte complet envoye au LLM a chaque appel.
"""

from __future__ import annotations

import logging
from typing import Any

from gideonne.utils.config import Config

logger = logging.getLogger(__name__)

# Prompt systeme par defaut de Gideonne.
# Modifiable ici ou via la config pour adapter la personnalite.
DEFAULT_SYSTEM_PROMPT = """\
Tu es Gideonne, une intelligence artificielle conversationnelle developpee par Nathanael.
Tu es precise, bienveillante, et tu communiques en francais par defaut.
Tu penses de maniere structuree : tu identifies d'abord le besoin de l'utilisateur,
tu formules ensuite une reponse claire et utile.
Si tu ne sais pas quelque chose, tu le dis honnement plutot que d'inventer.
Tu peux utiliser des outils si necessaire pour repondre a des questions factuelles
ou effectuer des actions concretes.
"""


class PromptBuilder:
    """
    Construit les listes de messages a envoyer au LLM.

    Args:
        config: Configuration du projet.
        system_prompt: Prompt systeme personnalise (optionnel).
    """

    def __init__(
        self,
        config: Config,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> None:
        self.config = config
        self.system_prompt = system_prompt

    def build(
        self,
        history: list[dict],
        user_message: str,
        tools: list[dict] | None = None,
    ) -> list[dict]:
        """
        Assemble le contexte complet : systeme + historique + message courant.

        Args:
            history: Historique des messages precedents (format OpenAI).
            user_message: Message courant de l'utilisateur.
            tools: Schemas des outils disponibles (non utilise dans le prompt
                   mais conserve pour la signature, l'API les recoit a part).

        Returns:
            Liste de messages prete a etre envoyee au LLM.
        """
        messages: list[dict] = [
            {"role": "system", "content": self.system_prompt}
        ]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        return messages

    def build_with_tool_results(
        self,
        messages: list[dict],
        tool_calls: list[dict],
        tool_results: list[dict],
    ) -> list[dict]:
        """
        Re-injecte les resultats d'outils dans le contexte pour que le LLM
        formule sa reponse finale.

        Args:
            messages: Contexte initial (avant l'appel au LLM).
            tool_calls: Appels d'outils demandes par le modele.
            tool_results: Resultats de l'execution des outils.

        Returns:
            Contexte enrichi des resultats.
        """
        extended = list(messages)
        # Message de l'assistant qui a demande les outils
        extended.append(
            {"role": "assistant", "content": None, "tool_calls": tool_calls}
        )
        # Resultats des outils
        extended.extend(tool_results)
        return extended
