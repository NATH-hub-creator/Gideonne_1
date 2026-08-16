"""
Module de stockage persistant pour Gideonne.

Permet de sauvegarder et de recharger les conversations
entre plusieurs sessions (redémarrages du programme).

Backend par défaut : fichiers JSON dans le répertoire `data/`.
"""

from gideonne.storage.conversation_store import ConversationStore
from gideonne.storage.json_backend import JSONBackend

__all__ = ["ConversationStore", "JSONBackend"]
