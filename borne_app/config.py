# borne_app/config.py
from __future__ import annotations

import configparser
import json
import platform
from pathlib import Path

CONFIG_FILE = Path(__file__).resolve().parent.parent / "config.ini"

config = configparser.ConfigParser()
_read = config.read(CONFIG_FILE, encoding="utf-8")
if not _read:
    raise FileNotFoundError(f"config.ini introuvable : {CONFIG_FILE}")

current_os = platform.system()
PATH_SECTION = "Paths_Windows" if current_os == "Windows" else "Paths_Linux"


def get_path(key: str) -> str:
    """Récupère un chemin depuis la section [Paths_...]"""
    return config.get(PATH_SECTION, key)


def load_json(file_path) -> dict | list:
    """Charge un fichier JSON et retourne les données."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_core_map(key: str) -> str:
    return config.get("CoreMap", key)


def get_all_core_keys() -> list[str]:
    """Retourne une liste de toutes les clés dans la section [CoreMap]."""
    return config.options("CoreMap")


def get_icon_path(key: str) -> str:
    """Récupère le chemin d'une icône depuis la section [icons]"""
    return config.get("icons", key)
