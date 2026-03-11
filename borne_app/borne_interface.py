import sys
import datetime
import pygame

from . import game_scanner, launcher, config
from .utils import (
    C_BG_PRIMARY,
    W_SIDEBAR,
    H_TOPBAR,
    PADDING,
    init_fonts,
    ImageCache,
)
from .sidebar import Sidebar
from .topbar import TopBar
from .views.home_view import draw_home_view
from .views.games_view import draw_games_view
from .views.settings_view import draw_settings_view
from .views.profile_view import draw_profile_view


class BorneInterface:
    """
    Classe principale qui orchestre la borne :
    - boucle principale Pygame
    - gestion du focus clavier
    - délégation du rendu à la sidebar, topbar et vues.
    """

    def __init__(self):
        pygame.init()

        # Configuration écran
        info = pygame.display.Info()
        self.w_ecran = info.current_w
        self.h_ecran = info.current_h

        self.ecran = pygame.display.set_mode(
            (self.w_ecran, self.h_ecran),
            pygame.FULLSCREEN | pygame.DOUBLEBUF,
        )
        pygame.display.set_caption("Arcade Dashboard")

        # Polices globales (remplies dans utils.init_fonts)
        init_fonts()

        # Données jeux / plateformes
        self.games_list = game_scanner.load_games_data()
        self.games_list_by_platform = []
        tabs = config.get_all_core_keys()

        # Composants UI
        self.sidebar = Sidebar(self.h_ecran)
        self.topbar = TopBar(self.w_ecran, tabs)

        # Etat de navigation
        self.current_view = "GAMES"  # HOME | GAMES | SETTINGS | PROFILE
        self.focus_area = "TOPBAR"   # "SIDEBAR" | "TOPBAR" | "LIST"

        # Liste de jeux
        self.selected_index = 0
        self.scroll_y = 0

        # Zones de layout
        self.rect_sidebar = pygame.Rect(0, 0, W_SIDEBAR, self.h_ecran)
        self.rect_topbar = pygame.Rect(
            W_SIDEBAR, 0, self.w_ecran - W_SIDEBAR, H_TOPBAR
        )

        self.w_content_area = self.w_ecran - W_SIDEBAR
        self.h_content_area = self.h_ecran - H_TOPBAR

        # Liste (40 %) / Détails (60 %)
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

        # Paramètres liste
        self.item_height = 80
        self.item_margin = 15

        # Cache textures/images
        self.image_cache = ImageCache()

    # --------- BOUCLE PRINCIPALE ----------
    def run(self):
        clock = pygame.time.Clock()
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
                        pygame.K_UP,
                        pygame.K_DOWN,
                        pygame.K_LEFT,
                        pygame.K_RIGHT,
                    ):
                        self.handle_arrow_key(event.key)
                    elif event.key == pygame.K_RETURN:
                        self.lancer_jeu()
                elif event.type == pygame.MOUSEWHEEL:
                    self.scroll_y -= event.y * 30
                    self.limiter_scroll()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.check_click(mouse_pos)

            self.draw(time_str, mouse_pos)
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()

    # --------- LOGIQUE LISTE / SCROLL ----------
    def ajuster_scroll(self):
        y_pos = self.selected_index * (self.item_height + self.item_margin) + PADDING

        if y_pos < self.scroll_y:
            self.scroll_y = y_pos - PADDING
        elif y_pos + self.item_height > self.scroll_y + self.rect_list_area.height:
            self.scroll_y = (
                y_pos + self.item_height + PADDING - self.rect_list_area.height
            )

    def limiter_scroll(self):
        content_h = len(self.games_list_by_platform) * (
            self.item_height + self.item_margin
        ) + PADDING
        max_s = max(0, content_h - self.rect_list_area.height)
        self.scroll_y = max(0, min(self.scroll_y, max_s))

    # --------- NAVIGATION CLAVIER ----------
    def handle_arrow_key(self, key):
        # Navigation verticale
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

        # Navigation horizontale
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
            elif self.focus_area == "LIST" and self.current_view == "GAMES":
                self.focus_area = "TOPBAR"

    # --------- SOURIS / CLICS ----------
    def check_click(self, pos):
        # Sidebar ?
        if self.rect_sidebar.collidepoint(pos):
            self.handle_sidebar_click(pos)
            return

        # Liste de jeux ?
        if self.rect_list_area.collidepoint(pos) and self.current_view == "GAMES":
            rel_y = pos[1] - self.rect_list_area.y + self.scroll_y - PADDING
            idx = int(rel_y // (self.item_height + self.item_margin))
            if 0 <= idx < len(self.games_list_by_platform):
                self.selected_index = idx
                return

        # Bouton jouer ?
        cx = self.rect_detail_area.centerx
        cy = self.h_ecran - 100
        btn_rect = pygame.Rect(0, 0, 220, 60)
        btn_rect.center = (cx, cy)
        if btn_rect.collidepoint(pos):
            self.lancer_jeu()

    def handle_sidebar_click(self, pos):
        for rect, char, idx in self.sidebar.icon_rects:
            if rect.collidepoint(pos):
                self.sidebar.selected_index = idx
                self.current_view = self.sidebar.routes.get(char, "GAMES")
                self.focus_area = "SIDEBAR"
                return

    # --------- LANCEMENT JEU ----------
    def lancer_jeu(self):
        if not self.games_list_by_platform:
            return

        game = self.games_list_by_platform[self.selected_index]

        overlay = pygame.Surface((self.w_ecran, self.h_ecran))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        self.ecran.blit(overlay, (0, 0))

        # Texte simple de lancement
        font = pygame.font.SysFont(["Segoe UI", "Verdana", "Arial"], 40, bold=True)
        msg = font.render("LANCEMENT...", True, (255, 107, 0))
        self.ecran.blit(msg, msg.get_rect(center=(self.w_ecran // 2, self.h_ecran // 2)))
        pygame.display.flip()
        pygame.time.wait(500)

        launcher.launch_game(game)
        pygame.display.set_mode(
            (self.w_ecran, self.h_ecran),
            pygame.FULLSCREEN | pygame.DOUBLEBUF,
        )

    # --------- UTILS JEUX / TABS ----------
    def get_games_for_selected_tab(self):
        platform_key = self.topbar.tabs[self.topbar.selected_tab]
        self.games_list_by_platform = [
            g
            for g in self.games_list
            if g["platform"].upper() == platform_key.upper()
        ]

    # --------- RENDU GLOBAL ----------
    def draw_shell(self, time_str):
        # Met à jour le focus visuel des composants
        self.sidebar.focus = self.focus_area == "SIDEBAR"
        self.topbar.focus = self.focus_area == "TOPBAR"

        self.sidebar.draw(self)
        self.topbar.draw(self.ecran, self.current_view, time_str)

    def draw(self, time_str, mouse_pos):
        self.ecran.fill(C_BG_PRIMARY)
        self.ecran.set_clip(None)

        self.draw_shell(time_str)

        # Contenu principal (vues)
        if self.current_view == "HOME":
            draw_home_view(self)
        elif self.current_view == "GAMES":
            self.get_games_for_selected_tab()
            draw_games_view(self, mouse_pos)
        elif self.current_view == "SETTINGS":
            draw_settings_view(self)
        elif self.current_view == "PROFILE":
            draw_profile_view(self)


