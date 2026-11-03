from dataclasses import dataclass, field
from datetime import datetime, timezone, date
from mediaatlas.domain.enums import LibraryStatus, MediaType

@dataclass
class MediaItem:
    source: str
    external_id: str
    media_type: MediaType
    title: str
    description:str | None = None
    cover_url:str | None = None
    release_date: date | None = None
    genres: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("Title cannot be empty")

        if not self.source.strip():
            raise ValueError("Source cannot be empty")

        if not self.external_id.strip():
            raise ValueError("External ID cannot be empty")


@dataclass
class LibraryEntry:
    media_key: tuple[str, MediaType, str]
    status: LibraryStatus
    rating: int | None = None
    notes: str = ""
    added_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None

    def __post_init__(self):
        if not isinstance(self.status, LibraryStatus):
            raise ValueError("Invalid library status")
        
        self._validate_rating(self.rating)
        
        if self.status == LibraryStatus.COMPLETED and self.completed_at is None:
            self.completed_at = datetime.now(timezone.utc)

        if self.status != LibraryStatus.COMPLETED and self.completed_at is not None:
            raise ValueError("Media item cannot have completed date before it is actually completed")

    def _validate_rating(self, rating: int | None) -> None:

        if rating is None:
            return
        
        if type(rating) is not int:
            raise ValueError("Rating must be an integer")

        if rating < 1 or rating > 10:
            raise ValueError("Rating must be between 1 and 10")

        if self.status != LibraryStatus.COMPLETED:
            raise ValueError("You must complete the media before rating it.")

    def change_status(self, new_status: LibraryStatus) -> None:
        if not isinstance(new_status, LibraryStatus):
            raise ValueError("Invalid library status")

        if self.status == new_status:
            return

        if new_status == LibraryStatus.COMPLETED:
            self.completed_at = datetime.now(timezone.utc)

        else:
            self.completed_at = None
            self.rating = None

        self.status = new_status

    def set_rating(self, new_rating: int | None) -> None:
        self._validate_rating(new_rating)
        self.rating = new_rating

        

        
    
