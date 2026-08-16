"""
Point d'entrée principal de Gideonne.

Orchestre l'initialisation de tous les modules et lance
l'interface choisie (CLI par défaut, API avec --mode api).

Usage :
    python main.py                     # Mode CLI interactif
    python main.py --mode cli          # Idem
    python main.py --mode api          # Serveur REST (nécessite FastAPI + uvicorn)
    python main.py --mode api --port 8080  # Serveur sur un port spécifique
    python main.py --session ma_session    # Reprendre une session existante

Variables d'environnement importantes :
    OPENAI_API_KEY     — Clé API OpenAI (ou fournisseur compatible)
    GIDEONNE_MODEL     — Modèle à utiliser (défaut : gpt-4o-mini)
    GIDEONNE_BASE_URL  — URL de base de l'API (pour Ollama, LMStudio, etc.)
    GIDEONNE_LOG_LEVEL — Niveau de log (défaut : INFO)
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

    Returns:
        Tuple (agent, store) prêts à l'emploi.
    """
    from gideonne.utils.config import Config
    from gideonne.models.openai_model import OpenAIModel
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
    logger.info("Configuration chargée | modèle=%s", config.model)

    # 2. Registre des outils
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(DateTimeTool())
    registry.register(WordCountTool())
    registry.register(KeywordTool())
    logger.info("Outils enregistrés : %s", registry.tool_names)

    # 3. Backend LLM
    model = OpenAIModel(config)

    # 4. Agent principal
    agent = GideonneAgent(config=config, model=model, tool_registry=registry)

    # 5. Backend de stockage persistant
    backend = JSONBackend(storage_dir=config.storage_dir)

    return agent, backend


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
        port: Port d'écoute.
        host: Adresse d'écoute.
    """
    try:
        import uvicorn
    except ImportError:
        print(
            "[ERREUR] uvicorn n'est pas installé. "
            "Lancez : pip install fastapi uvicorn",
            file=sys.stderr,
        )
        sys.exit(1)

    from gideonne.interface.api import APIInterface

    interface = APIInterface(agent=agent)
    logger = logging.getLogger(__name__)
    logger.info("Démarrage du serveur Gideonne sur %s:%d", host, port)

    uvicorn.run(interface.app, host=host, port=port)


def main() -> None:
    """
    Point d'entrée principal : analyse les arguments CLI et lance le mode demandé.
    """
    # --- Analyse des arguments ---
    parser = argparse.ArgumentParser(
        description="Gideonne — IA conversationnelle locale pour NAG NAT Industries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=["cli", "api"],
        default="cli",
        help="Mode de lancement : 'cli' (terminal) ou 'api' (serveur REST). Défaut : cli.",
    )
    parser.add_argument(
        "--session",
        default="default",
        help="Identifiant de session à reprendre ou créer. Défaut : 'default'.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Adresse d'écoute du serveur API. Défaut : 127.0.0.1.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port d'écoute du serveur API. Défaut : 8000.",
    )
    parser.add_argument(
        "--log-level",
        default=None,
        help="Niveau de log (DEBUG, INFO, WARNING, ERROR). Prioritaire sur GIDEONNE_LOG_LEVEL.",
    )
    args = parser.parse_args()

    # --- Initialisation du logging ---
    # On charge temporairement la config pour récupérer le niveau de log par défaut
    from gideonne.utils.config import Config
    config_temp = Config.from_env()
    niveau_log = args.log_level or config_temp.log_level
    _configurer_logging(niveau_log)

    logger = logging.getLogger(__name__)
    logger.info("=== Démarrage de Gideonne ===")

    # --- Construction de l'agent ---
    agent, backend = _construire_agent()

    # --- Lancement du mode demandé ---
    if args.mode == "api":
        _lancer_api(agent=agent, port=args.port, host=args.host)
    else:
        _lancer_cli(agent=agent, backend=backend, session_id=args.session)


if __name__ == "__main__":
    main()
