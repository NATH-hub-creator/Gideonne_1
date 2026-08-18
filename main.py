"""
Point d'entrée principal de Gideonne.

Orchestre l'initialisation de tous les modules et lance
l'interface choisie (CLI par défaut, API avec --mode api).

Usage :
    python main.py                     # Mode CLI interactif (Ollama par défaut)
    python main.py --mode cli          # Idem
    python main.py --mode api          # Serveur REST (nécessite FastAPI + uvicorn)
    python main.py --mode api --port 8080  # Serveur sur un port spécifique
    python main.py --session ma_session    # Reprendre une session existante

Variables d'environnement importantes :
    MODEL_PROVIDER       — "ollama" (défaut) ou "openai"
    OLLAMA_BASE_URL      — URL Ollama (défaut : http://localhost:11434)
    OPENAI_API_KEY       — Clé API OpenAI (requis uniquement si MODEL_PROVIDER=openai)
    GIDEONNE_MODEL       — Modèle à utiliser (défaut : llama3)
    GIDEONNE_LOG_LEVEL   — Niveau de log (défaut : INFO)

Pour démarrer rapidement avec Ollama :
    1. Installez Ollama : https://ollama.com
    2. Téléchargez le modèle : ollama pull llama3
    3. Lancez : python main.py
"""

from __future__ import annotations

import argparse
import logging
import sys


def _configurer_logging(niveau: str) -> None:
    """
    Configure le système de log de Python.

    Args:
        niveau: Niveau de log au format string (ex. : 'DEBUG', 'INFO').
    """
    format_log = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    logging.basicConfig(
        level=getattr(logging, niveau.upper(), logging.INFO),
        format=format_log,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _construire_agent():
    """
    Instancie et configure l'agent Gideonne avec tous ses modules.

    Le moteur LLM est sélectionné automatiquement selon MODEL_PROVIDER :
        - "ollama" (défaut) : OllamaModel — aucune clé API requise
        - "openai"          : OpenAIModel — nécessite OPENAI_API_KEY

    Returns:
        Tuple (agent, store) prêts à l'emploi.
    """
    from gideonne.utils.config import Config
    from gideonne.core.agent import GideonneAgent
    from gideonne.tools.registry import ToolRegistry
    from gideonne.tools.calculator import CalculatorTool
    from gideonne.tools.datetime_tool import DateTimeTool
    from gideonne.tools.text_utils import WordCountTool, KeywordTool
    from gideonne.storage.json_backend import JSONBackend
    from gideonne.storage.conversation_store import ConversationStore

    # 1. Configuration depuis les variables d'environnement
    config = Config.from_env()
    logger = logging.getLogger(__name__)
    logger.info(
        "Configuration chargée | provider=%s | modèle=%s",
        config.model_provider,
        config.model,
    )

    # 2. Registre des outils
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(DateTimeTool())
    registry.register(WordCountTool())
    registry.register(KeywordTool())
    logger.info("Outils enregistrés : %s", registry.tool_names)

    # 3. Sélection du backend LLM selon MODEL_PROVIDER
    model = _instancier_modele(config)
    logger.info("Backend LLM actif : %s", type(model).__name__)

    # 4. Agent principal
    agent = GideonneAgent(config=config, model=model, tool_registry=registry)

    # 5. Backend de stockage persistant
    backend = JSONBackend(storage_dir=config.storage_dir)

    return agent, backend


def _instancier_modele(config):
    """
    Choisit et instancie le backend LLM approprié selon config.model_provider.

    Args:
        config: Instance de Config déjà peuplée depuis l'environnement.

    Returns:
        Une instance de BaseModel (OllamaModel ou OpenAIModel).

    Raises:
        SystemExit: Si MODEL_PROVIDER est inconnu ou si OpenAI est sélectionné
                    sans clé API configurée.
    """
    logger = logging.getLogger(__name__)

    if config.model_provider == "ollama":
        from gideonne.models.ollama_model import OllamaModel
        logger.info(
            "Moteur Ollama sélectionné | url=%s | modèle=%s",
            config.ollama_base_url,
            config.model,
        )
        return OllamaModel(config)

    elif config.model_provider == "openai":
        from gideonne.models.openai_model import OpenAIModel

        if not config.openai_api_key:
            logger.error(
                "MODEL_PROVIDER=openai mais OPENAI_API_KEY n'est pas défini. "
                "Définissez OPENAI_API_KEY dans .env ou passez MODEL_PROVIDER=ollama."
            )
            sys.exit(1)

        logger.info(
            "Moteur OpenAI sélectionné | base_url=%s | modèle=%s",
            config.openai_base_url,
            config.model,
        )
        return OpenAIModel(config)

    else:
        logger.error(
            "MODEL_PROVIDER='%s' non reconnu. Valeurs valides : ollama, openai.",
            config.model_provider,
        )
        sys.exit(1)


def _lancer_cli(agent, backend, session_id: str) -> None:
    """
    Lance l'interface en ligne de commande.

    Args:
        agent: Instance de GideonneAgent.
        backend: Backend de stockage JSON.
        session_id: Identifiant de la session à utiliser.
    """
    from gideonne.storage.conversation_store import ConversationStore
    from gideonne.interface.cli import CLIInterface

    # Restauration de la session précédente si elle existe
    store = ConversationStore(backend=backend, session_id=session_id)
    tours_restaures = store.restaurer(agent.memory)

    logger = logging.getLogger(__name__)
    if tours_restaures > 0:
        logger.info(
            "Session '%s' restaurée : %d tours rechargés.",
            session_id, tours_restaures,
        )
    else:
        logger.info("Nouvelle session '%s' démarrée.", session_id)

    # Interface CLI
    cli = CLIInterface(agent=agent)

    try:
        cli.run()
    finally:
        # Sauvegarde automatique de la session à la fermeture
        store.persister(agent.memory)
        logger.info("Session '%s' sauvegardée.", session_id)


def _lancer_api(agent, port: int, host: str) -> None:
    """
    Lance le serveur HTTP REST via uvicorn.

    Args:
        agent: Instance de GideonneAgent.
        port: Port d'écoute du serveur.
        host: Interface réseau d'écoute.
    """
    try:
        import uvicorn
    except ImportError:
        logging.getLogger(__name__).error(
            "uvicorn n'est pas installé. Lancez : pip install uvicorn fastapi"
        )
        sys.exit(1)

    from gideonne.interface.api import build_app

    app = build_app(agent=agent)
    logger = logging.getLogger(__name__)
    logger.info("Serveur API démarré sur %s:%d", host, port)
    uvicorn.run(app, host=host, port=port)


def main() -> None:
    """
    Point d'entrée principal : parse les arguments et délègue à l'interface choisie.
    """
    parser = argparse.ArgumentParser(
        description="Gideonne — assistant IA local (Ollama/llama3 par défaut)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=["cli", "api"],
        default="cli",
        help="Interface à lancer : cli (défaut) ou api (serveur REST).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port du serveur API (défaut : 8000, mode api uniquement).",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Interface réseau du serveur API (défaut : 127.0.0.1).",
    )
    parser.add_argument(
        "--session",
        default="default",
        help="Identifiant de session (défaut : 'default').",
    )

    args = parser.parse_args()

    # Initialisation du logging avant tout
    from gideonne.utils.config import Config
    config_base = Config.from_env()
    _configurer_logging(config_base.log_level)

    # Construction de l'agent
    agent, backend = _construire_agent()

    # Lancement de l'interface choisie
    if args.mode == "api":
        _lancer_api(agent, port=args.port, host=args.host)
    else:
        _lancer_cli(agent, backend, session_id=args.session)


if __name__ == "__main__":
    main()
