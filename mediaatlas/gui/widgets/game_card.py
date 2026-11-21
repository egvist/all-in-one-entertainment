from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap
from mediaatlas.domain.models import MediaItem
from PySide6.QtCore import Qt, QUrl, Slot
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply


class GameCard(QFrame):


    def __init__(self, game: MediaItem, image_manager: QNetworkAccessManager):
        super().__init__()
        self.image_manager = image_manager
        self.game = game
        self.setup_ui()

    def setup_ui(self):
        card_layout = QVBoxLayout(self)

        self.cover_label = QLabel("Game Cover")
        self.cover_label.setFixedHeight(180)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setObjectName("gameCard")
        self.setStyleSheet("""
            QFrame#gameCard {
                background-color: gray;
                border-radius: 12px;
            }

        """)

        self.setFixedWidth(220)

        label = QLabel(self.game.title)
        label.setWordWrap(True)
        genre = QLabel()
        genres_text = (
            ", ".join(self.game.genres)
            if self.game.genres
            else "Unknown genre"
        )

        genre.setText(genres_text)
        release_date = QLabel()
        if self.game.release_date is not None:
            release_date.setText(self.game.release_date.isoformat())
        else:
            release_date.setText("Release date unknown")

        card_layout.addWidget(self.cover_label)
        card_layout.addWidget(label)
        card_layout.addWidget(genre)
        card_layout.addWidget(release_date)

        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(8)

        self.load_cover()

    def load_cover(self):
        cover_url = self.game.cover_url

        if not cover_url:
            self.cover_label.setText("No cover available")

        else:
            url = QUrl(cover_url)
            request  = QNetworkRequest(url)
            self._cover_reply = self.image_manager.get(request)
            self._cover_reply.finished.connect(self.on_cover_loaded)
            self._cover_reply.finished.connect(self._cover_reply.deleteLater)

    @Slot()
    def on_cover_loaded(self):
        reply = self._cover_reply

        if reply is None:
            return

        try:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                self.cover_label.setText("No cover available")
                return

            image_data = bytes(reply.readAll())

            pixmap = QPixmap()

            if not pixmap.loadFromData(image_data):
                self.cover_label.setText("No cover available")
                return

            scaled_pixmap = pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.cover_label.setPixmap(scaled_pixmap)

        finally:
            self._cover_reply = None
