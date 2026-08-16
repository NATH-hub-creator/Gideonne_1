"""
Gestionnaire de conversations persistantes pour Gideonne.

Fait le lien entre la mémoire conversationnelle en RAM (ConversationMemory)
et le backend de persistance (JSONBackend).

Flux typique :
    store = ConversationStore(backend=JSONBackend("data"), session_id="session_1")
    store.restaurer(agent.memory)  # recharge l'historique au démarrage
    ...  # conversation normale via agent.chat()
    store.persister(agent.memory)  # sauvegarde après chaque tour ou à la fin
"""

from __future__ import annotations

import logging
from typing import Optional

from gideonne.core.memory import ConversationMemory
from gideonne.storage.json_backend import JSONBackend

logger = logging.getLogger(__name__)


class ConversationStore:
    """
    Orchestrateur de persistance des conversations.

    Args:
        backend: Backend de stockage (JSONBackend ou tout autre implémentation).
        session_id: Identifiant unique de la session à gérer.
    """

    def __init__(
        self,
        backend: JSONBackend,
        session_id: str = "default",
    ) -> None:
        self.backend = backend
        self.session_id = session_id

    def persister(self, memoire: ConversationMemory) -> None:
        """
        Sauvegarde l'état actuel de la mémoire dans le backend.

        À appeler après chaque tour ou en fin de session.

        Args:
            memoire: La mémoire conversationnelle de l'agent.
        """
        # Extraction des tours au format stockage {user, assistant}
        tours = self._extraire_tours(memoire)
        self.backend.sauvegarder(self.session_id, tours)
        logger.debug(
            "Mémoire persistée | session=%s | tours=%d",
            self.session_id,
            len(tours),
        )

    def restaurer(self, memoire: ConversationMemory) -> int:
        """
        Recharge une session sauvegardée dans la mémoire de l'agent.

        À appeler au démarrage pour reprendre une conversation interrompue.

        Args:
            memoire: La mémoire conversationnelle à alimenter.

        Returns:
            Nombre de tours rechargés (0 si aucune session existante).
        """
        tours = self.backend.charger(self.session_id)

        if not tours:
            logger.debug("Aucun historique à restaurer pour '%s'.", self.session_id)
            return 0

        # Réinjection des tours dans la mémoire, dans l'ordre chronologique
        for tour in tours:
            user = tour.get("user", "")
            assistant = tour.get("assistant", "")
            if user and assistant:
                memoire.add_turn(user=user, assistant=assistant)

        logger.info(
            "Session '%s' restaurée | %d tours rechargés.",
            self.session_id,
            len(tours),
        )
        return len(tours)

    def effacer(self) -> None:
        """
        Supprime la session du backend de stockage.
        La mémoire en RAM n'est pas modifiée par cette méthode.
        """
        self.backend.supprimer(self.session_id)
        logger.info("Session '%s' effacée du stockage.", self.session_id)

    @staticmethod
    def _extraire_tours(memoire: ConversationMemory) -> list[dict]:
        """
        Convertit la mémoire en liste de dicts pour le backend.

        Args:
            memoire: La mémoire conversationnelle.

        Returns:
            Liste de dicts {"user": ..., "assistant": ...}.
        """
        # Accès direct aux tours internes (sans passer par le format OpenAI)
        return [
            {"user": tour.user, "assistant": tour.assistant}
            for tour in memoire._turns
        ]
