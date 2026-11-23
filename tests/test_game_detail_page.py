import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from datetime import date

from PySide6.QtWidgets import QApplication

from mediaatlas.domain.models import MediaItem
from mediaatlas.domain.enums import MediaType
from mediaatlas.gui.pages.game_detail_page import GameDetailPage


def test_game_detail_page():
    app = QApplication.instance() or QApplication([])

    game = MediaItem(
        source="igdb",
        external_id="123",
        media_type=MediaType.GAME,
        title="Elden Ring",
        description="An action RPG.",
        release_date=date(2022, 2, 25),
        genres=("Action", "RPG"),
    )

    page = GameDetailPage()
    page.set_game(game)

    assert page.title_label.text() == "Elden Ring"
    assert page.genres_label.text() == "Action, RPG"
    assert page.release_label.text() == "2022-02-25"
    assert page.description_label.text() == "An action RPG."

    events = []
    page.back_requested.connect(lambda: events.append("back"))

    page.back_button.click()

    assert events == ["back"]