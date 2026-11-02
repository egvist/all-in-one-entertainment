
from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("MediaAtlas")
        self.resize(1100, 700)
        self.setMinimumSize(900, 600)

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        # Remove outer spacing so the sidebar fills the height
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = self.create_sidebar()
        content_area = self.create_content_area()

        # Responsive width ratio: 1:4
        main_layout.addWidget(sidebar, 1)
        main_layout.addWidget(content_area, 4)

        self.setCentralWidget(central_widget)

    def create_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")

        # Responsive sidebar with width limits
        sidebar.setMinimumWidth(190)
        sidebar.setMaximumWidth(280)

        sidebar.setStyleSheet("""
            QWidget#sidebar {
                background-color: #282828;
            }

            QWidget#sidebar QPushButton {
                text-align: left;
                padding-left: 16px;
            }
        """)

        v_layout = QVBoxLayout(sidebar)
        v_layout.setSpacing(8)
        v_layout.setContentsMargins(12, 16, 12, 16)

        # Application title
        app_title = QLabel("MediaAtlas")
        app_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 8px;"
        )
        v_layout.addWidget(app_title)

        # Navigation buttons
        categories = [
            "Home",
            "Games",
            "Movies",
            "TV Series",
            "Anime",
            "Books",
        ]

        for category in categories:
            button = QPushButton(category)
            button.setFixedHeight(52)
            v_layout.addWidget(button)

        # Push My Library to the bottom
        v_layout.addStretch()

        library_button = QPushButton("My Library")
        library_button.setFixedHeight(52)
        v_layout.addWidget(library_button)

        return sidebar

    def create_content_area(self):
        content_area = QWidget()

        v_layout = QVBoxLayout(content_area)
        v_layout.setSpacing(8)
        v_layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Games Catalog")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        description = QLabel("Discover your next game")

        v_layout.addWidget(title)
        v_layout.addWidget(description)
        v_layout.addStretch()

        return content_area
