from enum import Enum

class MediaType(str, Enum):
    GAME = "game"
    MOVIE = "movie"
    TV_SERIES = "tv_series"
    ANIME = "anime"
    BOOK = "book"


class LibraryStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    DROPPED = "dropped"