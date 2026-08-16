"""
Module d'interface de Gideonne.

Propose deux modes d'accès à l'agent :
  - CLI  : interaction directe en ligne de commande (mode conversationnel)
  - API  : serveur HTTP REST léger via FastAPI (mode serveur)
"""

from gideonne.interface.cli import CLIInterface
from gideonne.interface.api import APIInterface

__all__ = ["CLIInterface", "APIInterface"]
