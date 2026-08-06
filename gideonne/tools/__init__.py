"""
Module tools : outils utilisables par l'agent Gideonne.

Pour ajouter un outil :
  1. Creer une classe qui herite de BaseTool dans ce package.
  2. L'enregistrer dans le ToolRegistry via registry.register(MonOutil()).
"""

from gideonne.tools.base_tool import BaseTool
from gideonne.tools.registry import ToolRegistry

__all__ = ["BaseTool", "ToolRegistry"]
