# borne_app/launcher.py
from __future__ import annotations

import logging
import platform
import subprocess
from pathlib import Path

from . import config

logger = logging.getLogger(__name__)


def launch_game(game_data: dict) -> None:
    """Lance un jeu en utilisant les infos de game_data."""
    logger.debug("Données reçues : %s", game_data)

    retroarch_cmd: str | None = None
    core_path: str | None = None
    rom_path: str | None = None

    try:
        retroarch_cmd = config.get_path("retroarch_exe")
        cores_dir = config.get_path("cores_dir")

        core_name = config.get_core_map(game_data["platform"])
        core_ext = ".dll" if platform.system() == "Windows" else ".so"
        core_path = str(Path(cores_dir) / f"{core_name}{core_ext}")

        rom_path = game_data["rom_path"]

        logger.debug("RetroArch=%s | core=%s | rom=%s", retroarch_cmd, core_path, rom_path)

        commande = [retroarch_cmd, "-L", core_path, rom_path]
        logger.info("Lancement : %s", " ".join(commande))

        subprocess.run(commande, check=True)

    except KeyError as e:
        logger.error(
            "Clé %s manquante dans game_data — game_scanner doit fournir 'platform' et 'rom_path'.",
            e,
        )
    except Exception as e:
        logger.error("Échec du lancement : %s", e)
        logger.error("Vérifie : retroarch=%r | core=%r | rom=%r", retroarch_cmd, core_path, rom_path)

    logger.info("RetroArch fermé — retour au frontend.")
