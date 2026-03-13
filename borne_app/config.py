# borne_app/config.py
import configparser
import platform
import os
import json

# On trouve le chemin du fichier .ini (il est à la racine, un niveau au-dessus)
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config.ini')

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# Détecte l'OS pour utiliser la bonne section [Paths_...]
current_os = platform.system()
PATH_SECTION = 'Paths_Windows' if current_os == 'Windows' else 'Paths_Linux'

# --- Fonctions pour accéder à la config ---

def get_path(key):
    """Cherche uniquement dans [Paths_Windows] ou [Paths_Linux]"""
    return config.get(PATH_SECTION, key)

def load_json(file_path):
    """Charge un fichier JSON et retourne les données."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_core_map(key):
    # Le 'libretro.dll' ou '.so' sera ajouté par le launcher
    return config.get('CoreMap', key)

def get_all_core_keys():
    """Retourne une liste de toutes les clés dans la section [CoreMap]."""
    return config.options('CoreMap')

def get_icon_path(key):
    """Récupère le chemin d'une icône depuis la section [icons]"""
    return config.get('icons', key)

def get_rom_extensions():
    """Cherche uniquement dans [Settings]"""
    ext_string = config.get('Settings', 'rom_extensions')
    return tuple(ext.strip() for ext in ext_string.split(','))