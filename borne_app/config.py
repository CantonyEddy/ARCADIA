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


# --- User settings (datas/user_settings.json) ---

USER_SETTINGS_PATH = Path(__file__).resolve().parent.parent / "datas" / "user_settings.json"

DEFAULT_USER_SETTINGS: dict = {
    "volume": 80,
    "music_enabled": False,
    "accent_color": [255, 107, 0],
    "show_fps": False,
}


def load_user_settings() -> dict:
    """Charge les préférences utilisateur ; retourne les défauts si fichier absent/corrompu."""
    if not USER_SETTINGS_PATH.exists():
        return dict(DEFAULT_USER_SETTINGS)
    try:
        with open(USER_SETTINGS_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return dict(DEFAULT_USER_SETTINGS)
    merged = dict(DEFAULT_USER_SETTINGS)
    if isinstance(data, dict):
        merged.update(data)
    return merged


def save_user_settings(settings: dict) -> None:
    """Écrit les préférences utilisateur de façon atomique (tmp + rename)."""
    USER_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = USER_SETTINGS_PATH.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
    tmp.replace(USER_SETTINGS_PATH)
