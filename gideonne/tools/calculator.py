"""
Outil calculatrice pour Gideonne.

Permet au modèle LLM d'effectuer des calculs arithmétiques
de manière sûre, sans recourir à eval().
"""

from __future__ import annotations

import ast
import logging
import operator
from typing import Any

from gideonne.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

# Opérateurs arithmétiques autorisés (liste blanche de sécurité)
_SAFE_OPERATORS: dict[type, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,  # nombre négatif : -5
    ast.UAdd: operator.pos,
}


def _safe_eval(node: ast.AST) -> float:
    """
    Évalue récursivement un nœud AST en n'autorisant que l'arithmétique.

    Args:
        node: Nœud de l'arbre syntaxique abstrait.

    Returns:
        Le résultat numérique du sous-arbre.

    Raises:
        ValueError: Si une opération non autorisée est détectée.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPERATORS:
            raise ValueError(f"Opérateur non autorisé : {op_type.__name__}")
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return _SAFE_OPERATORS[op_type](left, right)

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPERATORS:
            raise ValueError(f"Opérateur unaire non autorisé : {op_type.__name__}")
        return _SAFE_OPERATORS[op_type](_safe_eval(node.operand))

    raise ValueError(f"Expression non supportée : {type(node).__name__}")


class CalculatorTool(BaseTool):
    """
    Outil arithmétique sécurisé.

    Le LLM peut demander un calcul en fournissant une expression textuelle
    (ex. : "(42 * 7) + 3.14"). Le résultat est retourné sous forme de chaîne.
    """

    name = "calculatrice"
    description = (
        "Effectue un calcul arithmétique à partir d'une expression mathématique. "
        "Supporte +, -, *, /, **, % et //. "
        "Exemple d'expression : '(10 + 5) * 2 / 3'"
    )
    parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "L'expression arithmétique à calculer (ex. : '3.14 * 5 ** 2').",
            }
        },
        "required": ["expression"],
    }

    async def execute(self, **kwargs: Any) -> str:
        """
        Évalue l'expression et retourne le résultat.

        Args:
            expression: L'expression arithmétique fournie par le LLM.

        Returns:
            Le résultat sous forme de chaîne, ou un message d'erreur clair.
        """
        expression: str = kwargs.get("expression", "").strip()
        logger.debug("Calcul demandé : %s", expression)

        try:
            # Analyse syntaxique sans exécution de code arbitraire
            tree = ast.parse(expression, mode="eval")
            result = _safe_eval(tree.body)

            # Affichage propre : entier si pas de décimale significative
            if result == int(result):
                formatted = str(int(result))
            else:
                formatted = f"{result:.6g}"

            logger.debug("Résultat : %s", formatted)
            return f"{expression} = {formatted}"

        except ZeroDivisionError:
            return "Erreur : division par zéro."
        except (ValueError, TypeError, SyntaxError) as exc:
            logger.warning("Erreur de calcul pour '%s' : %s", expression, exc)
            return f"Erreur : expression invalide ({exc})."
