# borne_app/game_scanner.py
import os
from . import config  # Importe notre module config.py

data_game_path = os.path.join(os.path.dirname(__file__), '..', 'datas', 'data_game.json')

def load_games_data():  # <-- VÉRIFIE BIEN QU'IL N'Y A RIEN ENTRE LES PARENTHÈSES
    """Scanne les datas pour retourne une liste de jeux."""
    print("--- Démarrage du scan des datas ---")
    
    # Récupère les datas des jeux depuis le fichier JSON
    games_data = config.load_json(data_game_path)
    print(f"--- Scan terminé : {len(games_data)} jeux trouvés ---")
    print("-------------------------------------")
    print(games_data)
    return games_data

    