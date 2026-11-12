from mediaatlas.domain.models import MediaItem
from mediaatlas.domain.enums import MediaType
from datetime import datetime, timezone

def map_igdb_game(game: dict) -> MediaItem:

    release_data_timestamp = game.get("first_release_date")
    first_release_date = (
        datetime.fromtimestamp(release_data_timestamp, tz=timezone.utc).date()
        if release_data_timestamp is not None
        else None
    )

    genres = tuple(
        genre["name"]
        for genre in game.get("genres", [])
    )


    cover_data = game.get("cover") or {}
    image_id = cover_data.get("image_id")
    cover = (
        f"https://images.igdb.com/igdb/image/upload/t_cover_big/{image_id}.jpg"
        if image_id
        else None
    )

    return MediaItem(
        source="igdb",
        external_id=str(game["id"]),
        media_type=MediaType.GAME,
        title=game["name"],
        description=game.get("summary"),
        cover_url= cover,
        release_date=first_release_date,
        genres=genres
        
    )