# borne_app/game_scanner.py
"""
Charge la liste des jeux depuis la base SQLite (datas/arcadia.db).
Le nom de la fonction est conservé pour compat avec l'UI existante.
"""
from __future__ import annotations

import logging

from . import database

logger = logging.getLogger(__name__)


def load_games_data() -> list[dict]:
    """Retourne la liste des jeux sous forme de dicts (compatibles UI)."""
    games = database.list_games()
    logger.info("Chargement bibliothèque : %d jeux", len(games))
    return games
