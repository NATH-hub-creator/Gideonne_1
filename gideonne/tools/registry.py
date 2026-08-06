"""
Registre des outils disponibles pour Gideonne.

Permet d'enregistrer, de lister et d'executer dynamiquement les outils.
L'agent interroge ce registre pour construire la liste des outils a passer au LLM.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from gideonne.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registre central des outils de l'agent.

    Usage:
        registry = ToolRegistry()
        registry.register(MonOutil())
        schemas = registry.get_tool_schemas()
        result = await registry.execute("mon_outil", '{"param": "valeur"}')
    """

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """
        Enregistre un outil dans le registre.

        Args:
            tool: Instance de BaseTool a enregistrer.

        Raises:
            ValueError: Si un outil avec le meme nom est deja enregistre.
        """
        if tool.name in self._tools:
            raise ValueError(
                f"Un outil nomme '{tool.name}' est deja enregistre."
            )
        self._tools[tool.name] = tool
        logger.info("Outil enregistre : %s", tool.name)

    def unregister(self, name: str) -> None:
        """
        Retire un outil du registre.

        Args:
            name: Nom de l'outil a retirer.
        """
        if name in self._tools:
            del self._tools[name]
            logger.info("Outil retire : %s", name)

    def get_tool_schemas(self) -> list[dict]:
        """
        Retourne les schemas JSON de tous les outils enregistres.
        A passer directement dans le parametre `tools` de l'API OpenAI.

        Returns:
            Liste de schemas au format OpenAI.
        """
        return [tool.to_schema() for tool in self._tools.values()]

    async def execute(self, name: str, arguments_json: str) -> Any:
        """
        Execute un outil par son nom avec les arguments JSON fournis par le LLM.

        Args:
            name: Nom de l'outil.
            arguments_json: Arguments au format JSON (string).

        Returns:
            Le resultat de l'execution de l'outil.

        Raises:
            KeyError: Si l'outil n'est pas trouve dans le registre.
            json.JSONDecodeError: Si arguments_json n'est pas du JSON valide.
        """
        if name not in self._tools:
            logger.error("Outil inconnu demande par le LLM : %s", name)
            return f"Erreur : outil '{name}' non disponible."

        try:
            kwargs = json.loads(arguments_json)
        except json.JSONDecodeError as exc:
            logger.error("Arguments JSON invalides pour '%s' : %s", name, exc)
            return f"Erreur : arguments JSON invalides ({exc})."

        result = await self._tools[name].execute(**kwargs)
        logger.debug("Outil '%s' execute | resultat=%s", name, str(result)[:80])
        return result

    @property
    def tool_names(self) -> list[str]:
        """Liste des noms des outils enregistres."""
        return list(self._tools.keys())
