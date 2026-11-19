
from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit
)

from PySide6.QtCore import QThread, Slot
from mediaatlas.gui.workers import GameSearchWorker
from mediaatlas.api.igdb_client import IGDBClient
from mediaatlas.domain.models import MediaItem


class MainWindow(QMainWindow):

    def __init__(self, igdb_client: IGDBClient):
        super().__init__()

        self.igdb_client = igdb_client
        self.setWindowTitle("MediaAtlas")
        self.resize(1100, 700)
        self.setMinimumSize(900, 600)
        self._search_running = False


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
        

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search any games...")
        self.search_button = QPushButton("Search")
        search_field = QHBoxLayout()
        search_field.addWidget(self.search_input)
        search_field.addWidget(self.search_button)
        self.search_button.clicked.connect(self.handle_search)
        self.search_input.returnPressed.connect(self.handle_search)
        v_layout.addLayout(search_field)

        self.result_label = QLabel("Search for a game to get started.")
        self.result_label.setWordWrap(True)
        v_layout.addWidget(self.result_label)
        v_layout.addStretch()

        return content_area

    def handle_search(self):
        query = self.search_input.text().strip()
        if not query:
            return

        if self._search_running:
            return

        self._search_running = True
        self.result_label.setText("Searching...")
        self.search_button.setEnabled(False)

        
        self._search_thread = QThread()
        self._search_worker = GameSearchWorker(query, self.igdb_client)

        self._search_worker.moveToThread(self._search_thread)

        self._search_thread.started.connect(self._search_worker.run)

        self._search_worker.result_ready.connect(self.show_search_result)
        self._search_worker.error.connect(self.show_search_error)
        self._search_thread.finished.connect(self.on_search_finished)

        self._search_worker.finished.connect(self._search_thread.quit)

        self._search_worker.finished.connect(self._search_worker.deleteLater)
        self._search_thread.finished.connect(self._search_thread.deleteLater)
        

        self._search_thread.start()

    @Slot(object)
    def show_search_result(self, games: list[MediaItem]):
        if not games:
            self.result_label.setText("No games found.")
            return

        lines = []
        for index, game in enumerate(games, start=1):
            lines.append(f"{index}. {game.title}")
        
        result_text = (f"Games found: {len(games)}\n\n" + "\n".join(lines))

        self.result_label.setText(result_text)

    @Slot()
    def on_search_finished(self):
        self._search_running = False
        self.search_button.setEnabled(True)
        self._search_worker = None
        self._search_thread = None

    @Slot(str)
    def show_search_error(self, message:str):
        self.result_label.setText(f"Search failed: {message}")