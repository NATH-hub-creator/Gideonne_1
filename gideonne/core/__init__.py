"""
Module core : moteur de l'agent Gideonne.
Contient l'agent principal, la gestion de la memoire et la construction des prompts.
"""

from gideonne.core.agent import GideonneAgent
from gideonne.core.memory import ConversationMemory
from gideonne.core.prompt import PromptBuilder

__all__ = ["GideonneAgent", "ConversationMemory", "PromptBuilder"]
