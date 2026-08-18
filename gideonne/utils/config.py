"""
Configuration centralisée de Gideonne.

Lit les variables d'environnement (ou le fichier .env) et expose
une dataclass immuable consommée par tous les modules du projet.

Variables d'environnement reconnues :
    MODEL_PROVIDER       — Moteur LLM : "ollama" (défaut) ou "openai"
    OLLAMA_BASE_URL      — URL de l'API Ollama (défaut : http://localhost:11434)
    OPENAI_API_KEY       — Clé API OpenAI (requis si MODEL_PROVIDER=openai)
    GIDEONNE_BASE_URL    — URL de base OpenAI (si MODEL_PROVIDER=openai)
    GIDEONNE_MODEL       — Identifiant du modèle (défaut : llama3)
    GIDEONNE_MAX_TOKENS  — Tokens max par réponse (défaut : 2048)
    GIDEONNE_TEMPERATURE — Créativité du modèle (défaut : 0.7)
    GIDEONNE_MEMORY_SIZE — Tours en mémoire (défaut : 20)
    GIDEONNE_STORAGE_DIR — Répertoire de stockage (défaut : data)
    GIDEONNE_LOG_LEVEL   — Niveau de log (défaut : INFO)

Utilisation :
    config = Config.from_env()
    print(config.model_provider)  # "ollama"
    print(config.model)           # "llama3"
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# Chargement optionnel de .env si python-dotenv est disponible
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass  # python-dotenv non installé : les variables doivent être définies manuellement


@dataclass(frozen=True)
class Config:
    """
    Paramètres de configuration de Gideonne.

    Tous les champs ont une valeur par défaut orientée usage local
    (Ollama / llama3) afin que le projet démarre sans clé API externe.
    """

    # ------------------------------------------------------------------
    # Choix du moteur LLM
    # ------------------------------------------------------------------

    # Fournisseur de modèle actif : "ollama" ou "openai"
    model_provider: str = "ollama"

    # ------------------------------------------------------------------
    # Paramètres Ollama (utilisés si model_provider == "ollama")
    # ------------------------------------------------------------------

    # URL de base de l'API Ollama locale
    ollama_base_url: str = "http://localhost:11434"

    # ------------------------------------------------------------------
    # Paramètres OpenAI / compatibles (utilisés si model_provider == "openai")
    # ------------------------------------------------------------------

    # Clé API OpenAI (vide par défaut pour ne pas bloquer le démarrage local)
    openai_api_key: str = ""

    # URL de base de l'API OpenAI (ou fournisseur compatible)
    openai_base_url: str = "https://api.openai.com/v1"

    # ------------------------------------------------------------------
    # Paramètres communs
    # ------------------------------------------------------------------

    # Identifiant du modèle à utiliser
    model: str = "llama3"

    # Nombre maximum de tokens générés par réponse
    max_tokens: int = 2048

    # Paramètre de créativité (0 = déterministe, 1 = créatif)
    temperature: float = 0.7

    # Nombre de tours de conversation conservés en mémoire
    memory_size: int = 20

    # Répertoire de stockage des données persistantes
    storage_dir: str = "data"

    # Niveau de log (DEBUG, INFO, WARNING, ERROR)
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Config":
        """
        Crée une Config en lisant les variables d'environnement.

        La variable MODEL_PROVIDER détermine quel moteur est utilisé.
        En l'absence de toute configuration, Ollama avec llama3 est le défaut.

        Returns:
            Une instance de Config peuplée depuis l'environnement.
        """
        return cls(
            # Choix du moteur : ollama par défaut
            model_provider=os.getenv("MODEL_PROVIDER", "ollama").lower().strip(),

            # Ollama
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),

            # OpenAI (optionnel)
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_base_url=os.getenv("GIDEONNE_BASE_URL", "https://api.openai.com/v1"),

            # Paramètres communs
            model=os.getenv("GIDEONNE_MODEL", "llama3"),
            max_tokens=int(os.getenv("GIDEONNE_MAX_TOKENS", "2048")),
            temperature=float(os.getenv("GIDEONNE_TEMPERATURE", "0.7")),
            memory_size=int(os.getenv("GIDEONNE_MEMORY_SIZE", "20")),
            storage_dir=os.getenv("GIDEONNE_STORAGE_DIR", "data"),
            log_level=os.getenv("GIDEONNE_LOG_LEVEL", "INFO"),
        )
