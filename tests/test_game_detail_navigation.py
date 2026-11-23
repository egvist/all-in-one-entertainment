import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from mediaatlas.gui.main_window import MainWindow
from mediaatlas.domain.models import MediaItem
from mediaatlas.domain.enums import MediaType


def test_game_detail_navigation():
    app = QApplication.instance() or QApplication([])

    # Bu testte API isteği yapmayacağız.
    window = MainWindow(igdb_client=None)

    game = MediaItem(
        source="igdb",
        external_id="123",
        media_type=MediaType.GAME,
        title="Elden Ring",
        description="An action RPG.",
    )

    window.show_search_result([game])

    window.show()
    app.processEvents()

    # Başlangıçta katalog görünmeli.
    assert window.content_stack.currentWidget() is window.catalog_page

    # Oyun kartına tıkla.
    card = window.results_grid.itemAt(0).widget()

    QTest.mouseClick(card, Qt.MouseButton.LeftButton)

    # Detay sayfası açılmalı.
    assert window.content_stack.currentWidget() is window.detail_page
    assert window.detail_page.title_label.text() == "Elden Ring"

    # Back butonuna bas.
    window.detail_page.back_button.click()

    # Kataloğa geri dönmeli.
    assert window.content_stack.currentWidget() is window.catalog_page

    window.close()