"""
Vue SETTINGS : liste de catégories à gauche (40 %), widgets de la catégorie
sélectionnée à droite (60 %). Le layout suit la convention du reste de l'app.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from .. import utils
from ..utils import (
    C_BG_SECONDARY,
    C_BG_TERTIARY,
    C_TXT_PRI,
    C_TXT_SEC,
    PADDING,
    RADIUS,
    W_SIDEBAR,
)

if TYPE_CHECKING:
    from ..borne_interface import BorneInterface


CATEGORIES = ["AUDIO", "AFFICHAGE", "CONTROLES", "SYSTEME"]


def draw_settings_view(app: "BorneInterface") -> None:
    _draw_category_list(app)
    _draw_widget_panel(app)


def _draw_category_list(app: "BorneInterface") -> None:
    panel_focus = app.focus_area == "SETTINGS_CATS"

    # En-tête simple
    header = utils.FONT_BOLD.render("PARAMÈTRES", True, utils.C_ACCENT)
    app.ecran.blit(
        header,
        (W_SIDEBAR + PADDING, app.rect_list_area.y + PADDING - 5),
    )

    base_y = app.rect_list_area.y + PADDING + 40
    item_h = 56
    gap = 14

    for i, cat in enumerate(CATEGORIES):
        rect = pygame.Rect(
            W_SIDEBAR + PADDING,
            base_y + i * (item_h + gap),
            app.w_list_panel - PADDING * 2,
            item_h,
        )
        is_sel = i == app.settings_category_index

        if is_sel and panel_focus:
            bg = C_BG_TERTIARY
        elif is_sel:
            bg = (35, 35, 35)
        else:
            bg = C_BG_SECONDARY
        pygame.draw.rect(app.ecran, bg, rect, border_radius=RADIUS)

        if is_sel:
            border = utils.C_ACCENT if panel_focus else (120, 120, 120)
            pygame.draw.rect(app.ecran, border, rect, width=2, border_radius=RADIUS)
            # Petite barre verticale d'accent à gauche, comme dans GAMES
            pygame.draw.rect(
                app.ecran,
                border,
                (rect.x, rect.y + 10, 6, rect.height - 20),
                border_radius=3,
            )

        col = C_TXT_PRI if (is_sel and panel_focus) else C_TXT_SEC
        txt = utils.FONT_BOLD.render(cat, True, col)
        app.ecran.blit(txt, (rect.x + 24, rect.centery - txt.get_height() // 2))


def _draw_widget_panel(app: "BorneInterface") -> None:
    panel_focus = app.focus_area == "SETTINGS_WIDGETS"

    panel_bg = app.rect_detail_area.inflate(-40, -40)
    pygame.draw.rect(app.ecran, C_BG_SECONDARY, panel_bg, border_radius=RADIUS)
    if panel_focus:
        pygame.draw.rect(
            app.ecran, utils.C_ACCENT, panel_bg, width=2, border_radius=RADIUS
        )

    # Titre de la catégorie courante
    cat_name = CATEGORIES[app.settings_category_index]
    title = utils.FONT_TITLE.render(cat_name, True, utils.C_ACCENT)
    app.ecran.blit(
        title,
        (panel_bg.x + 24, panel_bg.y + 16),
    )

    widgets = app.settings_widgets[app.settings_category_index]
    if not widgets:
        hint = utils.FONT_REG.render("(Aucun paramètre)", True, C_TXT_SEC)
        app.ecran.blit(
            hint,
            hint.get_rect(center=(panel_bg.centerx, panel_bg.centery)),
        )
        return

    w_rect_w = panel_bg.width - 48
    w_h = 64
    gap = 14
    y = panel_bg.y + 16 + title.get_height() + 24

    for i, widget in enumerate(widgets):
        rect = pygame.Rect(panel_bg.x + 24, y, w_rect_w, w_h)
        focused = panel_focus and i == app.settings_widget_index
        widget.draw(app.ecran, rect, focused)
        y += w_h + gap
