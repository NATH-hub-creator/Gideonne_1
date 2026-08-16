"""
Outils de traitement de texte pour Gideonne.

Fournit des fonctions utilitaires opérant sur le texte :
compter les mots, résumer grossièrement, extraire les mots-clés, etc.
Ces fonctions fonctionnent entièrement hors-ligne.
"""

from __future__ import annotations

import logging
import re
import string
from collections import Counter
from typing import Any

from gideonne.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

# Mots vides français courants (stop-words légers, sans dépendance externe)
_STOP_WORDS_FR = frozenset({
    "le", "la", "les", "de", "du", "des", "un", "une", "et", "en", "au", "aux",
    "ce", "se", "sa", "son", "ses", "je", "tu", "il", "elle", "nous", "vous",
    "ils", "elles", "que", "qui", "quoi", "dont", "où", "par", "pour", "sur",
    "sous", "avec", "dans", "à", "est", "sont", "a", "ont", "pas", "plus",
    "ne", "ni", "ou", "mais", "car", "donc", "or", "comme", "si", "très",
})


def _tokenize(text: str) -> list[str]:
    """Découpe un texte en tokens alphanumériques en minuscules."""
    return re.findall(r"[\w']+", text.lower())


class WordCountTool(BaseTool):
    """Compte les mots, phrases et caractères d'un texte."""

    name = "compter_mots"
    description = (
        "Analyse un texte et retourne le nombre de mots, de phrases et de caractères."
    )
    parameters = {
        "type": "object",
        "properties": {
            "texte": {
                "type": "string",
                "description": "Le texte à analyser.",
            }
        },
        "required": ["texte"],
    }

    async def execute(self, **kwargs: Any) -> str:
        texte: str = kwargs.get("texte", "")
        mots = _tokenize(texte)
        phrases = re.split(r"[.!?]+", texte)
        phrases = [p.strip() for p in phrases if p.strip()]
        caracteres = len(texte)

        logger.debug(
            "Comptage : %d mots, %d phrases, %d caractères",
            len(mots), len(phrases), caracteres,
        )
        return (
            f"Mots : {len(mots)} | "
            f"Phrases : {len(phrases)} | "
            f"Caractères : {caracteres}"
        )


class KeywordTool(BaseTool):
    """Extrait les mots-clés les plus fréquents d'un texte."""

    name = "extraire_mots_cles"
    description = (
        "Extrait les N mots-clés les plus fréquents d'un texte, "
        "en ignorant les mots vides courants du français."
    )
    parameters = {
        "type": "object",
        "properties": {
            "texte": {
                "type": "string",
                "description": "Le texte depuis lequel extraire les mots-clés.",
            },
            "top_n": {
                "type": "integer",
                "description": "Nombre de mots-clés à retourner (défaut : 5).",
                "default": 5,
            },
        },
        "required": ["texte"],
    }

    async def execute(self, **kwargs: Any) -> str:
        texte: str = kwargs.get("texte", "")
        top_n: int = int(kwargs.get("top_n", 5))

        tokens = _tokenize(texte)
        # Filtrage des mots vides et des tokens trop courts
        tokens_filtres = [
            t for t in tokens
            if t not in _STOP_WORDS_FR and len(t) > 2
        ]

        if not tokens_filtres:
            return "Aucun mot-clé significatif trouvé."

        compteur = Counter(tokens_filtres)
        mots_cles = compteur.most_common(top_n)

        lignes = [f"{mot} ({count}x)" for mot, count in mots_cles]
        return "Mots-clés : " + ", ".join(lignes)
