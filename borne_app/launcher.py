# borne_app/launcher.py
from __future__ import annotations

import logging
import platform
import subprocess
from pathlib import Path

from . import config, database

logger = logging.getLogger(__name__)


def launch_game(game_data: dict) -> None:
    """Lance un jeu via RetroArch. Incrémente play_count en BDD si le run réussit."""
    logger.debug("Données reçues : %s", game_data)

    retroarch_cmd: str | None = None
    core_path: str | None = None
    rom_path: str | None = None
    success = False

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
        success = True

    except KeyError as e:
        logger.error(
            "Clé %s manquante dans game_data — fournit 'platform' et 'rom_path'.", e
        )
    except subprocess.CalledProcessError as e:
        logger.warning("RetroArch a quitté avec un code non-zéro : %s", e)
    except Exception as e:
        logger.error("Échec du lancement : %s", e)
        logger.error("Vérifie : retroarch=%r | core=%r | rom=%r",
                     retroarch_cmd, core_path, rom_path)

    if success:
        game_id = game_data.get("id")
        if isinstance(game_id, int):
            try:
                database.increment_play_count(game_id)
                logger.info("play_count incrémenté pour game_id=%d", game_id)
            except Exception as e:
                logger.warning("Échec incrément play_count (game_id=%d) : %s", game_id, e)
        else:
            logger.debug("Pas d'id dans game_data ; play_count non incrémenté.")

    logger.info("RetroArch fermé — retour au frontend.")
