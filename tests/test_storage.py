"""
Tests unitaires pour le module de stockage de Gideonne.

Vérifie le comportement de :
  - JSONBackend           : lecture/écriture/suppression de fichiers JSON
  - ConversationStore     : persistance et restauration de la mémoire
"""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from gideonne.core.memory import ConversationMemory
from gideonne.storage.json_backend import JSONBackend
from gideonne.storage.conversation_store import ConversationStore


# ---------------------------------------------------------------------------
# Tests : JSONBackend
# ---------------------------------------------------------------------------

class TestJSONBackend:
    """Tests du backend de stockage JSON."""

    def setup_method(self, tmp_path_factory=None):
        """Utilise un répertoire temporaire pour chaque test."""
        # Création manuelle d'un répertoire temp (compatible sans fixture pytest)
        import tempfile
        self._tmpdir = tempfile.mkdtemp(prefix="gideonne_test_")
        self.backend = JSONBackend(storage_dir=self._tmpdir)

    def teardown_method(self):
        """Nettoyage du répertoire temporaire."""
        import shutil
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_sauvegarder_et_charger(self):
        """Un enregistrement sauvegardé doit être rechargeable."""
        tours = [
            {"user": "Bonjour", "assistant": "Salut !"},
            {"user": "Comment vas-tu ?", "assistant": "Très bien, merci."},
        ]
        self.backend.sauvegarder("session_test", tours)
        resultat = self.backend.charger("session_test")
        assert resultat == tours

    def test_charger_session_inexistante(self):
        """Charger une session qui n'existe pas doit retourner une liste vide."""
        resultat = self.backend.charger("session_inexistante_xyz")
        assert resultat == []

    def test_sauvegarder_conserve_date_creation(self):
        """Une deuxième sauvegarde ne doit pas écraser la date de création."""
        self.backend.sauvegarder("ma_session", [{"user": "a", "assistant": "b"}])

        # Lecture de la date de création initiale
        fichier = Path(self._tmpdir) / "ma_session.json"
        donnees_init = json.loads(fichier.read_text(encoding="utf-8"))
        cree_le_init = donnees_init["cree_le"]

        # Deuxième sauvegarde
        self.backend.sauvegarder("ma_session", [{"user": "x", "assistant": "y"}])
        donnees_apres = json.loads(fichier.read_text(encoding="utf-8"))
        assert donnees_apres["cree_le"] == cree_le_init

    def test_supprimer_session(self):
        """Supprimer une session doit effacer le fichier."""
        self.backend.sauvegarder("session_a_supprimer", [])
        supprime = self.backend.supprimer("session_a_supprimer")
        assert supprime is True
        # Vérification que la session est bien partie
        assert self.backend.charger("session_a_supprimer") == []

    def test_supprimer_session_inexistante(self):
        """Supprimer une session inexistante doit retourner False sans lever d'exception."""
        assert self.backend.supprimer("fantome") is False

    def test_lister_sessions(self):
        """La liste doit contenir toutes les sessions sauvegardées."""
        self.backend.sauvegarder("s1", [])
        self.backend.sauvegarder("s2", [])
        sessions = self.backend.lister_sessions()
        assert "s1" in sessions
        assert "s2" in sessions

    def test_session_id_avec_caracteres_speciaux(self):
        """Les caractères dangereux doivent être ignorés pour éviter les traversées."""
        # "../secret" devient "secret" après nettoyage
        tours = [{"user": "test", "assistant": "ok"}]
        self.backend.sauvegarder("../secret", tours)
        # Aucune exception ne doit être levée


# ---------------------------------------------------------------------------
# Tests : ConversationStore
# ---------------------------------------------------------------------------

class TestConversationStore:
    """Tests de l'orchestrateur de persistance."""

    def setup_method(self):
        import tempfile
        self._tmpdir = tempfile.mkdtemp(prefix="gideonne_store_test_")
        self.backend = JSONBackend(storage_dir=self._tmpdir)
        self.store = ConversationStore(backend=self.backend, session_id="test_conv")

    def teardown_method(self):
        import shutil
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_persister_et_restaurer(self):
        """Persister une mémoire et la restaurer dans une nouvelle instance."""
        # Alimentation de la mémoire originale
        memoire_originale = ConversationMemory(max_turns=10)
        memoire_originale.add_turn(user="Salut", assistant="Bonjour !")
        memoire_originale.add_turn(user="Qui es-tu ?", assistant="Je suis Gideonne.")

        # Persistance
        self.store.persister(memoire_originale)

        # Restauration dans une mémoire vierge
        memoire_restauree = ConversationMemory(max_turns=10)
        tours_recharges = self.store.restaurer(memoire_restauree)

        assert tours_recharges == 2
        assert memoire_restauree.turn_count == 2

    def test_restaurer_session_vide(self):
        """Restaurer une session inexistante ne doit pas lever d'exception."""
        memoire = ConversationMemory(max_turns=10)
        store_vide = ConversationStore(
            backend=self.backend, session_id="aucune_session"
        )
        tours = store_vide.restaurer(memoire)
        assert tours == 0
        assert memoire.turn_count == 0

    def test_effacer_session(self):
        """Effacer une session doit la rendre inaccessible."""
        memoire = ConversationMemory(max_turns=5)
        memoire.add_turn(user="test", assistant="ok")
        self.store.persister(memoire)
        self.store.effacer()

        # Après effacement, la restauration ne doit rien trouver
        memoire_vide = ConversationMemory(max_turns=5)
        assert self.store.restaurer(memoire_vide) == 0
