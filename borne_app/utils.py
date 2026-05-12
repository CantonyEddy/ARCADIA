from __future__ import annotations

import json
import logging
from pathlib import Path

import pygame

logger = logging.getLogger(__name__)

# --- PALETTE DE COULEURS ---
C_BG_PRIMARY = (24, 24, 24)
C_BG_SECONDARY = (37, 37, 37)
C_BG_TERTIARY = (48, 48, 48)

# Accent (peut être surchargé par datas/user_settings.json — cf. _load_user_accent)
C_ACCENT = (255, 107, 0)
C_ACCENT_HOVER = (255, 158, 0)

C_TXT_PRI = (255, 255, 255)
C_TXT_SEC = (160, 160, 160)

# --- DIMENSIONS ---
W_SIDEBAR = 90
H_TOPBAR = 80
PADDING = 20
RADIUS = 12


# --- POLICES (remplies dynamiquement après pygame.init) ---
FONT_SMALL = None
FONT_REG = None
FONT_BOLD = None
FONT_TITLE = None
FONT_TIME = None


def init_fonts() -> None:
    """Initialise les polices globales. À appeler APRÈS pygame.init()."""
    global FONT_SMALL, FONT_REG, FONT_BOLD, FONT_TITLE, FONT_TIME

    fonts = ["Segoe UI", "Verdana", "Arial"]
    FONT_SMALL = pygame.font.SysFont(fonts, 16)
    FONT_REG = pygame.font.SysFont(fonts, 20)
    FONT_BOLD = pygame.font.SysFont(fonts, 24, bold=True)
    FONT_TITLE = pygame.font.SysFont(fonts, 40, bold=True)
    FONT_TIME = pygame.font.SysFont("Consolas", 24, bold=True)


def _load_user_accent() -> None:
    """
    Lit datas/user_settings.json (s'il existe) pour surcharger C_ACCENT.
    Appelé à l'import du module pour que tous les `from .utils import C_ACCENT`
    voient la couleur choisie par l'utilisateur.
    """
    global C_ACCENT, C_ACCENT_HOVER
    try:
        path = Path(__file__).resolve().parent.parent / "datas" / "user_settings.json"
        if not path.exists():
            return
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        color = data.get("accent_color")
        if isinstance(color, (list, tuple)) and len(color) == 3:
            C_ACCENT = tuple(int(c) for c in color)
            C_ACCENT_HOVER = tuple(min(255, int(c) + 50) for c in C_ACCENT)
    except (OSError, json.JSONDecodeError, ValueError) as e:
        logger.warning("Lecture accent utilisateur échouée : %s", e)


_load_user_accent()


def draw_avatar(
    screen: pygame.Surface,
    profile: dict | None,
    center: tuple,
    diameter: int,
    image_cache=None,
    border_color: tuple | None = None,
    border_width: int | None = None,
) -> None:
    """Dessine un avatar circulaire (image si disponible, sinon disque accent + initiale).

    Utilisé à la fois par la sidebar (petit format) et la vue PROFILE (grand format).
    """
    radius = diameter // 2
    cx, cy = center
    profile = profile or {}
    avatar_path = profile.get("avatar_path") or ""
    img_loaded = False

    if avatar_path and image_cache is not None:
        try:
            if Path(avatar_path).exists():
                img = image_cache.get(avatar_path, (diameter, diameter))
                mask = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
                pygame.draw.circle(mask, (255, 255, 255, 255), (radius, radius), radius)
                clipped = img.copy()
                clipped.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                screen.blit(clipped, clipped.get_rect(center=(cx, cy)))
                img_loaded = True
        except (OSError, pygame.error) as e:
            logger.warning("Chargement avatar %s échoué : %s", avatar_path, e)

    if not img_loaded:
        pygame.draw.circle(screen, C_ACCENT, (cx, cy), radius)
        initiale = (profile.get("username") or "?").strip()[:1].upper() or "?"
        font_size = max(8, int(diameter * 0.55))
        font = pygame.font.SysFont(
            ["Segoe UI", "Verdana", "Arial"], font_size, bold=True
        )
        letter = font.render(initiale, True, C_TXT_PRI)
        screen.blit(letter, letter.get_rect(center=(cx, cy)))

    if border_color is not None:
        bw = border_width if border_width is not None else max(2, diameter // 60)
        pygame.draw.circle(screen, border_color, (cx, cy), radius, width=bw)


class ImageCache:
    """Petit cache d'images pour éviter de recharger les textures à chaque frame."""

    def __init__(self) -> None:
        self._cache: dict = {}

    def clear(self) -> None:
        self._cache = {}

    def get(self, path, size, color_override=None):
        key = (path, size, color_override)

        if key not in self._cache:
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, size)

                if color_override:
                    img.fill(color_override, special_flags=pygame.BLEND_RGBA_MULT)

                self._cache[key] = img
            except Exception as e:
                logger.warning("Échec chargement image %s : %s", path, e)
                fallback = pygame.Surface(size)
                fallback.fill((255, 0, 255))
                self._cache[key] = fallback

        return self._cache[key]
