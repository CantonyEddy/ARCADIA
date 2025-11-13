# borne_app/launcher.py
import subprocess
import platform
import os
from . import config

def launch_game(game_data):
    """Lance un jeu en utilisant les infos de game_data."""
    
    # --- DEBUG 1: Qu'est-ce que je reçois ? ---
    print("\n--- DEBUG (launcher.py) ---")
    print(f"Données reçues : {game_data}")
    print("------------------------------\n")
    
    try:
        # 1. Récupère les chemins de base
        retroarch_cmd = config.get_path('retroarch_exe')
        cores_dir = config.get_path('cores_dir')
        
        # 2. Construit le nom complet du core
        core_name = game_data['core_name'] # Doit être "snes9x_libretro", etc.
        core_ext = ".dll" if platform.system() == "Windows" else ".so"
        core_path = os.path.join(cores_dir, f"{core_name}{core_ext}")
        
        # 3. Récupère le chemin de la ROM
        rom_path = game_data['rom_path']
        
        # --- DEBUG 2: Quels sont les chemins finaux ? ---
        print("--- DEBUG (launcher.py) ---")
        print(f"Chemin RetroArch : {retroarch_cmd}")
        print(f"Chemin Cores Dir : {cores_dir}")
        print(f"Nom Core : {core_name}")
        print(f"Chemin Core FINAL : {core_path}")
        print(f"Chemin ROM FINAL : {rom_path}")
        print("------------------------------\n")

        print("Le frontend (Kivy) est en pause...")
        
        commande = [retroarch_cmd, "-L", core_path, rom_path]
        
        # --- DEBUG 3: Quelle est la commande exacte ? ---
        print(f"COMMANDE ENVOYÉE : {' '.join(commande)}")
        
        # On utilise check=True pour que ça lève une erreur si ça échoue
        subprocess.run(commande, check=True)
    
    except KeyError as e:
        # --- DEBUG 4: Erreur si 'core_name' n'existe pas ---
        print(f"!!!!! ERREUR FATALE (launcher.py) !!!!!")
        print(f"La clé {e} n'a pas été trouvée dans game_data.")
        print("Vérifie que 'game_scanner.py' envoie bien 'core_name'.")
        print("-------------------------------------------\n")

    except Exception as e:
        # --- DEBUG 5: Attrape TOUTES les autres erreurs ---
        print(f"!!!!! ERREUR FATALE (launcher.py) !!!!!")
        print(f"Échec du lancement. Erreur : {e}")
        print("Vérifie les points suivants :")
        print("1. Tous les chemins dans 'config.ini' sont-ils PARFAITS ? (pas de fautes de frappe)")
        print(f"2. Le fichier '{retroarch_cmd}' existe-t-il VRAIMENT ?")
        print(f"3. Le fichier '{core_path}' existe-t-il VRAIMENT ?")
        print(f"4. Le fichier '{rom_path}' existe-t-il VRAIMENT ?")
        print("-------------------------------------------\n")
    
    print("\n---------------------------------")
    print("RetroArch est fermé (ou n'a pas pu se lancer).")
    print("Retour au frontend.")
    print("---------------------------------\n")