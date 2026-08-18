"""
Backend Ollama pour Gideonne.

Utilise l'API REST native d'Ollama (http://localhost:11434) via httpx.
Pas besoin de clé API : Ollama tourne en local et est gratuit.

Pré-requis :
    - Ollama installé et en cours d'exécution : https://ollama.com
    - Le modèle souhaité téléchargé : `ollama pull llama3`
    - httpx installé : `pip install httpx`

Utilisation :
    config = Config.from_env()          # MODEL_PROVIDER=ollama dans .env
    model = OllamaModel(config)
    texte, _ = await model.generate(messages)
"""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from gideonne.models.base import BaseModel
from gideonne.utils.config import Config

logger = logging.getLogger(__name__)

# Endpoint de l'API chat d'Ollama
_OLLAMA_CHAT_PATH = "/api/chat"


class OllamaModel(BaseModel):
    """
    Backend LLM qui s'appuie sur l'API locale d'Ollama.

    Ollama expose une API REST minimaliste : POST /api/chat
    avec un corps JSON similaire au format OpenAI, ce qui facilite
    la migration depuis OpenAIModel.

    Args:
        config: Configuration du projet (ollama_base_url, model).
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        # URL de base, ex. : http://localhost:11434
        self._base_url = config.ollama_base_url.rstrip("/")
        # Nom du modèle Ollama, ex. : llama3, mistral, phi3
        self._model = config.model
        logger.info(
            "OllamaModel initialisé | base_url=%s | modèle=%s",
            self._base_url,
            self._model,
        )

    async def generate(
        self,
        messages: list[dict],
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> tuple[str, list[dict]]:
        """
        Envoie une requête au serveur Ollama local et retourne la réponse.

        L'API Ollama /api/chat accepte le même format de messages qu'OpenAI
        (liste de dicts {role, content}), ce qui simplifie la compatibilité.

        Args:
            messages: Historique + message courant au format {role, content}.
            max_tokens: Ignoré côté Ollama (contrôlé par num_predict dans les options).
            temperature: Paramètre de créativité transmis dans options.temperature.

        Returns:
            Tuple (texte_reponse, liste_tool_calls).
            Ollama ne supporte pas nativement les tool_calls : retourne toujours [].

        Raises:
            httpx.HTTPError: Si Ollama n'est pas joignable ou retourne une erreur HTTP.
            ValueError: Si la réponse JSON est malformée.
        """
        url = self._base_url + _OLLAMA_CHAT_PATH

        # Corps de la requête Ollama
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "stream": False,  # Réponse complète en une seule fois
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        logger.debug("Requête Ollama | url=%s | modèle=%s | messages=%d", url, self._model, len(messages))

        # Timeout généreux : les modèles locaux peuvent être lents au premier appel
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

        data: dict = response.json()

        # Structure de réponse Ollama : { "message": { "role": "assistant", "content": "..." }, ... }
        message = data.get("message", {})
        texte = message.get("content", "").strip()

        logger.debug(
            "Réponse Ollama reçue | done=%s | tokens_eval=%s",
            data.get("done"),
            data.get("eval_count"),
        )

        # Ollama ne génère pas de tool_calls natifs : liste vide pour compatibilité
        return texte, []
