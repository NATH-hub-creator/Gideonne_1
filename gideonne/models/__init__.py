"""
Module models : abstraction des modèles LLM.

Ajouter un nouveau modèle = créer une classe qui hérite de BaseModel
et implémenter les méthodes abstraites.

Modèles disponibles :
    - OllamaModel  : backend local via Ollama (défaut, aucune clé API requise)
    - OpenAIModel  : backend cloud via l'API OpenAI
"""

from gideonne.models.base import BaseModel
from gideonne.models.openai_model import OpenAIModel
from gideonne.models.ollama_model import OllamaModel

__all__ = ["BaseModel", "OpenAIModel", "OllamaModel"]
