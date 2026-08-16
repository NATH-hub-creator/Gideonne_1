"""
Backend de stockage JSON pour Gideonne.

Sérialise et désérialise les conversations dans des fichiers JSON
stockés localement. Fonctionne entièrement hors-ligne.

Structure d'un fichier de conversation :
{
    "session_id": "abc123",
    "cree_le": "2026-01-01T10:00:00",
    "modifie_le": "2026-01-01T10:30:00",
    "tours": [
        {"user": "Bonjour", "assistant": "Bonjour ! Comment puis-je vous aider ?"},
        ...
    ]
}
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class JSONBackend:
    """
    Backend de persistance basé sur des fichiers JSON.

    Chaque session est stockée dans un fichier distinct :
        <storage_dir>/<session_id>.json

    Args:
        storage_dir: Chemin du répertoire de stockage.
    """

    def __init__(self, storage_dir: str = "data") -> None:
        self._dir = Path(storage_dir)
        # Création automatique du répertoire s'il n'existe pas
        self._dir.mkdir(parents=True, exist_ok=True)
        logger.debug("JSONBackend initialisé | répertoire=%s", self._dir.resolve())

    def _chemin_session(self, session_id: str) -> Path:
        """Retourne le chemin du fichier JSON pour une session donnée."""
        # Nettoyage du session_id pour éviter les traversées de répertoire
        safe_id = "".join(c for c in session_id if c.isalnum() or c in "-_")
        return self._dir / f"{safe_id}.json"

    def sauvegarder(self, session_id: str, tours: list[dict]) -> None:
        """
        Sauvegarde les tours d'une session dans son fichier JSON.

        Args:
            session_id: Identifiant unique de la session.
            tours: Liste de dicts {"user": ..., "assistant": ...}.
        """
        chemin = self._chemin_session(session_id)
        maintenant = datetime.now().isoformat()

        # Chargement de l'existant pour conserver la date de création
        if chemin.exists():
            try:
                existant = json.loads(chemin.read_text(encoding="utf-8"))
                cree_le = existant.get("cree_le", maintenant)
            except (json.JSONDecodeError, OSError):
                cree_le = maintenant
        else:
            cree_le = maintenant

        donnees = {
            "session_id": session_id,
            "cree_le": cree_le,
            "modifie_le": maintenant,
            "tours": tours,
        }

        try:
            chemin.write_text(
                json.dumps(donnees, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            logger.debug(
                "Session '%s' sauvegardée | %d tours", session_id, len(tours)
            )
        except OSError as exc:
            logger.error("Impossible de sauvegarder la session '%s' : %s", session_id, exc)
            raise

    def charger(self, session_id: str) -> list[dict]:
        """
        Charge les tours d'une session depuis son fichier JSON.

        Args:
            session_id: Identifiant unique de la session.

        Returns:
            Liste de dicts {"user": ..., "assistant": ...}.
            Liste vide si la session n'existe pas encore.
        """
        chemin = self._chemin_session(session_id)

        if not chemin.exists():
            logger.debug("Aucune session trouvée pour '%s'.", session_id)
            return []

        try:
            donnees = json.loads(chemin.read_text(encoding="utf-8"))
            tours = donnees.get("tours", [])
            logger.debug(
                "Session '%s' chargée | %d tours", session_id, len(tours)
            )
            return tours
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Erreur de lecture pour la session '%s' : %s", session_id, exc)
            return []

    def supprimer(self, session_id: str) -> bool:
        """
        Supprime le fichier JSON d'une session.

        Args:
            session_id: Identifiant de la session à supprimer.

        Returns:
            True si la suppression a réussi, False si le fichier n'existait pas.
        """
        chemin = self._chemin_session(session_id)
        if chemin.exists():
            chemin.unlink()
            logger.info("Session '%s' supprimée.", session_id)
            return True
        return False

    def lister_sessions(self) -> list[str]:
        """
        Retourne la liste des identifiants de toutes les sessions sauvegardées.

        Returns:
            Liste de session_ids triés par date de modification (plus récent en premier).
        """
        fichiers = sorted(
            self._dir.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
        return [f.stem for f in fichiers]
