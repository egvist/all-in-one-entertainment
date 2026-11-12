import httpx
from mediaatlas.api.igdb_mapper import map_igdb_game
from mediaatlas.domain.models import MediaItem

class IGDBClient:
    AUTH_BASE_URL = "https://id.twitch.tv"
    API_BASE_URL = "https://api.igdb.com/v4"


    def __init__(self, client_id: str, client_secret: str):
        if not client_id or not client_secret:
            raise ValueError("Missing Twitch credentials")

        self.client_id = client_id
        self.client_secret = client_secret

    def _get_access_token(self) -> str:
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }

        with httpx.Client(
            base_url=self.AUTH_BASE_URL,
            timeout=10.0
        ) as client:
            response = client.post(
                "/oauth2/token",
                data=payload
            )

            response.raise_for_status()
            auth_data = response.json()

        return auth_data["access_token"]

    def search_games(self, title:str) -> list[MediaItem]:
        if not title.strip():
            raise ValueError("Search title cannot be empty")

        access_token = self._get_access_token()

        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

        safe_title = title.replace("\\", "\\\\").replace('"', '\\"')

        query = f"""
        fields id, name, summary, cover.image_id, first_release_date, genres.name;
        search "{safe_title}";
        limit 5;
        """

        with httpx.Client(
            base_url=self.API_BASE_URL,
            headers=headers,
            timeout=10.0
        ) as client:
            response = client.post(
                "/games",
                content=query
            )

            response.raise_for_status()
            games = response.json()

        return [map_igdb_game(game) for game in games]