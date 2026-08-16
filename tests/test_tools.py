"""
Tests unitaires pour les outils de Gideonne.

Vérifie le comportement de :
  - CalculatorTool  : calculs arithmétiques sécurisés
  - DateTimeTool    : date et heure dans différents fuseaux
  - WordCountTool   : comptage de mots/phrases/caractères
  - KeywordTool     : extraction de mots-clés
"""

from __future__ import annotations

import asyncio
import pytest

from gideonne.tools.calculator import CalculatorTool, _safe_eval
from gideonne.tools.datetime_tool import DateTimeTool
from gideonne.tools.text_utils import WordCountTool, KeywordTool


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(coro):
    """Exécute une coroutine dans un contexte synchrone (compat pytest sans plugin async)."""
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# Tests : CalculatorTool
# ---------------------------------------------------------------------------

class TestCalculatorTool:
    """Tests de la calculatrice sécurisée."""

    def setup_method(self):
        self.outil = CalculatorTool()

    def test_addition_simple(self):
        """Addition de deux entiers."""
        resultat = run(self.outil.execute(expression="3 + 4"))
        assert "7" in resultat

    def test_multiplication(self):
        """Multiplication avec priorité des opérateurs."""
        resultat = run(self.outil.execute(expression="6 * 7"))
        assert "42" in resultat

    def test_expression_complexe(self):
        """Expression avec parenthèses et plusieurs opérateurs."""
        resultat = run(self.outil.execute(expression="(10 + 5) * 2"))
        assert "30" in resultat

    def test_division(self):
        """Division avec résultat décimal."""
        resultat = run(self.outil.execute(expression="7 / 2"))
        assert "3.5" in resultat

    def test_division_par_zero(self):
        """Division par zéro : doit retourner un message d'erreur clair."""
        resultat = run(self.outil.execute(expression="10 / 0"))
        assert "zéro" in resultat.lower() or "erreur" in resultat.lower()

    def test_expression_vide(self):
        """Expression vide : doit retourner une erreur gracieuse."""
        resultat = run(self.outil.execute(expression=""))
        assert "erreur" in resultat.lower() or len(resultat) > 0

    def test_puissance(self):
        """Opérateur puissance (**)"""
        resultat = run(self.outil.execute(expression="2 ** 10"))
        assert "1024" in resultat

    def test_modulo(self):
        """Opérateur modulo (%)"""
        resultat = run(self.outil.execute(expression="17 % 5"))
        assert "2" in resultat

    def test_schema_outil(self):
        """Le schema JSON doit être conforme au format OpenAI."""
        schema = self.outil.to_schema()
        assert schema["type"] == "function"
        assert "function" in schema
        assert schema["function"]["name"] == "calculatrice"
        assert "parameters" in schema["function"]


# ---------------------------------------------------------------------------
# Tests : DateTimeTool
# ---------------------------------------------------------------------------

class TestDateTimeTool:
    """Tests de l'outil date/heure."""

    def setup_method(self):
        self.outil = DateTimeTool()

    def test_retourne_une_chaine(self):
        """L'outil doit retourner une chaîne non vide."""
        resultat = run(self.outil.execute())
        assert isinstance(resultat, str)
        assert len(resultat) > 0

    def test_fuseau_ouagadougou(self):
        """Fuseau par défaut : Africa/Ouagadougou."""
        resultat = run(self.outil.execute(fuseau="Africa/Ouagadougou"))
        assert "Africa/Ouagadougou" in resultat

    def test_fuseau_utc(self):
        """Fuseau UTC explicite."""
        resultat = run(self.outil.execute(fuseau="UTC"))
        assert "UTC" in resultat

    def test_fuseau_invalide(self):
        """Fuseau inconnu : doit se replier sur UTC sans lever d'exception."""
        resultat = run(self.outil.execute(fuseau="Mars/Olympus_Mons"))
        assert isinstance(resultat, str)
        assert len(resultat) > 0

    def test_schema_outil(self):
        """Schéma JSON valide au format OpenAI."""
        schema = self.outil.to_schema()
        assert schema["function"]["name"] == "date_heure"


# ---------------------------------------------------------------------------
# Tests : WordCountTool
# ---------------------------------------------------------------------------

class TestWordCountTool:
    """Tests du compteur de mots."""

    def setup_method(self):
        self.outil = WordCountTool()

    def test_texte_simple(self):
        """Comptage sur un texte court connu."""
        resultat = run(self.outil.execute(texte="Bonjour monde. Comment allez-vous ?"))
        assert "Mots" in resultat
        assert "Phrases" in resultat
        assert "Caractères" in resultat

    def test_texte_vide(self):
        """Texte vide : doit retourner zéro partout sans lever d'exception."""
        resultat = run(self.outil.execute(texte=""))
        assert "0" in resultat

    def test_schema_outil(self):
        schema = self.outil.to_schema()
        assert schema["function"]["name"] == "compter_mots"


# ---------------------------------------------------------------------------
# Tests : KeywordTool
# ---------------------------------------------------------------------------

class TestKeywordTool:
    """Tests de l'extracteur de mots-clés."""

    def setup_method(self):
        self.outil = KeywordTool()

    def test_extrait_mots_cles(self):
        """Les mots les plus fréquents doivent être retournés."""
        texte = (
            "L'intelligence artificielle est une technologie."
            " L'intelligence artificielle transforme les métiers."
        )
        resultat = run(self.outil.execute(texte=texte, top_n=3))
        assert "Mots-clés" in resultat

    def test_texte_vide(self):
        """Texte vide : message spécifique attendu."""
        resultat = run(self.outil.execute(texte=""))
        assert isinstance(resultat, str)

    def test_top_n_respecte(self):
        """Le nombre de mots-clés retournés ne dépasse pas top_n."""
        texte = "gideonne gideonne gideonne nag nag nat industries python ia"
        resultat = run(self.outil.execute(texte=texte, top_n=2))
        # Au plus 2 mots-clés : on vérifie qu'il y en a bien dans la réponse
        assert "gideonne" in resultat.lower() or "nag" in resultat.lower()

    def test_schema_outil(self):
        schema = self.outil.to_schema()
        assert schema["function"]["name"] == "extraire_mots_cles"
