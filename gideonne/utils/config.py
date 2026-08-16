"""
Configuration centralisée de Gideonne.

Lit les variables d'environnement (ou le fichier .env) et expose
une dataclass immuable consommée par tous les modules du projet.

Utilisation :
    config = Config.from_env()
    print(config.model)  # ex. : "gpt-4o-mini"
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
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

    Tous les champs ont une valeur par défaut raisonnable pour un usage local
    sans connexion internet permanente.
    """

    # Clé API OpenAI (ou clé du fournisseur compatible)
    openai_api_key: str = ""

    # URL de base de l'API (peut pointer vers Ollama, LMStudio, etc.)
    openai_base_url: str = "https://api.openai.com/v1"

    # Identifiant du modèle à utiliser
    model: str = "gpt-4o-mini"

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

        Les noms des variables sont en majuscules et préfixés de GIDEONNE_
        (ex. : GIDEONNE_MODEL, GIDEONNE_MAX_TOKENS).

        Returns:
            Une instance de Config peuplée depuis l'environnement.
        """
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_base_url=os.getenv(
                "GIDEONNE_BASE_URL", "https://api.openai.com/v1"
            ),
            model=os.getenv("GIDEONNE_MODEL", "gpt-4o-mini"),
            max_tokens=int(os.getenv("GIDEONNE_MAX_TOKENS", "2048")),
            temperature=float(os.getenv("GIDEONNE_TEMPERATURE", "0.7")),
            memory_size=int(os.getenv("GIDEONNE_MEMORY_SIZE", "20")),
            storage_dir=os.getenv("GIDEONNE_STORAGE_DIR", "data"),
            log_level=os.getenv("GIDEONNE_LOG_LEVEL", "INFO"),
        )
