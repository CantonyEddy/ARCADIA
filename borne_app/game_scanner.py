# borne_app/game_scanner.py
import os
from . import config  # Importe notre module config.py

def scan_roms():  # <-- VÉRIFIE BIEN QU'IL N'Y A RIEN ENTRE LES PARENTHÈSES
    """Scanne le dossier ROMS et retourne une liste de jeux."""
    print("--- Démarrage du scan des ROMs ---")
    
    # 1. On récupère TOUT depuis le config.py
    roms_path = config.get_path('roms_dir')
    core_map = config.get_core_map()
    rom_extensions = config.get_rom_extensions()
    
    print(f"Chemin des ROMs : {roms_path}")
    print(f"Extensions valides : {rom_extensions}")
    print(f"Cores mappés : {core_map}")
    
    games_found = []
    
    for root_dir, sub_dirs, files in os.walk(roms_path):
        system_name = os.path.basename(root_dir)

        if system_name in core_map:
            print(f"Système trouvé : {system_name}")
            
            core_name_from_map = core_map[system_name]
            
            for game_file in files:
                if game_file.endswith(rom_extensions):
                    game_name = os.path.splitext(game_file)[0]
                    
                    game_info = {
                        "name": game_name,
                        "system": system_name,
                        "rom_path": os.path.join(root_dir, game_file),
                        "core_name": core_name_from_map 
                    }
                    
                    games_found.append(game_info)
                    print(f"  > Trouvé : {game_name}")

    print(f"--- Scan terminé. {len(games_found)} jeux trouvés. ---")
    return games_found