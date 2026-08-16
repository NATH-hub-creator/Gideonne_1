"""
Interface en ligne de commande (CLI) pour Gideonne.

Lance une boucle conversationnelle interactive dans le terminal.
L'utilisateur tape son message, Gideonne répond, et ainsi de suite.
Commandes spéciales :
  /quitter  — termine la session
  /effacer  — efface l'historique de la conversation en cours
  /aide     — affiche les commandes disponibles
"""

from __future__ import annotations

import asyncio
import logging
import sys
from typing import Optional

from gideonne.core.agent import GideonneAgent

logger = logging.getLogger(__name__)

# Largeur de la bannière d'accueil
_BANNER_WIDTH = 60


class CLIInterface:
    """
    Interface conversationnelle en mode terminal.

    Args:
        agent: Instance de GideonneAgent à piloter.
        invite: Texte affiché avant chaque saisie de l'utilisateur.
    """

    def __init__(
        self,
        agent: GideonneAgent,
        invite: str = "Vous > ",
    ) -> None:
        self.agent = agent
        self.invite = invite

    # ------------------------------------------------------------------
    # Points d'entrée publics
    # ------------------------------------------------------------------

    def run(self) -> None:
        """
        Lance la boucle CLI de manière synchrone.
        Utilise asyncio.run() pour exécuter la boucle asynchrone.
        """
        try:
            asyncio.run(self._boucle())
        except KeyboardInterrupt:
            # Ctrl+C : sortie propre sans traceback
            print("\nSession interrompue. À bientôt !", flush=True)
            sys.exit(0)

    async def run_async(self) -> None:
        """Lance la boucle CLI de manière asynchrone (pour intégration)."""
        await self._boucle()

    # ------------------------------------------------------------------
    # Logique interne
    # ------------------------------------------------------------------

    def _afficher_banniere(self) -> None:
        """Affiche la bannière d'accueil de Gideonne dans le terminal."""
        ligne = "=" * _BANNER_WIDTH
        print(ligne)
        print(" GIDEONNE — IA conversationnelle locale ".center(_BANNER_WIDTH))
        print(" NAG NAT Industries | Koudougou, Burkina Faso ".center(_BANNER_WIDTH))
        print(ligne)
        print("Tapez /aide pour la liste des commandes, /quitter pour sortir.")
        print()

    def _afficher_aide(self) -> None:
        """Affiche les commandes spéciales disponibles."""
        print(
            "\nCommandes disponibles :\n"
            "  /quitter  — Terminer la session\n"
            "  /effacer  — Effacer l'historique de la conversation\n"
            "  /aide     — Afficher ce message\n"
        )

    async def _boucle(self) -> None:
        """Boucle principale : lire → traiter → afficher, en continu."""
        self._afficher_banniere()

        while True:
            try:
                # Lecture du message (lecture bloquante dans un thread séparé)
                message = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: input(self.invite)
                )
            except EOFError:
                # Fin de flux (pipe ou fichier redirigé)
                print("\nFin de l'entrée. Session terminée.")
                break

            message = message.strip()

            # Commandes spéciales
            if not message:
                continue
            if message == "/quitter":
                print("À bientôt !")
                break
            if message == "/effacer":
                self.agent.memory.clear()
                print("Historique effacé.")
                continue
            if message == "/aide":
                self._afficher_aide()
                continue

            # Traitement par l'agent
            try:
                reponse = await self.agent.chat(message)
                print(f"\nGideonne > {reponse}\n")
            except Exception as exc:
                logger.error("Erreur lors du traitement : %s", exc)
                print(f"[Erreur] Une erreur s'est produite : {exc}\n")
