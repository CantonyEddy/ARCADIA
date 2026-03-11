import pygame
from . import utils
from .utils import (
    W_SIDEBAR,
    H_TOPBAR,
    C_BG_SECONDARY,
    C_BG_TERTIARY,
    C_ACCENT,
    C_ACCENT_HOVER,
    C_TXT_PRI,
    C_TXT_SEC,
)


class TopBar:
    """
    Gère l'affichage de la barre du haut (tabs plateformes + horloge).
    """

    def __init__(self, w_screen: int, tabs):
        self.rect = pygame.Rect(W_SIDEBAR, 0, w_screen - W_SIDEBAR, H_TOPBAR)
        self.selected_tab = 0
        self.focus = False
        self.tabs = list(tabs)

        # Polices locales pour la topbar (évite les soucis de globals None)
        fonts = ["Segoe UI", "Verdana", "Arial"]
        self.font_bold = pygame.font.SysFont(fonts, 24, bold=True)
        self.font_time = pygame.font.SysFont("Consolas", 24, bold=True)

    def draw(self, screen: pygame.Surface, current_view: str, time_str: str):
        bg = C_BG_TERTIARY if self.focus else C_BG_SECONDARY
        pygame.draw.rect(screen, bg, self.rect)
        pygame.draw.line(
            screen, (60, 60, 60), (W_SIDEBAR, H_TOPBAR), (self.rect.right, H_TOPBAR)
        )
        if self.focus:
            pygame.draw.rect(
                screen,
                C_ACCENT,
                self.rect.inflate(-4, -4),
                width=2,
                border_radius=10,
            )

        if current_view == "GAMES":
            x_tab = W_SIDEBAR + 40
            for i, tab in enumerate(self.tabs):
                is_active = i == self.selected_tab
                bg_color = (
                    C_ACCENT_HOVER
                    if is_active and self.focus
                    else (C_ACCENT if is_active else C_BG_SECONDARY)
                )
                txt_color = C_TXT_PRI if is_active else C_TXT_SEC
                txt_surf = self.font_bold.render(tab.upper(), True, txt_color)
                w_pill = txt_surf.get_width() + 40
                rect_pill = pygame.Rect(
                    x_tab, (H_TOPBAR - 40) // 2, w_pill, 40
                )
                if is_active:
                    pygame.draw.rect(screen, bg_color, rect_pill, border_radius=20)
                screen.blit(txt_surf, txt_surf.get_rect(center=rect_pill.center))
                x_tab += w_pill + 20

        txt_time = self.font_time.render(time_str, True, C_TXT_SEC)
        screen.blit(
            txt_time,
            (
                self.rect.right - 100,
                (H_TOPBAR - txt_time.get_height()) // 2,
            ),
        )
