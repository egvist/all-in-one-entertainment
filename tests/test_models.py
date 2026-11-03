import pytest
from mediaatlas.domain.models import LibraryEntry
from mediaatlas.domain.enums import LibraryStatus, MediaType


def test_planned_entry_without_rating():
    entry = LibraryEntry(
        media_key=("rawg", MediaType.GAME, "123"),
        status=LibraryStatus.PLANNED
    )

    assert entry.rating is None
    assert entry.status == LibraryStatus.PLANNED


def test_completed_entry_can_be_rated():
    entry = LibraryEntry(
        media_key=("rawg", MediaType.GAME, "123"),
        status=LibraryStatus.COMPLETED
    )

    entry.set_rating(8)

    assert entry.rating == 8


def test_invalid_rating_raises_error():
    entry = LibraryEntry(
        media_key=("rawg", MediaType.GAME, "123"),
        status=LibraryStatus.COMPLETED
    )

    with pytest.raises(ValueError):
        entry.set_rating(15)


def test_planned_entry_cannot_be_rated():
    entry = LibraryEntry(
        media_key=("rawg", MediaType.GAME, "123"),
        status=LibraryStatus.PLANNED
    )

    with pytest.raises(ValueError):
        entry.set_rating(8)



def test_rating_rejects_float():
    entry = LibraryEntry(
        media_key=("rawg", MediaType.GAME, "123"),
        status=LibraryStatus.COMPLETED
    )

    with pytest.raises(ValueError):
        entry.set_rating(5.5)


def test_rating_rejects_bool():
    entry = LibraryEntry(
        media_key=("rawg", MediaType.GAME, "123"),
        status=LibraryStatus.COMPLETED
    )

    with pytest.raises(ValueError):
        entry.set_rating(True)


def test_remove_rating():
    entry = LibraryEntry(
        media_key=("rawg", MediaType.GAME, "123"),
        status=LibraryStatus.COMPLETED
    )

    entry.set_rating(8)
    entry.set_rating(None)

    assert entry.rating is None


def test_change_status_clears_rating():
    entry = LibraryEntry(
        media_key=("rawg", MediaType.GAME, "123"),
        status=LibraryStatus.COMPLETED,
        rating=8
    )

    entry.change_status(LibraryStatus.PLANNED)

    assert entry.status == LibraryStatus.PLANNED
    assert entry.rating is None
    assert entry.completed_at is None


def test_same_status_preserves_completion_date():
    entry = LibraryEntry(
        media_key=("rawg", MediaType.GAME, "123"),
        status=LibraryStatus.PLANNED
    )

    entry.change_status(LibraryStatus.COMPLETED)
    original_date = entry.completed_at

    entry.change_status(LibraryStatus.COMPLETED)

    assert original_date is not None
    assert entry.completed_at == original_date


def test_invalid_rating_preserves_old_rating():
    entry = LibraryEntry(
        media_key=("rawg", MediaType.GAME, "123"),
        status=LibraryStatus.COMPLETED,
        rating=8
    )

    with pytest.raises(ValueError):
        entry.set_rating(15)

    assert entry.rating == 8

def test_invalid_initial_status():
    with pytest.raises(ValueError, match="Invalid library status"):
        LibraryEntry(
            media_key=("rawg", MediaType.GAME, "123"),
            status="banana"
        )

def test_valid_initial_status():
    entry = LibraryEntry(
        media_key=("rawg", MediaType.GAME, "123"),
        status=LibraryStatus.PLANNED
    )

    assert entry.status == LibraryStatus.PLANNED