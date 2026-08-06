"""
Module models : abstraction des modeles LLM.

Ajouter un nouveau modele = creer une classe qui herite de BaseModel
et implementer les methodes abstraites.
"""

from gideonne.models.base import BaseModel
from gideonne.models.openai_model import OpenAIModel

__all__ = ["BaseModel", "OpenAIModel"]
