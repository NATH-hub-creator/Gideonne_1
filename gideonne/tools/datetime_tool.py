"""
Outil date et heure pour Gideonne.

Fournit la date et l'heure courantes au modèle LLM,
utile quand l'agent fonctionne hors-ligne ou sans accès au web.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from gideonne.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

# Fuseau horaire par défaut pour NAG NAT Industries (Koudougou, Burkina Faso)
DEFAULT_TIMEZONE = "Africa/Ouagadougou"


class DateTimeTool(BaseTool):
    """
    Retourne la date et l'heure courantes dans le fuseau horaire demandé.

    Le LLM peut préciser un fuseau IANA (ex. : 'Europe/Paris', 'UTC').
    Sans précision, le fuseau de Koudougou est utilisé.
    """

    name = "date_heure"
    description = (
        "Retourne la date et l'heure actuelles. "
        "Le paramètre 'fuseau' accepte n'importe quel identifiant de fuseau IANA "
        "(ex. : 'UTC', 'Europe/Paris', 'Africa/Ouagadougou'). "
        "Par défaut : 'Africa/Ouagadougou'."
    )
    parameters = {
        "type": "object",
        "properties": {
            "fuseau": {
                "type": "string",
                "description": "Identifiant IANA du fuseau horaire (optionnel).",
                "default": DEFAULT_TIMEZONE,
            }
        },
        "required": [],
    }

    async def execute(self, **kwargs: Any) -> str:
        """
        Retourne la date/heure formatée dans le fuseau demandé.

        Args:
            fuseau: Identifiant IANA du fuseau (optionnel).

        Returns:
            Une chaîne lisible avec la date et l'heure complètes.
        """
        tz_name: str = kwargs.get("fuseau", DEFAULT_TIMEZONE)
        logger.debug("Heure demandée pour le fuseau : %s", tz_name)

        try:
            tz = ZoneInfo(tz_name)
        except ZoneInfoNotFoundError:
            logger.warning("Fuseau inconnu '%s', repli sur UTC.", tz_name)
            tz = timezone.utc
            tz_name = "UTC"

        now = datetime.now(tz=tz)
        # Format lisible et non ambigu
        formatted = now.strftime("%A %d %B %Y, %H:%M:%S")
        return f"Date et heure ({tz_name}) : {formatted}"
