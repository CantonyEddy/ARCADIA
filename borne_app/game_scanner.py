# borne_app/game_scanner.py
import sqlite3
import os
from . import config
import uuid

# Chemin vers la base de données définie dans votre architecture
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'datas', 'arcadia.db')

def load_games_data(user_id="default_user"):
    """
    Récupère la liste des jeux depuis la BDD SQLite.
    Joint la table Game et User_Game pour avoir les favoris et le temps de jeu.
    """
    print(f"--- Connexion à la BDD pour l'utilisateur : {user_id} ---")
    
    games_list = []
    
    if not os.path.exists(DB_PATH):
        print(f"ERREUR : La base de données est introuvable à {DB_PATH}")
        return []

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
        cursor = conn.cursor()

        # Requête qui récupère les infos du jeu + les stats de l'utilisateur (LEFT JOIN)
        query = """
            SELECT 
                g.GameID, g.Name, g.Path as rom_path, g.Plateform as platform, 
                g.Description, g.Cover,
                COALESCE(ug.IsFavorite, 0) as is_favorite,
                COALESCE(ug.PlayTime, 0) as play_time
            FROM Game g
            LEFT JOIN User_Game ug ON g.GameID = ug.GameID AND ug.UserID = ?
        """
        
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()

        # Conversion en liste de dictionnaires pour rester compatible avec borne_interface.py
        for row in rows:
            games_list.append(dict(row))

        conn.close()
        print(f"--- Scan BDD terminé : {len(games_list)} jeux chargés ---")
        
    except sqlite3.Error as e:
        print(f"Erreur lors de la lecture de la base de données : {e}")

    return games_list

def sync_roms_to_db():
    from . import config
    
    # CORRECT : On utilise 'roms_dir' qui est dans [Paths_Windows]
    root_roms_dir = config.get_path('roms_dir')
    
    # CORRECT : On utilise la nouvelle fonction pour les extensions
    allowed_extensions = config.get_rom_extensions()
    
    systems = config.get_all_core_keys() 
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if not os.path.exists(root_roms_dir):
        print(f"Répertoire introuvable : {root_roms_dir}")
        return

    # Scan des dossiers (gestion de la casse pour 'nes' vs 'NES')
    for folder_name in os.listdir(root_roms_dir):
        folder_path = os.path.join(root_roms_dir, folder_name)
        
        if os.path.isdir(folder_path):
            # On cherche le système correspondant dans le CoreMap
            system_key = next((s for s in systems if s.lower() == folder_name.lower()), None)
            
            if system_key:
                for filename in os.listdir(folder_path):
                    if filename.lower().endswith(allowed_extensions):
                        rom_path = os.path.join(folder_path, filename)
                        
                        # Vérification doublon
                        cursor.execute("SELECT 1 FROM Game WHERE Path = ?", (rom_path,))
                        if not cursor.fetchone():
                            game_id = str(uuid.uuid4())
                            game_name = os.path.splitext(filename)[0].replace('-', ' ').replace('_', ' ')
                            
                            cursor.execute('''
                                INSERT INTO Game (GameID, Name, Path, Plateform, Description, Cover)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (game_id, game_name, rom_path, system_key, f"Système {system_key}", f"assets/covers_game/{game_name}.jpg"))
                            print(f" [+] Ajouté : {game_name}")
    
    conn.commit()
    conn.close()
    print("--- Synchronisation terminée ---")