"""
Couche d'accès SQLite pour ARCADIA.

- Singleton de connexion (sqlite3) ouvert au boot via init()
- Schéma : tables `games` et `profiles`
- Migration automatique depuis datas/data_game.json si la table games est vide
- Toutes les fonctions publiques renvoient des dicts (compatibles UI existante).
"""
from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from . import config

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "datas"
DB_PATH = DATA_DIR / "arcadia.db"
LEGACY_JSON = DATA_DIR / "data_game.json"

_conn: Optional[sqlite3.Connection] = None


# ============================================================
# Init / shutdown
# ============================================================
def init() -> None:
    """Ouvre la connexion (idempotent), crée le schéma, migre depuis JSON si besoin.
    À appeler au démarrage de l'app, avant toute autre fonction du module."""
    global _conn
    if _conn is not None:
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    _conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    _conn.row_factory = sqlite3.Row
    _conn.execute("PRAGMA foreign_keys = ON")

    _init_schema(_conn)
    _migrate_from_json_if_needed(_conn)
    logger.info("Base SQLite prête (%s)", DB_PATH)


def close() -> None:
    """Ferme la connexion proprement (à appeler au shutdown)."""
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None


def _ensure() -> sqlite3.Connection:
    """Garantit qu'une connexion existe (init paresseux pour les tests)."""
    if _conn is None:
        init()
    assert _conn is not None
    return _conn


# ============================================================
# Schéma
# ============================================================
_SCHEMA_GAMES = """
CREATE TABLE IF NOT EXISTS games (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    platform    TEXT    NOT NULL,
    cover       TEXT,
    rom_path    TEXT    NOT NULL,
    resume      TEXT,
    is_favorite INTEGER NOT NULL DEFAULT 0,
    play_count  INTEGER NOT NULL DEFAULT 0
)
"""

_SCHEMA_PROFILES = """
CREATE TABLE IF NOT EXISTS profiles (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT    NOT NULL UNIQUE,
    avatar_path TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
)
"""


def _init_schema(conn: sqlite3.Connection) -> None:
    conn.execute(_SCHEMA_GAMES)
    conn.execute(_SCHEMA_PROFILES)
    conn.commit()


def _migrate_from_json_if_needed(conn: sqlite3.Connection) -> None:
    """Importe data_game.json dans la table games si celle-ci est vide."""
    n = conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]
    if n > 0:
        return
    if not LEGACY_JSON.exists():
        logger.info("Aucun data_game.json à migrer ; base vide.")
        return
    try:
        with open(LEGACY_JSON, encoding="utf-8") as f:
            games = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.error("Lecture %s échouée : %s", LEGACY_JSON, e)
        return
    if not isinstance(games, list):
        logger.error("Format inattendu dans %s (liste attendue).", LEGACY_JSON)
        return

    rows = [
        (
            g.get("name", ""),
            g.get("platform", ""),
            g.get("cover", ""),
            g.get("rom_path", ""),
            g.get("resume", ""),
        )
        for g in games if isinstance(g, dict)
    ]
    conn.executemany(
        "INSERT INTO games (name, platform, cover, rom_path, resume) VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    logger.info("Migration JSON → SQLite : %d jeux importés", len(rows))


# ============================================================
# Jeux
# ============================================================
def list_games() -> List[dict]:
    """Liste complète des jeux sous forme de dicts (utilisable tel quel par l'UI)."""
    rows = _ensure().execute(
        "SELECT id, name, platform, cover, rom_path, resume, is_favorite, play_count "
        "FROM games ORDER BY platform, name"
    ).fetchall()
    return [dict(r) for r in rows]


def count_games() -> int:
    row = _ensure().execute("SELECT COUNT(*) FROM games").fetchone()
    return int(row[0])


def total_play_count() -> int:
    """Somme globale (toutes manettes/profils confondus — cf. limitation du schéma)."""
    row = _ensure().execute("SELECT COALESCE(SUM(play_count), 0) FROM games").fetchone()
    return int(row[0])


def increment_play_count(game_id: int) -> None:
    """Appelée par launcher.py après un lancement réussi."""
    conn = _ensure()
    conn.execute("UPDATE games SET play_count = play_count + 1 WHERE id = ?", (game_id,))
    conn.commit()


def set_favorite(game_id: int, is_fav: bool) -> None:
    conn = _ensure()
    conn.execute(
        "UPDATE games SET is_favorite = ? WHERE id = ?", (1 if is_fav else 0, game_id)
    )
    conn.commit()


# ============================================================
# Profils
# ============================================================
def list_profiles() -> List[dict]:
    rows = _ensure().execute(
        "SELECT id, username, avatar_path, created_at FROM profiles ORDER BY id"
    ).fetchall()
    return [dict(r) for r in rows]


def get_profile(profile_id: int) -> Optional[dict]:
    row = _ensure().execute(
        "SELECT id, username, avatar_path, created_at FROM profiles WHERE id = ?",
        (profile_id,),
    ).fetchone()
    return dict(row) if row else None


def create_profile(username: str, avatar_path: Optional[str] = None) -> int:
    conn = _ensure()
    cur = conn.execute(
        "INSERT INTO profiles (username, avatar_path) VALUES (?, ?)",
        (username, avatar_path),
    )
    conn.commit()
    new_id = int(cur.lastrowid)
    logger.info("Profil créé : id=%d username=%r", new_id, username)
    return new_id


def get_active_profile() -> dict:
    """
    Retourne le profil actif. Stratégie :
      1. lit `active_profile_id` dans user_settings.json
      2. fallback : premier profil existant en BDD
      3. fallback ultime : crée "Joueur 1" et le marque actif
    Met à jour user_settings.json si nécessaire.
    """
    settings = config.load_user_settings()
    pid = settings.get("active_profile_id")
    if isinstance(pid, int):
        profile = get_profile(pid)
        if profile is not None:
            return profile
        logger.warning("active_profile_id=%d introuvable, fallback", pid)

    # Premier profil existant
    profiles = list_profiles()
    if profiles:
        first = profiles[0]
        settings["active_profile_id"] = first["id"]
        config.save_user_settings(settings)
        return first

    # Création d'un profil par défaut
    new_id = create_profile("Joueur 1", None)
    settings["active_profile_id"] = new_id
    config.save_user_settings(settings)
    profile = get_profile(new_id)
    assert profile is not None
    return profile


def set_active_profile(profile_id: int) -> None:
    """Persiste le choix du profil actif dans user_settings.json."""
    if get_profile(profile_id) is None:
        raise ValueError(f"profile_id={profile_id} inexistant")
    settings = config.load_user_settings()
    settings["active_profile_id"] = profile_id
    config.save_user_settings(settings)


# ============================================================
# Utilitaires d'affichage
# ============================================================
def format_created_at(iso_string: str) -> str:
    """Convertit '2026-01-15 12:34:56' (SQLite UTC) en '15/01/2026'."""
    try:
        dt = datetime.fromisoformat(iso_string.replace(" ", "T"))
        return dt.strftime("%d/%m/%Y")
    except (ValueError, AttributeError):
        return iso_string or "—"
