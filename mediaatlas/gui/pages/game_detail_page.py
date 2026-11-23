from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal
from mediaatlas.domain.models import MediaItem

class GameDetailPage(QWidget):

    back_requested = Signal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.title_label = QLabel()
        self.genres_label = QLabel()
        self.release_label = QLabel()
        self.description_label = QLabel()
        self.back_button = QPushButton()
        self.back_button.setText("Back")
        self.description_label.setWordWrap(True)
        
        self.back_button.clicked.connect(self.back_requested.emit)

        layout.addWidget(self.title_label)
        layout.addWidget(self.genres_label)
        layout.addWidget(self.release_label)
        layout.addWidget(self.description_label)

        layout.addStretch()

        layout.addWidget(self.back_button)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)   
        self.title_label.setStyleSheet(
            "font-size: 26px; font-weight: bold;"
        )

    def set_game(self, game: MediaItem) -> None:
        self.title_label.setText(game.title)
        genres_text = (
            ", ".join(game.genres)
            if game.genres
            else "Unknown genre"
        )
        self.genres_label.setText(genres_text)
        if game.release_date is not None:
            self.release_label.setText(game.release_date.isoformat())
        else:
            self.release_label.setText("Release date unknown")
        if game.description is None:
            self.description_label.setText("No description available")
        else:
            self.description_label.setText(game.description)