import pygame
from . import config
from .utils import (
    W_SIDEBAR,
    H_TOPBAR,
    C_BG_SECONDARY,
    C_BG_TERTIARY,
    C_ACCENT,
    C_TXT_SEC,
)


class Sidebar:
    """
    Gère l'affichage et la sélection de la barre latérale.
    """

    def __init__(self, h_screen: int):
        self.icons = ["A", "H", "G", "S"]
        self.routes = {
            "A": "PROFILE",
            "H": "HOME",
            "G": "GAMES",
            "S": "SETTINGS",
        }
        self.selected_index = 2  # GAMES par défaut
        self.focus = False
        self.rect = pygame.Rect(0, 0, W_SIDEBAR, h_screen)
        self.icon_rects = []

    def draw(self, app):
        """
        Dessine la sidebar sur l'écran de l'app, avec les icônes d'assets/icon.
        """
        screen = app.ecran

        bg = C_BG_TERTIARY if self.focus else C_BG_SECONDARY
        pygame.draw.rect(screen, bg, self.rect)
        pygame.draw.line(
            screen, (60, 60, 60), (W_SIDEBAR, 0), (W_SIDEBAR, self.rect.height)
        )

        if self.focus:
            pygame.draw.rect(
                screen,
                C_ACCENT,
                self.rect.inflate(-4, -4),
                width=2,
                border_radius=10,
            )

        self.icon_rects = []
        y = H_TOPBAR + 40
        for i, char in enumerate(self.icons):
            center = (W_SIDEBAR // 2, y)
            rect = pygame.Rect(0, 0, 60, 60)
            rect.center = center
            self.icon_rects.append((rect, char, i))

            color = C_ACCENT if i == self.selected_index else C_TXT_SEC

            if char == "A":
                # Avatar circulaire
                pygame.draw.circle(screen, C_BG_TERTIARY, center, 20)
                if i == self.selected_index:
                    pygame.draw.circle(screen, color, center, 22, width=2)
            else:
                # Icône image (home / games / settings)
                icon_path = config.get_icon_path(char)
                icon_surf = app.image_cache.get(icon_path, (30, 30), color_override=color)
                screen.blit(icon_surf, icon_surf.get_rect(center=center))
            y += 80

    def move_selection(self, direction: int):
        self.selected_index = max(
            0, min(len(self.icons) - 1, self.selected_index + direction)
        )
        return self.routes[self.icons[self.selected_index]]
