"""
Tests unitaires pour le module core de Gideonne.

Vérifie le comportement de :
  - ConversationMemory  : gestion de la fenêtre glissante
  - PromptBuilder       : assemblage des messages
  - ToolRegistry        : enregistrement et exécution des outils

Note : GideonneAgent n'est pas testé ici en intégralité car il nécessite
un modèle LLM réel. Les tests d'intégration complets sont dans le dossier
tests/integration/ (créé ultérieurement avec un mock de l'API).
"""

from __future__ import annotations

import asyncio
import pytest

from gideonne.core.memory import ConversationMemory
from gideonne.core.prompt import PromptBuilder, DEFAULT_SYSTEM_PROMPT
from gideonne.tools.registry import ToolRegistry
from gideonne.tools.calculator import CalculatorTool
from gideonne.utils.config import Config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(coro):
    """Exécute une coroutine en contexte synchrone."""
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# Tests : ConversationMemory
# ---------------------------------------------------------------------------

class TestConversationMemory:
    """Tests de la mémoire conversationnelle à fenêtre glissante."""

    def test_ajouter_un_tour(self):
        """Un tour ajouté doit être reflété dans turn_count."""
        mem = ConversationMemory(max_turns=5)
        mem.add_turn(user="Bonjour", assistant="Salut !")
        assert mem.turn_count == 1

    def test_fenetre_glissante(self):
        """Au-delà de max_turns, les anciens tours sont évincés."""
        mem = ConversationMemory(max_turns=3)
        for i in range(5):
            mem.add_turn(user=f"msg_{i}", assistant=f"rep_{i}")
        # Seuls les 3 derniers doivent être présents
        assert mem.turn_count == 3

    def test_get_history_format_openai(self):
        """L'historique doit être au format OpenAI (list de dicts role/content)."""
        mem = ConversationMemory(max_turns=5)
        mem.add_turn(user="Question", assistant="Réponse")
        history = mem.get_history()
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
        assert history[0]["content"] == "Question"

    def test_clear_vide_la_memoire(self):
        """clear() doit vider complètement la mémoire."""
        mem = ConversationMemory(max_turns=5)
        mem.add_turn(user="a", assistant="b")
        mem.clear()
        assert mem.turn_count == 0
        assert mem.get_history() == []

    def test_memoire_vide_retourne_liste_vide(self):
        """Une mémoire neuve doit retourner un historique vide."""
        mem = ConversationMemory()
        assert mem.get_history() == []
        assert mem.turn_count == 0


# ---------------------------------------------------------------------------
# Tests : PromptBuilder
# ---------------------------------------------------------------------------

class TestPromptBuilder:
    """Tests de l'assembleur de prompts."""

    def setup_method(self):
        self.config = Config()  # valeurs par défaut
        self.builder = PromptBuilder(config=self.config)

    def test_build_inclut_system_prompt(self):
        """Le premier message doit être le prompt système."""
        messages = self.builder.build(history=[], user_message="Bonjour")
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == DEFAULT_SYSTEM_PROMPT

    def test_build_inclut_message_utilisateur(self):
        """Le dernier message doit être celui de l'utilisateur."""
        messages = self.builder.build(history=[], user_message="Qui es-tu ?")
        assert messages[-1]["role"] == "user"
        assert messages[-1]["content"] == "Qui es-tu ?"

    def test_build_inclut_historique(self):
        """L'historique doit être inséré entre le système et le message courant."""
        historique = [
            {"role": "user", "content": "Premier message"},
            {"role": "assistant", "content": "Première réponse"},
        ]
        messages = self.builder.build(history=historique, user_message="Deuxième message")
        # Ordre attendu : système | historique (2) | message courant
        assert len(messages) == 4
        assert messages[1]["role"] == "user"
        assert messages[2]["role"] == "assistant"
        assert messages[3]["content"] == "Deuxième message"


# ---------------------------------------------------------------------------
# Tests : ToolRegistry
# ---------------------------------------------------------------------------

class TestToolRegistry:
    """Tests du registre d'outils."""

    def setup_method(self):
        self.registry = ToolRegistry()

    def test_enregistrer_un_outil(self):
        """Un outil enregistré doit apparaître dans tool_names."""
        self.registry.register(CalculatorTool())
        assert "calculatrice" in self.registry.tool_names

    def test_enregistrement_doublon_leve_exception(self):
        """Enregistrer deux fois le mêtre outil doit lever ValueError."""
        self.registry.register(CalculatorTool())
        with pytest.raises(ValueError):
            self.registry.register(CalculatorTool())

    def test_get_tool_schemas_retourne_liste(self):
        """Les schémas JSON doivent être une liste de dicts valides."""
        self.registry.register(CalculatorTool())
        schemas = self.registry.get_tool_schemas()
        assert isinstance(schemas, list)
        assert len(schemas) == 1
        assert schemas[0]["type"] == "function"

    def test_executer_outil_connu(self):
        """Exécuter un outil enregistré avec des arguments JSON valides."""
        self.registry.register(CalculatorTool())
        resultat = run(self.registry.execute("calculatrice", '{"expression": "2 + 2"}'))
        assert "4" in str(resultat)

    def test_executer_outil_inconnu(self):
        """Tenter d'exécuter un outil non enregistré doit retourner un message d'erreur."""
        resultat = run(self.registry.execute("outil_fantome", "{}"))
        assert "erreur" in str(resultat).lower() or "non disponible" in str(resultat).lower()

    def test_desinscrire_outil(self):
        """Un outil désinscrit ne doit plus être dans tool_names."""
        self.registry.register(CalculatorTool())
        self.registry.unregister("calculatrice")
        assert "calculatrice" not in self.registry.tool_names


# ---------------------------------------------------------------------------
# Tests : Config
# ---------------------------------------------------------------------------

class TestConfig:
    """Tests de la configuration."""

    def test_valeurs_par_defaut(self):
        """Les valeurs par défaut doivent être cohérentes."""
        config = Config()
        assert config.model == "gpt-4o-mini"
        assert config.max_tokens == 2048
        assert 0.0 <= config.temperature <= 1.0
        assert config.memory_size > 0

    def test_immutabilite(self):
        """La Config est frozen : toute modification doit lever une exception."""
        config = Config()
        with pytest.raises((AttributeError, TypeError)):
            config.model = "autre_modele"  # type: ignore[misc]
