from datetime import date

from mediaatlas.api.igdb_mapper import map_igdb_game
from mediaatlas.domain.enums import MediaType


def test_map_igdb_game():
    game = {
        "id": 123,
        "name": "Example Game",
        "summary": "An action RPG",
        "first_release_date": 1704067200,
        "cover": {"image_id": "co1234"},
        "genres": [
            {"id": 12, "name": "RPG"},
            {"id": 31, "name": "Adventure"}
        ]
    }

    item = map_igdb_game(game)

    assert item.source == "igdb"
    assert item.external_id == "123"
    assert item.media_type == MediaType.GAME
    assert item.title == "Example Game"
    assert item.description == "An action RPG"
    assert item.release_date == date(2024, 1, 1)
    assert item.genres == ("RPG", "Adventure")
    assert item.cover_url == (
        "https://images.igdb.com/igdb/image/upload/"
        "t_cover_big/co1234.jpg"
    )