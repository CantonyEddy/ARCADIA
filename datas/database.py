# Dans borne_app/game_scanner.py ou borne_app/database.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'datas', 'arcadia.db')

def init_db():
    """Crée la base de données et les tables si elles n'existent pas."""
    # S'assurer que le dossier 'datas' existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table User (selon votre schéma)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            UserID TEXT PRIMARY KEY,
            Username TEXT NOT NULL,
            Password TEXT NOT NULL,
            Mail TEXT,
            CreateDate DATE,
            Avatar TEXT
        )
    ''')

    # Table Game (selon votre schéma)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Game (
            GameID TEXT PRIMARY KEY,
            Name TEXT NOT NULL,
            Path TEXT NOT NULL,
            Plateform TEXT NOT NULL,
            Description TEXT,
            Cover TEXT,
            UserID TEXT,
            FOREIGN KEY (UserID) REFERENCES User(UserID)
        )
    ''')

    # Table de liaison User_Game
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User_Game (
            UserID TEXT,
            GameID TEXT,
            IsFavorite BOOLEAN DEFAULT 0,
            PlayTime INTEGER DEFAULT 0,
            PRIMARY KEY (UserID, GameID),
            FOREIGN KEY (UserID) REFERENCES User(UserID),
            FOREIGN KEY (GameID) REFERENCES Game(GameID)
        )
    ''')

    conn.commit()
    conn.close()
    print("--- Base de données initialisée ---")