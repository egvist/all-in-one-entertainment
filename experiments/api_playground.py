
import os
import json
from pathlib import Path

from dotenv import load_dotenv

from mediaatlas.api.igdb_client import IGDBClient


PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

client_id = os.getenv("TWITCH_CLIENT_ID")
client_secret = os.getenv("TWITCH_CLIENT_SECRET")


client = IGDBClient(client_id, client_secret)

client.search_games("Elden Ring")
client.search_games("Minecraft")
client.search_games("Cyberpunk 2077")


first_page = client.search_games("Mario", page=1, page_size=10)
second_page = client.search_games("Mario", page=2, page_size=5)

for game in first_page:
    print("PAGE 1:", game.external_id, game.title)

for game in second_page:
    print("PAGE 2:", game.external_id, game.title)


games = client.discover_games(page=1, page_size=5)

for game in games:
    print(game.title)