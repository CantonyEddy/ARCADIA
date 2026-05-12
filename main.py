# main.py
import logging

from borne_app.borne_interface import BorneInterface


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    app = BorneInterface()
    app.run()
