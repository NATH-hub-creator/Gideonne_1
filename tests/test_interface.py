"""
Tests unitaires pour le module d'interface de Gideonne.

Vérifie que :
  - CLIInterface peut être instanciée sans erreur
  - APIInterface crée une application FastAPI fonctionnelle (si disponible)
  - Les endpoints /status, /chat, /reset répondent correctement
"""

from __future__ import annotations

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from gideonne.core.agent import GideonneAgent
from gideonne.core.memory import ConversationMemory
from gideonne.utils.config import Config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def creer_agent_mock() -> GideonneAgent:
    """
    Crée un agent Gideonne avec un modèle simulé (mock).
    Évite tout appel réel à une API LLM pendant les tests.
    """
    config = Config()  # valeurs par défaut
    model_mock = MagicMock()
    # chat() appelle model.generate() en async
    model_mock.generate = AsyncMock(return_value=("Réponse simulée de Gideonne.", []))

    agent = GideonneAgent.__new__(GideonneAgent)
    agent.config = config
    agent.model = model_mock
    agent.memory = ConversationMemory(max_turns=config.memory_size)

    # Import local pour éviter la circularité
    from gideonne.core.prompt import PromptBuilder
    from gideonne.tools.registry import ToolRegistry
    agent.prompt_builder = PromptBuilder(config=config)
    agent.tool_registry = ToolRegistry()

    return agent


# ---------------------------------------------------------------------------
# Tests : CLIInterface
# ---------------------------------------------------------------------------

class TestCLIInterface:
    """Tests basiques de l'interface CLI."""

    def test_instanciation(self):
        """CLIInterface doit être instanciée sans lever d'exception."""
        from gideonne.interface.cli import CLIInterface
        agent = creer_agent_mock()
        cli = CLIInterface(agent=agent, invite="Test > ")
        assert cli.invite == "Test > "
        assert cli.agent is agent

    def test_afficher_aide_ne_leve_pas(self, capsys):
        """La méthode _afficher_aide() doit écrire dans stdout sans exception."""
        from gideonne.interface.cli import CLIInterface
        agent = creer_agent_mock()
        cli = CLIInterface(agent=agent)
        cli._afficher_aide()
        sortie = capsys.readouterr().out
        assert "/quitter" in sortie


# ---------------------------------------------------------------------------
# Tests : APIInterface (nécessite FastAPI + httpx)
# ---------------------------------------------------------------------------

try:
    from fastapi.testclient import TestClient
    from gideonne.interface.api import APIInterface
    _FASTAPI_DISPO = True
except ImportError:
    _FASTAPI_DISPO = False


@pytest.mark.skipif(not _FASTAPI_DISPO, reason="FastAPI ou httpx non installé")
class TestAPIInterface:
    """Tests des endpoints REST via TestClient de FastAPI."""

    def setup_method(self):
        self.agent = creer_agent_mock()
        self.interface = APIInterface(agent=self.agent)
        self.client = TestClient(self.interface.app)

    def test_status_ok(self):
        """GET /status doit retourner 200 avec statut 'ok'."""
        reponse = self.client.get("/status")
        assert reponse.status_code == 200
        donnees = reponse.json()
        assert donnees["statut"] == "ok"
        assert "version" in donnees
        assert "modele" in donnees

    def test_chat_message_valide(self):
        """
        POST /chat avec un message valide doit retourner 200
        et une réponse non vide.
        """
        # On intercepte agent.chat pour retourner une réponse prédéfinie
        self.agent.chat = AsyncMock(return_value="Bonjour, je suis Gideonne.")
        reponse = self.client.post("/chat", json={"message": "Qui es-tu ?"})
        assert reponse.status_code == 200
        donnees = reponse.json()
        assert "reponse" in donnees
        assert len(donnees["reponse"]) > 0

    def test_chat_message_vide(self):
        """POST /chat avec un message vide doit retourner 400."""
        reponse = self.client.post("/chat", json={"message": ""})
        assert reponse.status_code == 400

    def test_reset_vide_la_memoire(self):
        """POST /reset doit vider la mémoire et retourner 200."""
        self.agent.memory.add_turn(user="test", assistant="ok")
        assert self.agent.memory.turn_count == 1
        reponse = self.client.post("/reset")
        assert reponse.status_code == 200
        assert self.agent.memory.turn_count == 0
