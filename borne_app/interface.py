import pygame
import sys
import datetime
from . import game_scanner
from . import launcher
from . import config

# --- PALETTE DE COULEURS (Basée sur votre front.html) ---
# Fonds
C_BG_PRIMARY = (24, 24, 24)     # #181818 (Fond global)
C_BG_SECONDARY = (37, 37, 37)   # #252525 (Panneaux, Sidebar)
C_BG_TERTIARY = (48, 48, 48)    # #303030 (Survol / Sélection fond)

# Accent (Orange Néon style Nuxt)
C_ACCENT = (255, 107, 0)        # #ff6b00 (Orange Vif)
C_ACCENT_HOVER = (255, 158, 0)  # Orange plus clair pour les boutons

# Textes
C_TXT_PRI = (255, 255, 255)     # Blanc
C_TXT_SEC = (160, 160, 160)     # #a0a0a0 (Gris clair)

# --- DIMENSIONS ---
W_SIDEBAR = 90
H_TOPBAR = 80
PADDING = 20
RADIUS = 12                     # Coins arrondis

class BorneInterface:
    def __init__(self):
        pygame.init()
        
        # Configuration Écran
        info = pygame.display.Info()
        self.w_ecran = info.current_w
        self.h_ecran = info.current_h
        
        self.ecran = pygame.display.set_mode(
            (self.w_ecran, self.h_ecran), 
            pygame.FULLSCREEN | pygame.DOUBLEBUF
        )
        pygame.display.set_caption("Arcade Dashboard")
        
        # --- POLICES ---
        # On tente de charger des polices modernes
        fonts = ["Segoe UI", "Verdana", "Arial"]
        self.font_sml = pygame.font.SysFont(fonts, 16)
        self.font_reg = pygame.font.SysFont(fonts, 20)
        self.font_bold = pygame.font.SysFont(fonts, 24, bold=True)
        self.font_title = pygame.font.SysFont(fonts, 40, bold=True) # Gros titre détails
        self.font_time = pygame.font.SysFont("Consolas", 24, bold=True)

        # Données
        self.games_list = game_scanner.load_games_data()
        self.games_list_by_platform = {}
        self.tabs = config.get_all_core_keys()
        self.selected_index = 0
        self.selected_tab = 0
        self.scroll_y = 0
        
        # Calcul des zones
        self.rect_sidebar = pygame.Rect(0, 0, W_SIDEBAR, self.h_ecran)
        self.rect_topbar = pygame.Rect(W_SIDEBAR, 0, self.w_ecran - W_SIDEBAR, H_TOPBAR)
        
        # Zone de contenu (Sous la topbar, à droite de la sidebar)
        self.w_content_area = self.w_ecran - W_SIDEBAR
        self.h_content_area = self.h_ecran - H_TOPBAR
        
        # Division Liste (40%) / Détail (60%)
        self.w_list_panel = int(self.w_content_area * 0.4)
        self.w_detail_panel = self.w_content_area - self.w_list_panel
        
        self.rect_list_area = pygame.Rect(W_SIDEBAR, H_TOPBAR, self.w_list_panel, self.h_content_area)
        self.rect_detail_area = pygame.Rect(W_SIDEBAR + self.w_list_panel, H_TOPBAR, self.w_detail_panel, self.h_content_area)
        
        # Hauteur d'un item dans la liste
        self.item_height = 80
        self.item_margin = 15

        self.texture_cache = {}

    def get_cached_image(self, path, size, color_override=None):
        """
        Récupère une image depuis le cache ou la charge si nécessaire.
        path: chemin du fichier
        size: tuple (largeur, hauteur)
        color_override: couleur à appliquer (pour tes icônes sidebar)
        """
        # On crée une clé unique pour cette demande
        key = (path, size, color_override)
        
        if key not in self.texture_cache:
            # SI l'image n'est pas connue, on fait le travail lourd (UNE SEULE FOIS)
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, size)
                
                # Gestion couleur (pour tes icônes sidebar)
                if color_override:
                    img.fill(color_override, special_flags=pygame.BLEND_RGBA_MULT)
                    
                self.texture_cache[key] = img
            except Exception as e:
                # En cas d'erreur (fichier manquant), on retourne un carré vide pour ne pas planter
                print(f"Erreur chargement {path}: {e}")
                fallback = pygame.Surface(size)
                fallback.fill((255, 0, 255)) # Magenta moche pour voir l'erreur
                self.texture_cache[key] = fallback

        return self.texture_cache[key]
    
    def clear_cache(self):
        self.texture_cache = {}

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # Gestion du temps
            now = datetime.datetime.now()
            time_str = now.strftime("%H:%M")
            mouse_pos = pygame.mouse.get_pos()
            
            # --- EVENTS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: running = False
                    
                    # Navigation Liste
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = min(len(self.games_list_by_platform)-1, self.selected_index + 1)
                        self.ajuster_scroll()
                    elif event.key == pygame.K_UP:
                        self.selected_index = max(0, self.selected_index - 1)
                        self.ajuster_scroll()

                    # Navigation Tabs
                    elif event.key == pygame.K_LEFT:
                        self.selected_tab = max(0, self.selected_tab - 1)
                        self.selected_index = 0
                        self.ajuster_scroll()
                    elif event.key == pygame.K_RIGHT:
                        self.selected_tab = min(len(self.tabs) - 1, self.selected_tab + 1)
                        self.selected_index = 0
                        self.ajuster_scroll()

                    # Lancer jeu
                    elif event.key == pygame.K_RETURN:
                        self.lancer_jeu()
                        
                elif event.type == pygame.MOUSEWHEEL:
                    self.scroll_y -= event.y * 30
                    self.limiter_scroll()
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: self.check_click(mouse_pos)

            # --- DESSIN ---
            self.draw(time_str, mouse_pos)
            pygame.display.flip()
            clock.tick(60)
            
        pygame.quit()
        sys.exit()

    # --- LOGIQUE ---
    def ajuster_scroll(self):
        # Garde l'élément sélectionné visible
        y_pos = self.selected_index * (self.item_height + self.item_margin) + PADDING
        
        # Si caché en haut
        if y_pos < self.scroll_y:
            self.scroll_y = y_pos - PADDING
        # Si caché en bas
        elif y_pos + self.item_height > self.scroll_y + self.rect_list_area.height:
            self.scroll_y = y_pos + self.item_height + PADDING - self.rect_list_area.height

    def limiter_scroll(self):
        content_h = len(self.games_list_by_platform) * (self.item_height + self.item_margin) + PADDING
        max_s = max(0, content_h - self.rect_list_area.height)
        self.scroll_y = max(0, min(self.scroll_y, max_s))

    def check_click(self, pos):
        # Clic dans la liste ?
        if self.rect_list_area.collidepoint(pos):
            rel_y = pos[1] - self.rect_list_area.y + self.scroll_y - PADDING
            idx = int(rel_y // (self.item_height + self.item_margin))
            if 0 <= idx < len(self.games_list_by_platform):
                self.selected_index = idx
        
        # Clic Bouton Jouer ? (Détection approximative zone bouton)
        # Centre du panneau détail
        cx = self.rect_detail_area.centerx
        cy = self.h_ecran - 100
        btn_rect = pygame.Rect(0, 0, 220, 60)
        btn_rect.center = (cx, cy)
        
        if btn_rect.collidepoint(pos):
            self.lancer_jeu()

    def lancer_jeu(self):
        if not self.games_list_by_platform: return
        game = self.games_list_by_platform[self.selected_index]
        
        # Effet visuel simple au lancement
        overlay = pygame.Surface((self.w_ecran, self.h_ecran))
        overlay.fill((0,0,0))
        overlay.set_alpha(200)
        self.ecran.blit(overlay, (0,0))
        
        msg = self.font_title.render("LANCEMENT...", True, C_ACCENT)
        self.ecran.blit(msg, msg.get_rect(center=(self.w_ecran//2, self.h_ecran//2)))
        pygame.display.flip()
        pygame.time.wait(500)
        
        launcher.launch_game(game)
        pygame.display.set_mode((self.w_ecran, self.h_ecran), pygame.FULLSCREEN | pygame.DOUBLEBUF)

    def get_games_for_selected_tab(self):
        platform_key = self.tabs[self.selected_tab]
        self.games_list_by_platform = [g for g in self.games_list if g['platform'].upper() == platform_key.upper()]

    # --- RENDU GRAPHIQUE ---
    def draw(self, time_str, mouse_pos):
        self.ecran.fill(C_BG_PRIMARY)

        # 1. SIDEBAR (Gauche)
        pygame.draw.rect(self.ecran, C_BG_SECONDARY, self.rect_sidebar)
        # Ligne de séparation droite
        pygame.draw.line(self.ecran, (60,60,60), (W_SIDEBAR, 0), (W_SIDEBAR, self.h_ecran))
        
        # Icônes Sidebar (Simulation Texte)
        icons = ["A", "H", "G", "S"] # Avatar, Home, Game, Settings
        y_icon = 50
        for i, char in enumerate(icons):
            color = C_ACCENT if i == 1 else C_TXT_SEC # Home actif
            if i == 0: # Avatar rond
                pygame.draw.circle(self.ecran, C_BG_TERTIARY, (W_SIDEBAR//2, y_icon), 20)
            else:
                icon_path = config.get_icon_path(char)
                # On utilise notre cache, en passant la couleur C_ACCENT
                lbl_icon = self.get_cached_image(icon_path, (30, 30), color_override=C_ACCENT)
                self.ecran.blit(lbl_icon, lbl_icon.get_rect(center=(W_SIDEBAR//2, y_icon)))
            y_icon += 80

        # 2. TOPBAR (Haut)
        pygame.draw.rect(self.ecran, C_BG_SECONDARY, self.rect_topbar)
        pygame.draw.line(self.ecran, (60,60,60), (W_SIDEBAR, H_TOPBAR), (self.w_ecran, H_TOPBAR))
        
        # Onglets (Tabs)
        tabs = self.tabs.copy()
        x_tab = W_SIDEBAR + 40
        for tab in tabs:
            is_active = (tab == tabs[self.selected_tab])
            bg_color = C_ACCENT if is_active else C_BG_SECONDARY
            txt_color = C_TXT_PRI if is_active else C_TXT_SEC
            
            # Pill shape background
            txt_surf = self.font_bold.render(tab, True, txt_color)
            w_pill = txt_surf.get_width() + 40
            rect_pill = pygame.Rect(x_tab, (H_TOPBAR - 40)//2, w_pill, 40)
            
            if is_active:
                pygame.draw.rect(self.ecran, bg_color, rect_pill, border_radius=20)
                # Petit glow orange
                s = pygame.Surface((w_pill+10, 50), pygame.SRCALPHA)
                pygame.draw.rect(s, (*C_ACCENT, 50), (5,5,w_pill,40), border_radius=20)
                self.ecran.blit(s, (rect_pill.x-5, rect_pill.y-5))
            
            self.ecran.blit(txt_surf, txt_surf.get_rect(center=rect_pill.center))
            x_tab += w_pill + 20
            
        # Heure
        txt_time = self.font_time.render(time_str, True, C_TXT_SEC)
        self.ecran.blit(txt_time, (self.w_ecran - 100, (H_TOPBAR - txt_time.get_height())//2))

        # 3. LISTE DES JEUX (Gauche)
        # Clip pour le scroll
        self.ecran.set_clip(self.rect_list_area)
        self.get_games_for_selected_tab()
        
        start_y = self.rect_list_area.y + PADDING - self.scroll_y
        
        for i, game in enumerate(self.games_list_by_platform):
            y = start_y + i * (self.item_height + self.item_margin)
            
            # Optimisation affichage
            if y + self.item_height < 0 or y > self.h_ecran: continue
            
            # Zone de la carte
            rect_item = pygame.Rect(W_SIDEBAR + PADDING, y, self.w_list_panel - (PADDING*2), self.item_height)
            is_sel = (i == self.selected_index)
            
            # Fond Carte
            bg_col = C_BG_TERTIARY if is_sel else C_BG_SECONDARY
            pygame.draw.rect(self.ecran, bg_col, rect_item, border_radius=RADIUS)
            
            # Si sélectionné : Bordure Orange + Glow
            if is_sel:
                pygame.draw.rect(self.ecran, C_ACCENT, rect_item, width=2, border_radius=RADIUS)
                # Effet barre verticale gauche
                pygame.draw.rect(self.ecran, C_ACCENT, (rect_item.x, rect_item.y + 10, 6, rect_item.height - 20), border_radius=3)

            # Thumbnail carré
            rect_thumb = pygame.Rect(rect_item.x + 10, rect_item.y + 10, 60, 60)
            rect_thumb_img = self.get_cached_image(game['cover'], (60, 60))
            self.ecran.blit(rect_thumb_img, rect_thumb)
            pygame.draw.rect(self.ecran, (54,20,98), rect_thumb, border_radius=8)
            self.ecran.blit(rect_thumb_img, rect_thumb)
            
            # Textes
            title_color = C_TXT_PRI if is_sel else C_TXT_SEC
            txt_name = self.font_bold.render(game['name'], True, title_color)
            txt_sys = self.font_sml.render(f"[{game['platform']}]", True, C_ACCENT if is_sel else (100,100,100))
            
            self.ecran.blit(txt_name, (rect_item.x + 85, rect_item.y + 15))
            self.ecran.blit(txt_sys, (rect_item.x + 85, rect_item.y + 45))

        self.ecran.set_clip(None)

        # 4. DETAIL PANEL (Droite)
        # Fond du panel (légèrement plus clair que le fond global)
        # Pour faire joli, on peut dessiner un grand rectangle arrondi
        rect_panel_bg = self.rect_detail_area.inflate(-40, -40)
        pygame.draw.rect(self.ecran, C_BG_SECONDARY, rect_panel_bg, border_radius=RADIUS)
        
        if self.games_list_by_platform:
            game = self.games_list_by_platform[self.selected_index]
            cx = rect_panel_bg.centerx
            
            # Grande Image (Carré)
            rect_img_big = pygame.Rect(0, 0, 300, 300)
            rect_img_big.center = (cx, rect_panel_bg.y + 200)

            # Ombre portée (décalée de 10px)
            pygame.draw.rect(self.ecran, (0,0,0), rect_img_big.move(10, 10), border_radius=RADIUS) 

            # Fond gris (au cas où l'image a de la transparence)
            pygame.draw.rect(self.ecran, (50,50,50), rect_img_big, border_radius=RADIUS)

            # --- GESTION DE L'IMAGE ---
            lbl_cover_base = self.get_cached_image(game['cover'], (300, 300))
            lbl_cover = lbl_cover_base.copy()

            # 1. Création du masque (le "pochoir")
            mask = pygame.Surface((300, 300), pygame.SRCALPHA)
            # On dessine un rectangle blanc arrondi sur le masque transparent
            pygame.draw.rect(mask, (255, 255, 255), (0, 0, 300, 300), border_radius=RADIUS)

            # 2. Application du masque sur l'image
            # Note : on ne fait PAS "lbl_cover =", car blit modifie l'image en place !
            lbl_cover.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

            # 3. Affichage final
            self.ecran.blit(lbl_cover, rect_img_big)
            
            # Titre Jeu (Gros Orange)
            txt_big_title = self.font_title.render(game['name'].upper(), True, C_ACCENT)
            # Effet d'ombre texte (Glow fake)
            txt_shadow = self.font_title.render(game['name'].upper(), True, (C_ACCENT[0]//3, C_ACCENT[1]//3, 0))
            self.ecran.blit(txt_shadow, txt_shadow.get_rect(center=(cx+2, rect_panel_bg.y + 400 + 2)))
            self.ecran.blit(txt_big_title, txt_big_title.get_rect(center=(cx, rect_panel_bg.y + 400)))
            
            # Description
            desc_y = rect_panel_bg.y + 460
            lines = [
                f"Système: {game['platform'].upper()}",
                f"{game['resume']}"
            ]
            for line in lines:
                t = self.font_reg.render(line, True, C_TXT_SEC)
                self.ecran.blit(t, t.get_rect(center=(cx, desc_y)))
                desc_y += 30
            
            # Bouton JOUER (Style Nuxt Gradient)
            rect_btn = pygame.Rect(0, 0, 220, 60)
            rect_btn.center = (cx, self.h_ecran - 100)
            
            # Couleur bouton (Hover ou Normal)
            is_hover = rect_btn.collidepoint(mouse_pos)
            col_btn = C_ACCENT_HOVER if is_hover else C_ACCENT
            
            # Ombre bouton
            pygame.draw.rect(self.ecran, (C_ACCENT[0]//2, C_ACCENT[1]//2, 0), rect_btn.move(0, 5), border_radius=30)
            # Corps bouton
            pygame.draw.rect(self.ecran, col_btn, rect_btn, border_radius=30)
            
            lbl_jouer = self.font_bold.render("JOUER", True, C_BG_PRIMARY) # Texte noir/foncé sur bouton orange
            self.ecran.blit(lbl_jouer, lbl_jouer.get_rect(center=rect_btn.center))