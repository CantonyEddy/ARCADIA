# main.py
from borne_app.borne_interface import BorneInterface
from borne_app.game_scanner import sync_roms_to_db
from datas.database import init_db


if __name__ == "__main__":
    init_db()
    sync_roms_to_db()
    app = BorneInterface()
    app.run()