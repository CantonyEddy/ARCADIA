# borne_app/interface.py
import pygame
import sys
import os

# Imports relatifs (car on est dans le package borne_app)
from . import game_scanner
from . import launcher

# --- CONSTANTES DE DESIGN ---
COULEUR_FOND = (20, 20, 20)
COULEUR_BOUTON = (50, 50, 50)
COULEUR_BOUTON_HOVER = (0, 120, 215)
COULEUR_TEXTE = (255, 255, 255)
LARGEUR_BOUTON = 800
HAUTEUR_BOUTON = 80
MARGE = 10
POS_Y_DEPART = 150

class BorneInterface:
    def __init__(self):
        # Initialisation de Pygame
        pygame.init()
        
        # Configuration Écran
        info_ecran = pygame.display.Info()
        self.largeur_ecran = info_ecran.current_w
        self.hauteur_ecran = info_ecran.current_h
        
        # Création de la fenêtre
        self.ecran = pygame.display.set_mode(
            (self.largeur_ecran, self.hauteur_ecran), 
            pygame.FULLSCREEN | pygame.DOUBLEBUF
        )
        pygame.display.set_caption("Borne Arcade")
        
        # Polices
        self.font_titre = pygame.font.SysFont("Arial", 50, bold=True)
        self.font_bouton = pygame.font.SysFont("Arial", 28)
        
        # Chargement des données (via vos modules existants)
        self.games_list = game_scanner.scan_roms()
        
        # Scroll
        self.scroll_y = 0
        hauteur_totale = len(self.games_list) * (HAUTEUR_BOUTON + MARGE)
        self.max_scroll = max(0, hauteur_totale - (self.hauteur_ecran - POS_Y_DEPART))

    def lancer_jeu(self, game_data):
        """Affiche un écran de chargement et lance le jeu"""
        self.ecran.fill((0, 0, 0))
        msg = self.font_titre.render(f"LANCEMENT DE {game_data['name']}...", True, COULEUR_TEXTE)
        rect = msg.get_rect(center=(self.largeur_ecran//2, self.hauteur_ecran//2))
        self.ecran.blit(msg, rect)
        pygame.display.flip()
        
        # Appel du launcher existant
        launcher.launch_game(game_data)
        
        # Restauration de l'affichage au retour
        pygame.display.set_mode((self.largeur_ecran, self.hauteur_ecran), pygame.FULLSCREEN | pygame.DOUBLEBUF)

    def run(self):
        """Boucle principale du jeu"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            souris_pos = pygame.mouse.get_pos()
            
            # 1. Événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEWHEEL:
                    self.scroll_y -= event.y * 20
                    # Clamp (limiter le scroll)
                    self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.check_click(souris_pos)

            # 2. Dessin
            self.draw(souris_pos)
            
            # 3. Update
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()

    def check_click(self, souris_pos):
        """Vérifie si on clique sur un bouton"""
        for i, game in enumerate(self.games_list):
            y_pos = POS_Y_DEPART + i * (HAUTEUR_BOUTON + MARGE) - self.scroll_y
            if -HAUTEUR_BOUTON < y_pos < self.hauteur_ecran:
                rect = pygame.Rect((self.largeur_ecran - LARGEUR_BOUTON) // 2, y_pos, LARGEUR_BOUTON, HAUTEUR_BOUTON)
                if rect.collidepoint(souris_pos):
                    self.lancer_jeu(game)
                    return

    def draw(self, souris_pos):
        """Gère tout l'affichage"""
        self.ecran.fill(COULEUR_FOND)
        
        # Titre
        titre = self.font_titre.render("CHOISISSEZ VOTRE JEU", True, COULEUR_TEXTE)
        self.ecran.blit(titre, titre.get_rect(center=(self.largeur_ecran // 2, 60)))
        
        # Liste
        for i, game in enumerate(self.games_list):
            y_pos = POS_Y_DEPART + i * (HAUTEUR_BOUTON + MARGE) - self.scroll_y
            
            # Optimisation: ne dessiner que ce qui est visible
            if -HAUTEUR_BOUTON < y_pos < self.hauteur_ecran:
                rect = pygame.Rect((self.largeur_ecran - LARGEUR_BOUTON) // 2, y_pos, LARGEUR_BOUTON, HAUTEUR_BOUTON)
                color = COULEUR_BOUTON_HOVER if rect.collidepoint(souris_pos) else COULEUR_BOUTON
                
                pygame.draw.rect(self.ecran, color, rect, border_radius=10)
                
                txt = self.font_bouton.render(f"[{game['system']}] - {game['name']}", True, COULEUR_TEXTE)
                self.ecran.blit(txt, txt.get_rect(center=rect.center))