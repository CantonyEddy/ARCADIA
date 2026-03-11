import pygame

from .. import utils
from ..utils import (
    W_SIDEBAR,
    PADDING,
    RADIUS,
    C_BG_SECONDARY,
    C_BG_TERTIARY,
    C_TXT_PRI,
    C_TXT_SEC,
    C_ACCENT,
    C_ACCENT_HOVER,
)


def draw_games_view(app, mouse_pos):
    """
    Vue principale des jeux : liste à gauche, détails à droite.
    Reprend la logique de l'ancienne méthode draw_games_view de BorneInterface.
    """
    # --- LISTE DES JEUX (gauche) ---
    app.ecran.set_clip(app.rect_list_area)
    app.get_games_for_selected_tab()

    start_y = app.rect_list_area.y + PADDING - app.scroll_y
    list_has_focus = app.focus_area == "LIST"

    for i, game in enumerate(app.games_list_by_platform):
        y = start_y + i * (app.item_height + app.item_margin)

        if y + app.item_height < 0 or y > app.h_ecran:
            continue

        rect_item = pygame.Rect(
            W_SIDEBAR + PADDING,
            y,
            app.w_list_panel - (PADDING * 2),
            app.item_height,
        )
        is_sel = i == app.selected_index

        if is_sel and list_has_focus:
            bg_col = C_BG_TERTIARY
        elif is_sel:
            bg_col = (35, 35, 35)
        else:
            bg_col = C_BG_SECONDARY

        pygame.draw.rect(app.ecran, bg_col, rect_item, border_radius=RADIUS)

        if is_sel:
            border_color = C_ACCENT if list_has_focus else (120, 120, 120)
            pygame.draw.rect(
                app.ecran,
                border_color,
                rect_item,
                width=2,
                border_radius=RADIUS,
            )
            pygame.draw.rect(
                app.ecran,
                border_color,
                (
                    rect_item.x,
                    rect_item.y + 10,
                    6,
                    rect_item.height - 20,
                ),
                border_radius=3,
            )

        # Thumbnail
        rect_thumb = pygame.Rect(rect_item.x + 10, rect_item.y + 10, 60, 60)
        rect_thumb_img = app.image_cache.get(game["cover"], (60, 60))
        app.ecran.blit(rect_thumb_img, rect_thumb)
        pygame.draw.rect(app.ecran, (54, 20, 98), rect_thumb, border_radius=8)
        app.ecran.blit(rect_thumb_img, rect_thumb)

        # Textes
        title_color = C_TXT_PRI if (is_sel and list_has_focus) else C_TXT_SEC
        txt_name = utils.FONT_BOLD.render(game["name"], True, title_color)
        txt_sys = utils.FONT_SMALL.render(
            f"[{game['platform']}]",
            True,
            C_ACCENT if is_sel else (100, 100, 100),
        )

        app.ecran.blit(txt_name, (rect_item.x + 85, rect_item.y + 15))
        app.ecran.blit(txt_sys, (rect_item.x + 85, rect_item.y + 45))

    app.ecran.set_clip(None)

    if list_has_focus:
        focus_rect = app.rect_list_area.inflate(-8, -8)
        pygame.draw.rect(
            app.ecran, C_ACCENT, focus_rect, width=2, border_radius=RADIUS
        )

    # --- PANEL DÉTAIL (droite) ---
    rect_panel_bg = app.rect_detail_area.inflate(-40, -40)
    pygame.draw.rect(app.ecran, C_BG_SECONDARY, rect_panel_bg, border_radius=RADIUS)

    if not app.games_list_by_platform:
        return

    game = app.games_list_by_platform[app.selected_index]
    cx = rect_panel_bg.centerx

    # Grande image
    rect_img_big = pygame.Rect(0, 0, 300, 300)
    rect_img_big.center = (cx, rect_panel_bg.y + 200)

    pygame.draw.rect(
        app.ecran, (0, 0, 0), rect_img_big.move(10, 10), border_radius=RADIUS
    )
    pygame.draw.rect(app.ecran, (50, 50, 50), rect_img_big, border_radius=RADIUS)

    lbl_cover_base = app.image_cache.get(game["cover"], (300, 300))
    lbl_cover = lbl_cover_base.copy()

    mask = pygame.Surface((300, 300), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255), (0, 0, 300, 300), border_radius=RADIUS)
    lbl_cover.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    app.ecran.blit(lbl_cover, rect_img_big)

    # Titre
    txt_big_title = utils.FONT_TITLE.render(game["name"].upper(), True, C_ACCENT)
    txt_shadow = utils.FONT_TITLE.render(
        game["name"].upper(),
        True,
        (C_ACCENT[0] // 3, C_ACCENT[1] // 3, 0),
    )
    app.ecran.blit(
        txt_shadow,
        txt_shadow.get_rect(center=(cx + 2, rect_panel_bg.y + 400 + 2)),
    )
    app.ecran.blit(
        txt_big_title,
        txt_big_title.get_rect(center=(cx, rect_panel_bg.y + 400)),
    )

    # Description
    desc_y = rect_panel_bg.y + 460
    lines = [
        f"Système: {game['platform'].upper()}",
        f"{game['resume']}",
    ]
    for line in lines:
        t = utils.FONT_REG.render(line, True, C_TXT_SEC)
        app.ecran.blit(t, t.get_rect(center=(cx, desc_y)))
        desc_y += 30

    # Bouton JOUER
    rect_btn = pygame.Rect(0, 0, 220, 60)
    rect_btn.center = (cx, app.h_ecran - 100)
    is_hover = rect_btn.collidepoint(mouse_pos)
    col_btn = C_ACCENT_HOVER if is_hover else C_ACCENT

    pygame.draw.rect(
        app.ecran,
        (C_ACCENT[0] // 2, C_ACCENT[1] // 2, 0),
        rect_btn.move(0, 5),
        border_radius=30,
    )
    pygame.draw.rect(app.ecran, col_btn, rect_btn, border_radius=30)

    lbl_jouer = utils.FONT_BOLD.render("JOUER", True, C_BG_SECONDARY)
    app.ecran.blit(lbl_jouer, lbl_jouer.get_rect(center=rect_btn.center))


