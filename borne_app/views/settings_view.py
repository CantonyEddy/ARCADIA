import pygame

from .. import utils
from ..utils import (
    W_SIDEBAR,
    H_TOPBAR,
    C_ACCENT,
)


def draw_settings_view(app):
    area = pygame.Rect(
        W_SIDEBAR,
        H_TOPBAR,
        app.w_content_area,
        app.h_content_area,
    )
    txt = utils.FONT_TITLE.render("SETTINGS", True, C_ACCENT)
    app.ecran.blit(txt, txt.get_rect(center=area.center))


