"""
Interface API REST pour Gideonne.

Serveur HTTP léger basé sur FastAPI.
Expose les endpoints suivants :
  POST /chat    — envoyer un message à Gideonne et obtenir une réponse
  POST /reset   — réinitialiser l'historique de la conversation
  GET  /status  — vérifier que le serveur est opérationnel

Démarrage :
    python -m uvicorn gideonne.interface.api:create_app --factory --reload

OU via main.py avec le flag --mode api.
"""

from __future__ import annotations

import logging
from typing import Optional

# Importation conditionnelle : FastAPI n'est pas obligatoire si on utilise uniquement la CLI
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel as PydanticModel
    _FASTAPI_DISPONIBLE = True
except ImportError:
    _FASTAPI_DISPONIBLE = False

from gideonne.core.agent import GideonneAgent

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Schémas de requête / réponse (Pydantic)
# ------------------------------------------------------------------

if _FASTAPI_DISPONIBLE:
    class ChatRequest(PydanticModel):
        """Corps de la requête POST /chat."""
        message: str
        # Identifiant de session optionnel (réservé pour usage futur multi-utilisateur)
        session_id: Optional[str] = None

    class ChatResponse(PydanticModel):
        """Corps de la réponse POST /chat."""
        reponse: str
        # Nombre de tours actuellement en mémoire
        tours_en_memoire: int

    class StatusResponse(PydanticModel):
        """Corps de la réponse GET /status."""
        statut: str
        version: str
        modele: str


# ------------------------------------------------------------------
# Classe principale
# ------------------------------------------------------------------

class APIInterface:
    """
    Interface HTTP REST pour Gideonne.

    Args:
        agent: Instance de GideonneAgent à exposer.
        prefix: Préfixe d'URL pour toutes les routes (ex. : "/v1").
    """

    def __init__(
        self,
        agent: GideonneAgent,
        prefix: str = "",
    ) -> None:
        if not _FASTAPI_DISPONIBLE:
            raise RuntimeError(
                "FastAPI n'est pas installé. Lancez : pip install fastapi uvicorn"
            )
        self.agent = agent
        self.prefix = prefix
        self.app = self._creer_application()

    def _creer_application(self) -> "FastAPI":
        """
        Crée et configure l'application FastAPI.

        Returns:
            Application FastAPI prête à être servie.
        """
        app = FastAPI(
            title="Gideonne API",
            description="API REST pour l'assistant IA Gideonne — NAG NAT Industries",
            version="1.0.0",
        )

        # Récupération de la version depuis le package principal
        try:
            import gideonne
            _version = gideonne.__version__
        except Exception:
            _version = "inconnue"

        # ---- Endpoint : vérification de l'état du serveur ----
        @app.get(self.prefix + "/status", response_model=StatusResponse)
        async def status() -> StatusResponse:
            """Vérifie que le serveur Gideonne est opérationnel."""
            return StatusResponse(
                statut="ok",
                version=_version,
                modele=self.agent.config.model,
            )

        # ---- Endpoint : conversation ----
        @app.post(self.prefix + "/chat", response_model=ChatResponse)
        async def chat(request: ChatRequest) -> ChatResponse:
            """
            Traite un message et retourne la réponse de Gideonne.

            Args:
                request: Corps JSON contenant le message de l'utilisateur.

            Returns:
                La réponse de l'agent et le nombre de tours en mémoire.
            """
            if not request.message.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Le message ne peut pas être vide.",
                )

            logger.info("POST /chat | message=%s", request.message[:60])

            try:
                reponse = await self.agent.chat(request.message)
            except Exception as exc:
                logger.error("Erreur lors du traitement : %s", exc)
                raise HTTPException(
                    status_code=500,
                    detail=f"Erreur interne : {exc}",
                )

            return ChatResponse(
                reponse=reponse,
                tours_en_memoire=self.agent.memory.turn_count,
            )

        # ---- Endpoint : réinitialisation de la mémoire ----
        @app.post(self.prefix + "/reset")
        async def reset() -> dict:
            """Efface l'historique de la conversation en cours."""
            self.agent.memory.clear()
            logger.info("POST /reset — mémoire effacée")
            return {"message": "Historique effacé avec succès."}

        return app


def create_app() -> "FastAPI":
    """
    Factory function pour uvicorn (--factory).

    Charge la configuration depuis l'environnement et instancie l'application.

    Returns:
        Application FastAPI prête à démarrer.
    """
    from gideonne.utils.config import Config
    from gideonne.models.openai_model import OpenAIModel
    from gideonne.tools.registry import ToolRegistry
    from gideonne.tools.calculator import CalculatorTool
    from gideonne.tools.datetime_tool import DateTimeTool
    from gideonne.tools.text_utils import WordCountTool, KeywordTool

    config = Config.from_env()
    model = OpenAIModel(config)

    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(DateTimeTool())
    registry.register(WordCountTool())
    registry.register(KeywordTool())

    agent = GideonneAgent(config=config, model=model, tool_registry=registry)
    interface = APIInterface(agent=agent)
    return interface.app
