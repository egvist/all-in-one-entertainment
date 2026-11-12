
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

games = client.search_games("Elden Ring")

for game in games:
    print("ID:", game.external_id)
    print("Title:", game.title)
    print("Description:", game.description)
    print("Genres:", game.genres)
    print("Release Date:", game.release_date)
    print("Cover URL:", game.cover_url)
    print()
