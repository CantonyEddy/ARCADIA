# borne_app/game_scanner.py
from __future__ import annotations

import logging
from pathlib import Path

from . import config

logger = logging.getLogger(__name__)

DATA_GAME_PATH = Path(__file__).resolve().parent.parent / "datas" / "data_game.json"


def load_games_data() -> list[dict]:
    """Charge les données de jeux depuis datas/data_game.json."""
    logger.info("Chargement des jeux depuis %s", DATA_GAME_PATH)
    try:
        games_data = config.load_json(DATA_GAME_PATH)
    except FileNotFoundError:
        logger.error("Fichier de jeux introuvable : %s", DATA_GAME_PATH)
        return []
    logger.info("%d jeux chargés", len(games_data))
    return games_data
