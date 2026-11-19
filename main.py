from mediaatlas.gui.main_window import MainWindow
from PySide6.QtWidgets import QApplication
import sys
import os
from dotenv import load_dotenv
from mediaatlas.api.igdb_client import IGDBClient
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

def main():
    app = QApplication(sys.argv)
        
    client_id = os.getenv("TWITCH_CLIENT_ID")
    client_secret = os.getenv("TWITCH_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise ValueError("Missing Twitch credentials")
    client = IGDBClient(client_id, client_secret)

    main_window = MainWindow(client)
    main_window.show()
    sys.exit(app.exec())



if __name__ == "__main__":
    main()