from __future__ import annotations

import datetime
import logging
from pathlib import Path
from typing import List, Tuple

import pygame

from . import config, game_scanner, launcher, utils
from .sidebar import Sidebar
from .topbar import TopBar
from .utils import (
    C_BG_PRIMARY,
    H_TOPBAR,
    PADDING,
    W_SIDEBAR,
    ImageCache,
    init_fonts,
)
from .views._widgets import Button, Choice, InfoLine, Slider, Toggle, Widget
from .views.games_view import draw_games_view
from .views.home_view import draw_home_view
from .views.profile_view import draw_profile_view
from .views.settings_view import CATEGORIES as SETTINGS_CATEGORIES
from .views.settings_view import draw_settings_view

logger = logging.getLogger(__name__)


# Options offertes par la Choice "Couleur d'accent"
ACCENT_OPTIONS: List[Tuple[str, List[int]]] = [
    ("Orange", [255, 107, 0]),
    ("Bleu",   [0, 140, 255]),
    ("Vert",   [60, 200, 100]),
    ("Rose",   [230, 80, 180]),
]

BG_MUSIC_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "audio" / "bg_music.ogg"
)


class BorneInterface:
    """
    Classe principale qui orchestre la borne :
    - boucle principale Pygame
    - gestion du focus clavier
    - délégation du rendu à la sidebar, topbar et vues.
    """

    def __init__(self) -> None:
        pygame.init()

        # Audio (peut échouer en l'absence de device)
        self.audio_ok = False
        try:
            pygame.mixer.init()
            self.audio_ok = True
        except pygame.error as e:
            logger.warning("Init audio impossible : %s", e)

        # Manette (lecture seule pour l'instant)
        pygame.joystick.init()

        # Écran
        info = pygame.display.Info()
        self.w_ecran = info.current_w
        self.h_ecran = info.current_h
        self.ecran = pygame.display.set_mode(
            (self.w_ecran, self.h_ecran),
            pygame.FULLSCREEN | pygame.DOUBLEBUF,
        )
        pygame.display.set_caption("Arcade Dashboard")

        init_fonts()

        # Préférences utilisateur
        self._user_settings = config.load_user_settings()
        self.volume: int = int(self._user_settings.get("volume", 80))
        self.music_enabled: bool = bool(self._user_settings.get("music_enabled", False))
        self.show_fps: bool = bool(self._user_settings.get("show_fps", False))

        # Données jeux
        self.games_list = game_scanner.load_games_data()
        self.games_list_by_platform: list[dict] = []

        platforms_with_games = {
            g.get("platform", "").upper() for g in self.games_list
        }
        tabs = [
            t for t in config.get_all_core_keys()
            if t.upper() in platforms_with_games
        ]

        # Composants UI
        self.sidebar = Sidebar(self.h_ecran)
        self.topbar = TopBar(self.w_ecran, tabs)

        # État de navigation
        # focus_area ∈ {"SIDEBAR", "TOPBAR", "LIST", "SETTINGS_CATS", "SETTINGS_WIDGETS"}
        self.current_view = "GAMES"
        self.focus_area = "TOPBAR"

        # Liste de jeux
        self.selected_index = 0
        self.scroll_y = 0
        self._last_tab_index: int | None = None

        # Settings
        self.settings_category_index = 0
        self.settings_widget_index = 0

        # Layout
        self.rect_sidebar = pygame.Rect(0, 0, W_SIDEBAR, self.h_ecran)
        self.rect_topbar = pygame.Rect(
            W_SIDEBAR, 0, self.w_ecran - W_SIDEBAR, H_TOPBAR
        )
        self.w_content_area = self.w_ecran - W_SIDEBAR
        self.h_content_area = self.h_ecran - H_TOPBAR
        self.w_list_panel = int(self.w_content_area * 0.4)
        self.w_detail_panel = self.w_content_area - self.w_list_panel
        self.rect_list_area = pygame.Rect(
            W_SIDEBAR, H_TOPBAR, self.w_list_panel, self.h_content_area
        )
        self.rect_detail_area = pygame.Rect(
            W_SIDEBAR + self.w_list_panel,
            H_TOPBAR,
            self.w_detail_panel,
            self.h_content_area,
        )

        self.item_height = 80
        self.item_margin = 15

        self.image_cache = ImageCache()
        self.clock = pygame.time.Clock()

        # Musique de fond
        self.music_loaded = False
        if self.audio_ok and BG_MUSIC_PATH.exists():
            try:
                pygame.mixer.music.load(str(BG_MUSIC_PATH))
                pygame.mixer.music.set_volume(self.volume / 100.0)
                self.music_loaded = True
                if self.music_enabled:
                    pygame.mixer.music.play(loops=-1)
            except pygame.error as e:
                logger.warning("Chargement musique échoué : %s", e)
        elif self.audio_ok:
            logger.info("Pas de musique d'ambiance (fichier absent : %s)", BG_MUSIC_PATH)

        # Construction des widgets SETTINGS (après chargement settings/audio)
        self.settings_widgets: List[List[Widget]] = self._build_settings_widgets()

        self.refresh_games_for_selected_tab()

    # ============================================================
    # BOUCLE PRINCIPALE
    # ============================================================
    def run(self) -> None:
        running = True

        while running:
            now = datetime.datetime.now()
            time_str = now.strftime("%H:%M")
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (
                        pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
                    ):
                        self.handle_arrow_key(event.key)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.handle_enter(event.key)
                elif event.type == pygame.MOUSEWHEEL:
                    self.scroll_y -= event.y * 30
                    self.limiter_scroll()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.check_click(mouse_pos)

            self.draw(time_str, mouse_pos)
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    # ============================================================
    # SCROLL LISTE JEUX
    # ============================================================
    def ajuster_scroll(self) -> None:
        y_pos = self.selected_index * (self.item_height + self.item_margin) + PADDING
        if y_pos < self.scroll_y:
            self.scroll_y = y_pos - PADDING
        elif y_pos + self.item_height > self.scroll_y + self.rect_list_area.height:
            self.scroll_y = (
                y_pos + self.item_height + PADDING - self.rect_list_area.height
            )

    def limiter_scroll(self) -> None:
        content_h = len(self.games_list_by_platform) * (
            self.item_height + self.item_margin
        ) + PADDING
        max_s = max(0, content_h - self.rect_list_area.height)
        self.scroll_y = max(0, min(self.scroll_y, max_s))

    # ============================================================
    # NAVIGATION CLAVIER
    # ============================================================
    def handle_arrow_key(self, key: int) -> None:
        # Aiguillage par vue
        if self.current_view == "SETTINGS":
            self._handle_settings_arrow(key)
            return

        # === Vue GAMES (comportement existant) ===
        if key == pygame.K_UP:
            if self.focus_area == "SIDEBAR":
                if self.sidebar.selected_index > 0:
                    self.sidebar.move_selection(-1)
                    self.current_view = self.sidebar.routes[
                        self.sidebar.icons[self.sidebar.selected_index]
                    ]
            elif self.focus_area == "LIST" and self.current_view == "GAMES":
                if self.selected_index > 0:
                    self.selected_index = max(0, self.selected_index - 1)
                    self.ajuster_scroll()
                else:
                    self.focus_area = "TOPBAR"

        elif key == pygame.K_DOWN:
            if self.focus_area == "SIDEBAR":
                if self.sidebar.selected_index < len(self.sidebar.icons) - 1:
                    self.sidebar.move_selection(1)
                    self.current_view = self.sidebar.routes[
                        self.sidebar.icons[self.sidebar.selected_index]
                    ]
                else:
                    if self.current_view == "GAMES":
                        self.focus_area = "TOPBAR"
            elif self.focus_area == "TOPBAR" and self.current_view == "GAMES":
                self.focus_area = "LIST"
            elif self.focus_area == "LIST" and self.current_view == "GAMES":
                self.selected_index = min(
                    len(self.games_list_by_platform) - 1, self.selected_index + 1
                )
                self.ajuster_scroll()

        elif key == pygame.K_LEFT:
            if self.focus_area == "TOPBAR" and self.current_view == "GAMES":
                if self.topbar.selected_tab > 0:
                    self.topbar.selected_tab -= 1
                    self.selected_index = 0
                    self.ajuster_scroll()
                else:
                    self.focus_area = "SIDEBAR"
            elif self.focus_area == "LIST":
                self.focus_area = "SIDEBAR"

        elif key == pygame.K_RIGHT:
            if self.focus_area == "TOPBAR" and self.current_view == "GAMES":
                if self.topbar.selected_tab < len(self.topbar.tabs) - 1:
                    self.topbar.selected_tab += 1
                    self.selected_index = 0
                    self.ajuster_scroll()
            elif self.focus_area == "SIDEBAR":
                if self.current_view == "GAMES":
                    self.focus_area = "TOPBAR"

    def _handle_settings_arrow(self, key: int) -> None:
        """Navigation dédiée à la vue SETTINGS.

        Schéma de navigation :
          SIDEBAR ─K_RIGHT→ SETTINGS_CATS ─K_RIGHT→ SETTINGS_WIDGETS
                  ←K_LEFT─                ←K_UP (à idx 0)─
        """
        if self.focus_area == "SIDEBAR":
            if key == pygame.K_UP and self.sidebar.selected_index > 0:
                self.sidebar.move_selection(-1)
                self.current_view = self.sidebar.routes[
                    self.sidebar.icons[self.sidebar.selected_index]
                ]
            elif key == pygame.K_DOWN and self.sidebar.selected_index < len(self.sidebar.icons) - 1:
                self.sidebar.move_selection(1)
                self.current_view = self.sidebar.routes[
                    self.sidebar.icons[self.sidebar.selected_index]
                ]
            elif key == pygame.K_RIGHT:
                self.focus_area = "SETTINGS_CATS"
                self.settings_widget_index = 0
            return

        if self.focus_area == "SETTINGS_CATS":
            if key == pygame.K_UP:
                self.settings_category_index = max(0, self.settings_category_index - 1)
                self.settings_widget_index = 0
            elif key == pygame.K_DOWN:
                self.settings_category_index = min(
                    len(self.settings_widgets) - 1, self.settings_category_index + 1
                )
                self.settings_widget_index = 0
            elif key == pygame.K_LEFT:
                self.focus_area = "SIDEBAR"
            elif key == pygame.K_RIGHT:
                if self.settings_widgets[self.settings_category_index]:
                    self.focus_area = "SETTINGS_WIDGETS"
                    self.settings_widget_index = 0
            return

        if self.focus_area == "SETTINGS_WIDGETS":
            widgets = self.settings_widgets[self.settings_category_index]
            if not widgets:
                self.focus_area = "SETTINGS_CATS"
                return
            if key == pygame.K_UP:
                if self.settings_widget_index == 0:
                    self.focus_area = "SETTINGS_CATS"
                else:
                    self.settings_widget_index -= 1
            elif key == pygame.K_DOWN:
                self.settings_widget_index = min(
                    len(widgets) - 1, self.settings_widget_index + 1
                )
            else:
                # K_LEFT / K_RIGHT délégués au widget courant
                widgets[self.settings_widget_index].handle_key(key)
            return

    def handle_enter(self, key: int) -> None:
        if self.current_view == "GAMES":
            self.lancer_jeu()
        elif self.current_view == "SETTINGS" and self.focus_area == "SETTINGS_WIDGETS":
            widgets = self.settings_widgets[self.settings_category_index]
            if widgets and 0 <= self.settings_widget_index < len(widgets):
                widgets[self.settings_widget_index].handle_key(key)

    # ============================================================
    # SOURIS / CLICS
    # ============================================================
    def check_click(self, pos: tuple[int, int]) -> None:
        if self.rect_sidebar.collidepoint(pos):
            self.handle_sidebar_click(pos)
            return

        if self.rect_list_area.collidepoint(pos) and self.current_view == "GAMES":
            rel_y = pos[1] - self.rect_list_area.y + self.scroll_y - PADDING
            idx = int(rel_y // (self.item_height + self.item_margin))
            if 0 <= idx < len(self.games_list_by_platform):
                self.selected_index = idx
                return

        if self.current_view == "GAMES":
            cx = self.rect_detail_area.centerx
            cy = self.h_ecran - 100
            btn_rect = pygame.Rect(0, 0, 220, 60)
            btn_rect.center = (cx, cy)
            if btn_rect.collidepoint(pos):
                self.lancer_jeu()

    def handle_sidebar_click(self, pos: tuple[int, int]) -> None:
        for rect, char, idx in self.sidebar.icon_rects:
            if rect.collidepoint(pos):
                self.sidebar.selected_index = idx
                self.current_view = self.sidebar.routes.get(char, "GAMES")
                self.focus_area = "SIDEBAR"
                return

    # ============================================================
    # LANCEMENT JEU
    # ============================================================
    def lancer_jeu(self) -> None:
        if not self.games_list_by_platform:
            return
        if not (0 <= self.selected_index < len(self.games_list_by_platform)):
            logger.warning(
                "selected_index=%d hors bornes (taille=%d)",
                self.selected_index,
                len(self.games_list_by_platform),
            )
            return

        game = self.games_list_by_platform[self.selected_index]

        overlay = pygame.Surface((self.w_ecran, self.h_ecran))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        self.ecran.blit(overlay, (0, 0))

        msg = utils.FONT_TITLE.render("LANCEMENT...", True, utils.C_ACCENT)
        self.ecran.blit(
            msg, msg.get_rect(center=(self.w_ecran // 2, self.h_ecran // 2))
        )
        pygame.display.flip()
        pygame.time.wait(500)

        launcher.launch_game(game)
        # RetroArch peut avoir cassé le contexte fullscreen → on réinitialise
        pygame.display.set_mode(
            (self.w_ecran, self.h_ecran),
            pygame.FULLSCREEN | pygame.DOUBLEBUF,
        )

    # ============================================================
    # JEUX / TABS
    # ============================================================
    def refresh_games_for_selected_tab(self) -> None:
        """Recalcule games_list_by_platform uniquement si le tab a changé."""
        if not self.topbar.tabs:
            self.games_list_by_platform = []
            return
        if self._last_tab_index == self.topbar.selected_tab:
            return
        platform_key = self.topbar.tabs[self.topbar.selected_tab]
        self.games_list_by_platform = [
            g for g in self.games_list
            if g.get("platform", "").upper() == platform_key.upper()
        ]
        self._last_tab_index = self.topbar.selected_tab
        if self.selected_index >= len(self.games_list_by_platform):
            self.selected_index = 0

    # ============================================================
    # SETTINGS — construction des widgets + callbacks
    # ============================================================
    def _build_settings_widgets(self) -> List[List[Widget]]:
        # Trouve l'index correspondant à la couleur actuelle (sinon 0)
        current_accent = self._user_settings.get("accent_color", [255, 107, 0])
        accent_idx = 0
        for i, (_name, rgb) in enumerate(ACCENT_OPTIONS):
            if list(rgb) == list(current_accent):
                accent_idx = i
                break

        assert len(SETTINGS_CATEGORIES) == 4  # garde-fou : matrice et catégories alignées

        return [
            # AUDIO
            [
                Slider("Volume général", self.volume, 0, 100, 5, self._on_volume_change),
                Toggle("Musique d'ambiance", self.music_enabled, self._on_music_toggle),
            ],
            # AFFICHAGE
            [
                Choice("Couleur d'accent", ACCENT_OPTIONS, accent_idx,
                       self._on_accent_change),
                Toggle("Afficher FPS", self.show_fps, self._on_fps_toggle),
            ],
            # CONTROLES
            [
                InfoLine("État manette", self._gamepad_status),
                InfoLine("Nombre de manettes", lambda: str(pygame.joystick.get_count())),
            ],
            # SYSTEME
            [
                Button("Scanner les ROMs (recharger JSON)", self._scan_roms),
                InfoLine("Jeux chargés", lambda: str(len(self.games_list))),
                InfoLine("RetroArch", lambda: config.get_path("retroarch_exe")),
                InfoLine("Cores", lambda: config.get_path("cores_dir")),
                Button("Quitter vers l'OS", self._quit_app),
            ],
        ]

    def _save_settings(self) -> None:
        self._user_settings.update({
            "volume": self.volume,
            "music_enabled": self.music_enabled,
            "show_fps": self.show_fps,
            # accent_color est mis à jour dans _on_accent_change
        })
        try:
            config.save_user_settings(self._user_settings)
        except OSError as e:
            logger.error("Sauvegarde des paramètres échouée : %s", e)

    def _on_volume_change(self, value: int) -> None:
        self.volume = value
        if self.music_loaded:
            pygame.mixer.music.set_volume(value / 100.0)
        self._save_settings()

    def _on_music_toggle(self, enabled: bool) -> None:
        self.music_enabled = enabled
        if self.music_loaded:
            if enabled:
                pygame.mixer.music.play(loops=-1)
            else:
                pygame.mixer.music.pause()
        elif enabled:
            logger.info("Toggle musique ON sans fichier audio chargé.")
        self._save_settings()

    def _on_accent_change(self, index: int) -> None:
        _name, color = ACCENT_OPTIONS[index]
        # Application live : on mute les attributs du module utils,
        # tous les sites qui font `utils.C_ACCENT` voient le changement au prochain frame.
        utils.C_ACCENT = tuple(int(c) for c in color)
        utils.C_ACCENT_HOVER = tuple(min(255, int(c) + 50) for c in color)
        self._user_settings["accent_color"] = list(color)
        self._save_settings()
        logger.info("Couleur d'accent changée : %s", _name)

    def _on_fps_toggle(self, enabled: bool) -> None:
        self.show_fps = enabled
        self._save_settings()

    def _gamepad_status(self) -> str:
        try:
            count = pygame.joystick.get_count()
            if count == 0:
                return "Non connectée"
            joy = pygame.joystick.Joystick(0)
            if not joy.get_init():
                joy.init()
            return joy.get_name()
        except pygame.error:
            return "Erreur"

    def _scan_roms(self) -> None:
        logger.info("Rechargement de data_game.json …")
        self.games_list = game_scanner.load_games_data()
        platforms_with_games = {
            g.get("platform", "").upper() for g in self.games_list
        }
        new_tabs = [
            t for t in config.get_all_core_keys()
            if t.upper() in platforms_with_games
        ]
        self.topbar.tabs = new_tabs
        if self.topbar.selected_tab >= len(new_tabs):
            self.topbar.selected_tab = 0
        self._last_tab_index = None  # force le refiltrage
        self.refresh_games_for_selected_tab()

    def _quit_app(self) -> None:
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    # ============================================================
    # RENDU GLOBAL
    # ============================================================
    def draw_shell(self, time_str: str) -> None:
        self.sidebar.focus = self.focus_area == "SIDEBAR"
        self.topbar.focus = self.focus_area == "TOPBAR"
        self.sidebar.draw(self)
        self.topbar.draw(self.ecran, self.current_view, time_str)

    def draw(self, time_str: str, mouse_pos: tuple[int, int]) -> None:
        self.ecran.fill(C_BG_PRIMARY)
        self.ecran.set_clip(None)

        self.draw_shell(time_str)

        if self.current_view == "HOME":
            draw_home_view(self)
        elif self.current_view == "GAMES":
            self.refresh_games_for_selected_tab()
            draw_games_view(self, mouse_pos)
        elif self.current_view == "SETTINGS":
            draw_settings_view(self)
        elif self.current_view == "PROFILE":
            draw_profile_view(self)

        if self.show_fps:
            fps = int(self.clock.get_fps())
            fps_txt = utils.FONT_BOLD.render(f"{fps} FPS", True, (0, 255, 0))
            self.ecran.blit(fps_txt, (10, self.h_ecran - fps_txt.get_height() - 8))
