import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtNetwork import QNetworkAccessManager

from mediaatlas.domain.models import MediaItem
from mediaatlas.domain.enums import MediaType
from mediaatlas.gui.widgets.game_card import GameCard


def test_game_card_click():
    app = QApplication.instance() or QApplication([])

    game = MediaItem(
        source="igdb",
        external_id="123",
        media_type=MediaType.GAME,
        title="Elden Ring",
    )

    manager = QNetworkAccessManager()
    card = GameCard(game, manager)

    received_games = []
    card.clicked.connect(received_games.append)

    card.show()
    app.processEvents()

    # Sağ tıklama sinyal göndermemeli.
    QTest.mouseClick(card, Qt.MouseButton.RightButton)

    assert received_games == []

    # Sol tıklama oyunu göndermeli.
    QTest.mouseClick(card, Qt.MouseButton.LeftButton)

    assert received_games == [game]

    # İmleç kontrolü
    assert card.cursor().shape() == Qt.CursorShape.PointingHandCursor

    card.close()