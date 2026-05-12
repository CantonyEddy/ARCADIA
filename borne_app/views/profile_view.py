from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from .. import database, utils
from ..utils import (
    C_BG_SECONDARY,
    C_TXT_PRI,
    C_TXT_SEC,
    H_TOPBAR,
    PADDING,
    RADIUS,
    W_SIDEBAR,
)

if TYPE_CHECKING:
    from ..borne_interface import BorneInterface


# Diamètre de l'avatar circulaire
_AVATAR_SIZE = 200


def draw_profile_view(app: "BorneInterface") -> None:
    """Affiche l'avatar et les statistiques du profil actif."""
    area = pygame.Rect(
        W_SIDEBAR,
        H_TOPBAR,
        app.w_content_area,
        app.h_content_area,
    )

    profile = app.active_profile  # mis en cache par BorneInterface

    # Titre
    title = utils.FONT_TITLE.render("PROFIL", True, utils.C_ACCENT)
    app.ecran.blit(title, title.get_rect(midtop=(area.centerx, area.y + 30)))

    # Avatar
    avatar_cx = area.centerx
    avatar_cy = area.y + 140 + _AVATAR_SIZE // 2
    _draw_avatar(app, profile, avatar_cx, avatar_cy)

    # Username
    username = profile.get("username", "?")
    name_surf = utils.FONT_TITLE.render(username, True, C_TXT_PRI)
    app.ecran.blit(
        name_surf,
        name_surf.get_rect(midtop=(area.centerx, avatar_cy + _AVATAR_SIZE // 2 + 24)),
    )

    # Statistiques (cartes)
    try:
        games_count = database.count_games()
        plays_total = database.total_play_count()
    except Exception:
        games_count, plays_total = 0, 0

    stats = [
        ("Jeux dans la bibliothèque", str(games_count)),
        ("Lancements totaux", str(plays_total)),
    ]
    _draw_stats(app, area, stats, avatar_cy + _AVATAR_SIZE // 2 + 100)

    # Date de création
    created = database.format_created_at(profile.get("created_at", ""))
    footer = utils.FONT_SMALL.render(
        f"Compte créé le {created}", True, C_TXT_SEC
    )
    app.ecran.blit(
        footer,
        footer.get_rect(midbottom=(area.centerx, area.bottom - 30)),
    )


def _draw_avatar(app: "BorneInterface", profile: dict, cx: int, cy: int) -> None:
    """Dessine l'avatar avec une ombre et une bordure accent."""
    radius = _AVATAR_SIZE // 2
    # Ombre
    pygame.draw.circle(app.ecran, (0, 0, 0), (cx + 4, cy + 4), radius)
    utils.draw_avatar(
        app.ecran,
        profile,
        center=(cx, cy),
        diameter=_AVATAR_SIZE,
        image_cache=app.image_cache,
        border_color=utils.C_ACCENT,
        border_width=3,
    )


def _draw_stats(app: "BorneInterface", area: pygame.Rect, stats: list, top_y: int) -> None:
    """Dessine deux cartes côte à côte avec libellé + valeur."""
    card_w = 260
    card_h = 90
    gap = 24
    total_w = card_w * len(stats) + gap * (len(stats) - 1)
    start_x = area.centerx - total_w // 2

    for i, (label, value) in enumerate(stats):
        x = start_x + i * (card_w + gap)
        rect = pygame.Rect(x, top_y, card_w, card_h)
        pygame.draw.rect(app.ecran, C_BG_SECONDARY, rect, border_radius=RADIUS)
        pygame.draw.rect(app.ecran, utils.C_ACCENT, rect, width=2, border_radius=RADIUS)

        lbl = utils.FONT_SMALL.render(label, True, C_TXT_SEC)
        val = utils.FONT_TITLE.render(value, True, C_TXT_PRI)
        app.ecran.blit(lbl, (rect.x + PADDING, rect.y + 12))
        app.ecran.blit(
            val,
            val.get_rect(
                bottomright=(rect.right - PADDING, rect.bottom - 8)
            ),
        )
