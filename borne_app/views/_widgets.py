"""
Mini-système de widgets pour les vues interactives (SETTINGS notamment).
Chaque widget gère son rendu et ses raccourcis clavier (handle_key).
"""
from __future__ import annotations

from typing import Callable, List, Tuple

import pygame

from .. import utils
from ..utils import (
    C_BG_SECONDARY,
    C_BG_TERTIARY,
    C_TXT_PRI,
    C_TXT_SEC,
    RADIUS,
)


class Widget:
    """Base abstraite : un widget dessinable et interactif."""

    def __init__(self, label: str) -> None:
        self.label = label
        self.rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)

    def draw(self, screen: pygame.Surface, rect: pygame.Rect, focused: bool) -> None:
        self.rect = rect
        self._draw_background(screen, rect, focused)
        self._draw_label(screen, rect)

    def _draw_background(self, screen: pygame.Surface, rect: pygame.Rect, focused: bool) -> None:
        bg = C_BG_TERTIARY if focused else C_BG_SECONDARY
        pygame.draw.rect(screen, bg, rect, border_radius=RADIUS)
        if focused:
            pygame.draw.rect(screen, utils.C_ACCENT, rect, width=2, border_radius=RADIUS)

    def _draw_label(self, screen: pygame.Surface, rect: pygame.Rect) -> None:
        txt = utils.FONT_REG.render(self.label, True, C_TXT_PRI)
        screen.blit(txt, (rect.x + 16, rect.centery - txt.get_height() // 2))

    def handle_key(self, key: int) -> bool:
        """Retourne True si l'event a été consommé par le widget."""
        return False


class Toggle(Widget):
    def __init__(self, label: str, value: bool, on_change: Callable[[bool], None]) -> None:
        super().__init__(label)
        self.value = value
        self.on_change = on_change

    def draw(self, screen: pygame.Surface, rect: pygame.Rect, focused: bool) -> None:
        super().draw(screen, rect, focused)
        sw_w, sw_h = 52, 26
        sw = pygame.Rect(rect.right - sw_w - 16, rect.centery - sw_h // 2, sw_w, sw_h)
        bg = utils.C_ACCENT if self.value else (80, 80, 80)
        pygame.draw.rect(screen, bg, sw, border_radius=13)
        knob_x = sw.right - 13 if self.value else sw.left + 13
        pygame.draw.circle(screen, C_TXT_PRI, (knob_x, sw.centery), 10)

    def handle_key(self, key: int) -> bool:
        if key == pygame.K_LEFT and self.value:
            self.value = False
            self.on_change(False)
            return True
        if key == pygame.K_RIGHT and not self.value:
            self.value = True
            self.on_change(True)
            return True
        if key in (pygame.K_RETURN, pygame.K_SPACE):
            self.value = not self.value
            self.on_change(self.value)
            return True
        return False


class Slider(Widget):
    def __init__(
        self,
        label: str,
        value: int,
        vmin: int,
        vmax: int,
        step: int,
        on_change: Callable[[int], None],
    ) -> None:
        super().__init__(label)
        self.value, self.vmin, self.vmax, self.step = value, vmin, vmax, step
        self.on_change = on_change

    def draw(self, screen: pygame.Surface, rect: pygame.Rect, focused: bool) -> None:
        super().draw(screen, rect, focused)
        val_surf = utils.FONT_BOLD.render(str(self.value), True, C_TXT_PRI)
        val_x = rect.right - val_surf.get_width() - 16
        screen.blit(val_surf, (val_x, rect.centery - val_surf.get_height() // 2))

        bar_w = 200
        bar = pygame.Rect(val_x - bar_w - 20, rect.centery - 3, bar_w, 6)
        pygame.draw.rect(screen, (80, 80, 80), bar, border_radius=3)
        span = max(1, self.vmax - self.vmin)
        ratio = (self.value - self.vmin) / span
        fill_w = max(0, min(bar.w, int(bar.w * ratio)))
        fill = pygame.Rect(bar.x, bar.y, fill_w, bar.h)
        pygame.draw.rect(screen, utils.C_ACCENT, fill, border_radius=3)
        pygame.draw.circle(screen, C_TXT_PRI, (bar.x + fill_w, bar.centery), 8)

    def handle_key(self, key: int) -> bool:
        if key == pygame.K_LEFT:
            self.value = max(self.vmin, self.value - self.step)
            self.on_change(self.value)
            return True
        if key == pygame.K_RIGHT:
            self.value = min(self.vmax, self.value + self.step)
            self.on_change(self.value)
            return True
        return False


class Choice(Widget):
    """Cycle entre N options. Utile pour couleur d'accent, langue, etc."""

    def __init__(
        self,
        label: str,
        options: List[Tuple[str, object]],
        current_index: int,
        on_change: Callable[[int], None],
    ) -> None:
        super().__init__(label)
        self.options = options
        self.index = max(0, min(current_index, len(options) - 1))
        self.on_change = on_change

    def draw(self, screen: pygame.Surface, rect: pygame.Rect, focused: bool) -> None:
        super().draw(screen, rect, focused)
        name, value = self.options[self.index]
        right_x = rect.right - 16

        if isinstance(value, (tuple, list)) and len(value) == 3:
            try:
                pygame.draw.circle(screen, tuple(value), (right_x - 12, rect.centery), 10)
                pygame.draw.circle(
                    screen, C_TXT_SEC, (right_x - 12, rect.centery), 10, width=1
                )
                right_x -= 32
            except (TypeError, ValueError):
                pass

        arrow_color = C_TXT_PRI if focused else C_TXT_SEC
        name_surf = utils.FONT_BOLD.render(f"< {name} >", True, arrow_color)
        screen.blit(
            name_surf,
            (right_x - name_surf.get_width(), rect.centery - name_surf.get_height() // 2),
        )

    def handle_key(self, key: int) -> bool:
        if key == pygame.K_LEFT:
            self.index = (self.index - 1) % len(self.options)
            self.on_change(self.index)
            return True
        if key == pygame.K_RIGHT:
            self.index = (self.index + 1) % len(self.options)
            self.on_change(self.index)
            return True
        return False


class Button(Widget):
    def __init__(self, label: str, on_click: Callable[[], None]) -> None:
        super().__init__(label)
        self.on_click = on_click

    def draw(self, screen: pygame.Surface, rect: pygame.Rect, focused: bool) -> None:
        bg = utils.C_ACCENT if focused else C_BG_TERTIARY
        pygame.draw.rect(screen, bg, rect, border_radius=RADIUS)
        if focused:
            pygame.draw.rect(screen, C_TXT_PRI, rect, width=2, border_radius=RADIUS)
        txt_color = C_BG_SECONDARY if focused else C_TXT_PRI
        txt = utils.FONT_BOLD.render(self.label, True, txt_color)
        screen.blit(txt, txt.get_rect(center=rect.center))

    def handle_key(self, key: int) -> bool:
        if key in (pygame.K_RETURN, pygame.K_SPACE):
            self.on_click()
            return True
        return False


class InfoLine(Widget):
    """Lecture seule. La valeur est récupérée à chaque frame via get_value()."""

    def __init__(self, label: str, get_value: Callable[[], str]) -> None:
        super().__init__(label)
        self.get_value = get_value

    def draw(self, screen: pygame.Surface, rect: pygame.Rect, focused: bool) -> None:
        # Le focus visuel reste discret : pas de bordure d'accent puisque non interactif
        bg = C_BG_TERTIARY if focused else C_BG_SECONDARY
        pygame.draw.rect(screen, bg, rect, border_radius=RADIUS)
        if focused:
            pygame.draw.rect(screen, C_TXT_SEC, rect, width=1, border_radius=RADIUS)
        self._draw_label(screen, rect)

        try:
            val = self.get_value()
        except Exception:
            val = "—"
        val_surf = utils.FONT_REG.render(val, True, C_TXT_SEC)
        screen.blit(
            val_surf,
            (rect.right - val_surf.get_width() - 16, rect.centery - val_surf.get_height() // 2),
        )

    def handle_key(self, key: int) -> bool:
        return False
