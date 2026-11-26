import httpx
import time

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

        # Cache
        self._access_token: str | None = None
        self._token_expires_at: float = 0.0

    def _get_access_token(self) -> str:
        if (self._access_token is not None and time.monotonic() < self._token_expires_at):
            return self._access_token
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
            self._access_token = auth_data["access_token"]
            expires_in = auth_data["expires_in"]
            self._token_expires_at = (time.monotonic() + max(0, expires_in - 60))

        return auth_data["access_token"]

    def search_games(self, title:str, page: int = 1, page_size: int = 5) -> list[MediaItem]:
        if not title.strip():
            raise ValueError("Search title cannot be empty")

        if type(page) is not int or page < 1:
            raise ValueError("Page must be a positive number")

        if type(page_size) is not int or (page_size > 50 or page_size < 1):
            raise ValueError("Page size must be between 1-50")

        # Pagination
        offset = (page-1) * page_size

        safe_title = title.replace("\\", "\\\\").replace('"', '\\"')

        query = f"""
        fields id, name, summary, cover.image_id, first_release_date, genres.name;
        search "{safe_title}";
        limit {page_size};
        offset {offset};
        """

        games = self._request_games(query)

        # return list of MediaItem object
        return [map_igdb_game(game) for game in games]

    # return games response as json
    def _request_games(self, query: str) -> list[dict]:
        for attempt in range(2):
            access_token = self._get_access_token()
            headers = {
                "Client-ID": self.client_id,
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
                }
            with httpx.Client(
                base_url=self.API_BASE_URL,
                headers=headers,
                timeout=10.0
            ) as client:
                response = client.post("/games", content=query)
                if response.status_code == 401 and attempt == 0:
                    self._invalidate_access_token()
                    continue
                response.raise_for_status()
                games = response.json()
            return games


    def _invalidate_access_token(self) -> None:
        self._access_token = None
        self._token_expires_at = 0.0



    def discover_games(self, page: int = 1, page_size: int = 20) -> list[MediaItem]:

        if type(page) is not int or page < 1:
            raise ValueError("Page must be a positive integer")

        if type(page_size) is not int or not 1 <= page_size <= 50:
            raise ValueError("Page size must be between 1 and 50")

        
        offset = (page-1) * page_size

        query = f"""
            fields id,name,summary, cover.image_id, first_release_date, genres.name, aggregated_rating,aggregated_rating_count;
            where aggregated_rating != null & aggregated_rating_count >= 5;
            sort aggregated_rating desc;
            limit {page_size};
            offset {offset};
        """

        games = self._request_games(query)

        return [map_igdb_game(game) for game in games]