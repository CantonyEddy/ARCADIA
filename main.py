# main.py
import logging

from borne_app import database
from borne_app.borne_interface import BorneInterface


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Ouvre la connexion SQLite, crée le schéma, migre depuis JSON si besoin.
    database.init()

    try:
        app = BorneInterface()
        app.run()
    finally:
        database.close()
