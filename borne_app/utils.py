import pygame

# --- PALETTE DE COULEURS ---
# Fonds
C_BG_PRIMARY = (24, 24, 24)      # #181818 (Fond global)
C_BG_SECONDARY = (37, 37, 37)    # #252525 (Panneaux, Sidebar)
C_BG_TERTIARY = (48, 48, 48)     # #303030 (Survol / Sélection fond)

# Accent
C_ACCENT = (255, 107, 0)         # #ff6b00 (Orange vif)
C_ACCENT_HOVER = (255, 158, 0)   # Orange plus clair

# Textes
C_TXT_PRI = (255, 255, 255)      # Blanc
C_TXT_SEC = (160, 160, 160)      # Gris clair

# --- DIMENSIONS ---
W_SIDEBAR = 90
H_TOPBAR = 80
PADDING = 20
RADIUS = 12                      # Coins arrondis


# --- POLICES (remplies dynamiquement après pygame.init) ---
FONT_SMALL = None
FONT_REG = None
FONT_BOLD = None
FONT_TITLE = None
FONT_TIME = None


def init_fonts():
    """
    Initialise les polices globales du module.
    A appeler APRÈS pygame.init().
    """
    global FONT_SMALL, FONT_REG, FONT_BOLD, FONT_TITLE, FONT_TIME

    fonts = ["Segoe UI", "Verdana", "Arial"]
    FONT_SMALL = pygame.font.SysFont(fonts, 16)
    FONT_REG = pygame.font.SysFont(fonts, 20)
    FONT_BOLD = pygame.font.SysFont(fonts, 24, bold=True)
    FONT_TITLE = pygame.font.SysFont(fonts, 40, bold=True)
    FONT_TIME = pygame.font.SysFont("Consolas", 24, bold=True)


class ImageCache:
    """
    Petit cache d'images pour éviter de recharger les textures à chaque frame.
    """

    def __init__(self):
        self._cache = {}

    def clear(self):
        self._cache = {}

    def get(self, path, size, color_override=None):
        key = (path, size, color_override)

        if key not in self._cache:
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, size)

                if color_override:
                    img.fill(color_override, special_flags=pygame.BLEND_RGBA_MULT)

                self._cache[key] = img
            except Exception as e:
                print(f"Erreur chargement {path}: {e}")
                fallback = pygame.Surface(size)
                fallback.fill((255, 0, 255))
                self._cache[key] = fallback

        return self._cache[key]