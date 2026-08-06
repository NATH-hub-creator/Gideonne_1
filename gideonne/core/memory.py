"""
Gestion de la memoire conversationnelle de Gideonne.

Implemente une fenetre glissante : on conserve les N derniers tours
(paire user/assistant) pour rester dans le contexte du LLM.
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Deque

logger = logging.getLogger(__name__)


class Turn:
    """Represente un tour de conversation (message utilisateur + reponse assistant)."""

    __slots__ = ("user", "assistant")

    def __init__(self, user: str, assistant: str) -> None:
        self.user = user
        self.assistant = assistant

    def to_messages(self) -> list[dict]:
        """Convertit le tour en paire de messages au format OpenAI."""
        return [
            {"role": "user", "content": self.user},
            {"role": "assistant", "content": self.assistant},
        ]


class ConversationMemory:
    """
    Memoire conversationnelle a fenetre glissante.

    Args:
        max_turns: Nombre maximum de tours conserves en memoire.
    """

    def __init__(self, max_turns: int = 20) -> None:
        self._max_turns = max_turns
        self._turns: Deque[Turn] = deque(maxlen=max_turns)
        logger.debug("ConversationMemory initialisee | max_turns=%d", max_turns)

    def add_turn(self, user: str, assistant: str) -> None:
        """
        Ajoute un nouveau tour en memoire.
        Si la capacite est atteinte, le tour le plus ancien est automatiquement evince.

        Args:
            user: Message de l'utilisateur.
            assistant: Reponse generee par l'agent.
        """
        self._turns.append(Turn(user=user, assistant=assistant))
        logger.debug(
            "Tour ajoute en memoire | total=%d / %d",
            len(self._turns),
            self._max_turns,
        )

    def get_history(self) -> list[dict]:
        """
        Retourne l'historique complet sous forme de liste de messages OpenAI.

        Returns:
            Liste de dicts {role, content} dans l'ordre chronologique.
        """
        messages = []
        for turn in self._turns:
            messages.extend(turn.to_messages())
        return messages

    def clear(self) -> None:
        """Efface tout l'historique conversationnel."""
        self._turns.clear()
        logger.info("Memoire effacee.")

    @property
    def turn_count(self) -> int:
        """Nombre de tours actuellement en memoire."""
        return len(self._turns)
