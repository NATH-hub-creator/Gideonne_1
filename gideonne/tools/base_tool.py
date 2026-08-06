"""
Classe de base pour tous les outils de Gideonne.

Chaque outil doit :
  - definir son schema JSON (nom, description, parametres)
  - implementer la methode `execute` qui effectue l'action concrete
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """
    Interface commune pour tous les outils de Gideonne.

    Exemple d'implementation minimale :

        class EchoTool(BaseTool):
            name = "echo"
            description = "Repete le texte fourni."
            parameters = {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Texte a repeter"}
                },
                "required": ["text"]
            }

            async def execute(self, **kwargs) -> str:
                return kwargs.get("text", "")
    """

    # A definir dans chaque sous-classe
    name: str = ""
    description: str = ""
    parameters: dict = {}

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """
        Execute l'action de l'outil.

        Args:
            **kwargs: Parametres passes par le modele LLM.

        Returns:
            Le resultat de l'action (sera converti en string pour l'API).
        """
        ...

    def to_schema(self) -> dict:
        """
        Retourne le schema JSON-Schema de l'outil, au format attendu par l'API OpenAI.

        Returns:
            Dict conforme au format `tools` de l'API OpenAI.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
