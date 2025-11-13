# borne_app/config.py
import configparser
import platform
import os

# On trouve le chemin du fichier .ini (il est à la racine, un niveau au-dessus)
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config.ini')

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# Détecte l'OS pour utiliser la bonne section [Paths_...]
current_os = platform.system()
PATH_SECTION = 'Paths_Windows' if current_os == 'Windows' else 'Paths_Linux'

# --- Fonctions pour accéder à la config ---

def get_path(key):
    """Récupère un chemin depuis la section [Paths_...]"""
    return config.get(PATH_SECTION, key)

def get_core_map():
    """Retourne la map des cores sous forme de dictionnaire"""
    # Le 'libretro.dll' ou '.so' sera ajouté par le launcher
    return dict(config.items('CoreMap'))

def get_rom_extensions():
    """Retourne un tuple des extensions de ROMs valides"""
    ext_string = config.get('Settings', 'rom_extensions')
    return tuple(ext.strip() for ext in ext_string.split(','))