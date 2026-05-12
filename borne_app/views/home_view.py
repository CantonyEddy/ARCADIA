from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from .. import utils
from ..utils import (
    W_SIDEBAR,
    H_TOPBAR,
    C_ACCENT,
    C_BG_SECONDARY,
    C_TXT_PRI,
)

if TYPE_CHECKING:
    from ..borne_interface import BorneInterface


def draw_home_view(app: "BorneInterface") -> None:
    """Vue d'accueil simple avec quelques gros boutons."""
    area = pygame.Rect(
        W_SIDEBAR,
        H_TOPBAR,
        app.w_content_area,
        app.h_content_area,
    )

    title = utils.FONT_TITLE.render("HOME", True, C_ACCENT)
    app.ecran.blit(title, title.get_rect(midtop=(area.centerx, area.y + 40)))

    buttons = [
        ("PLAY", "GAMES"),
        ("PROFILE", "PROFILE"),
        ("SETTINGS", "SETTINGS"),
        ("EXIT", "EXIT"),
    ]

    for i, (label, _action) in enumerate(buttons):
        rect = pygame.Rect(0, 0, 320, 90)
        rect.center = (area.centerx, area.y + 200 + i * 120)
        pygame.draw.rect(app.ecran, C_BG_SECONDARY, rect, border_radius=20)
        pygame.draw.rect(app.ecran, (60, 60, 60), rect, width=2, border_radius=20)
        txt = utils.FONT_BOLD.render(label, True, C_TXT_PRI)
        app.ecran.blit(txt, txt.get_rect(center=rect.center))
