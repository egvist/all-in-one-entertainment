from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QScrollArea,
    QGridLayout,
    QStackedWidget,
)

from PySide6.QtNetwork import QNetworkAccessManager
from PySide6.QtCore import QThread, Slot, Qt, QTimer

from mediaatlas.gui.workers import GameLoadWorker
from mediaatlas.api.igdb_client import IGDBClient
from mediaatlas.domain.models import MediaItem
from mediaatlas.gui.widgets.game_card import GameCard
from mediaatlas.gui.pages.game_detail_page import GameDetailPage

class MainWindow(QMainWindow):

    def __init__(self, igdb_client: IGDBClient):
        super().__init__()

        self.igdb_client = igdb_client
        self.image_manager = QNetworkAccessManager(self)

        self.setWindowTitle("MediaAtlas")
        self.resize(1100, 700)
        self.setMinimumSize(900, 600)

        self._search_running = False

        # Page navigation
        self.content_stack = QStackedWidget()
        self._game_cards = []
        self.discover_page = self.create_discover_page()
        self.detail_page = GameDetailPage()

        self.content_stack.addWidget(self.discover_page)
        self.content_stack.addWidget(self.detail_page)

        self.content_stack.setCurrentWidget(self.discover_page)

        self.setup_ui()
        QTimer.singleShot(0, self.load_initial_games)

    def setup_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = self.create_sidebar()

        main_layout.addWidget(sidebar, 1)
        main_layout.addWidget(self.content_stack, 4)

        self.setCentralWidget(central_widget)

        # Navigation signals
        self.detail_page.back_requested.connect(self.show_discover)

    def create_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")

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

        # Discover navigation
        self.discover_button = QPushButton("Discover")
        self.discover_button.setFixedHeight(52)

        self.discover_button.clicked.connect(self.show_discover)

        v_layout.addWidget(self.discover_button)

        # Push My Library to the bottom
        v_layout.addStretch()

        # My Library navigation
        self.library_button = QPushButton("My Library")
        self.library_button.setFixedHeight(52)

        v_layout.addWidget(self.library_button)

        return sidebar

    def create_discover_page(self):
        content_area = QWidget()

        # Results grid
        self.results_container = QWidget()

        self.results_grid = QGridLayout(self.results_container)
        self.results_grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.results_grid.setSpacing(12)
        self.results_grid.setContentsMargins(8, 8, 8, 8)

        # Scroll area
        self.results_scroll_area = QScrollArea()
        self.results_scroll_area.setWidgetResizable(True)
        self.results_scroll_area.setWidget(self.results_container)

        # Main content layout
        v_layout = QVBoxLayout(content_area)
        v_layout.setSpacing(8)
        v_layout.setContentsMargins(24, 24, 24, 24)

        # Page title
        title = QLabel("Discover Games")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        description = QLabel("Discover your next favorite game")

        v_layout.addWidget(title)
        v_layout.addWidget(description)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search any games...")

        self.search_button = QPushButton("Search")

        search_field = QHBoxLayout()
        search_field.addWidget(self.search_input)
        search_field.addWidget(self.search_button)

        self.search_button.clicked.connect(self.handle_search)
        self.search_input.returnPressed.connect(self.handle_search)

        v_layout.addLayout(search_field)

        # Search status
        self.result_label = QLabel(
            "Search for a game to get started."
        )
        self.result_label.setWordWrap(True)

        v_layout.addWidget(self.result_label)

        # Game cards
        v_layout.addWidget(self.results_scroll_area, 1)

        return content_area

    def handle_search(self):
        query = self.search_input.text().strip()

        if not query:
            return

        self.start_loading(query)



    @Slot(object)
    def show_search_result(self, games: list[MediaItem]):
        self.clear_results()

        if not games:
            self.result_label.setText("No games found.")
            return

        self.result_label.setText(
            f"Games found: {len(games)}"
        )

        for game in games:
            game_card = GameCard(game, self.image_manager)

            game_card.clicked.connect(self.open_game_detail)

            self._game_cards.append(game_card)

        self.layout_game_cards()

    @Slot(object)
    def open_game_detail(self, game: MediaItem):
        self.detail_page.set_game(game)

        self.content_stack.setCurrentWidget(
            self.detail_page
        )

    @Slot()
    def show_discover(self):
        self.content_stack.setCurrentWidget(
            self.discover_page
        )

    @Slot()
    def on_search_finished(self):
        self._search_running = False
        self.search_button.setEnabled(True)
        self.search_input.setEnabled(True)

        self._search_worker = None
        self._search_thread = None

    @Slot(str)
    def show_search_error(self, message: str):
        self.result_label.setText(
            f"Search failed: {message}"
        )

    def clear_results(self):
        while self.results_grid.count():
            item = self.results_grid.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()
        self._game_cards.clear()

    def start_loading(self, query:  str | None = None):

        if self._search_running:
            return

        self._search_running = True

        self.clear_results()

        if query is None:
            self.result_label.setText("Loading games...")
        else:
            self.result_label.setText("Searching...")

        self.search_button.setEnabled(False)
        self.search_input.setEnabled(False)


        # Worker thread
        self._search_thread = QThread()
        self._search_worker = GameLoadWorker(
            self.igdb_client,
            query
        )

        self._search_worker.moveToThread(self._search_thread)

        # Start search
        self._search_thread.started.connect(
            self._search_worker.run
        )

        # Results and errors
        self._search_worker.result_ready.connect(
            self.show_search_result
        )

        self._search_worker.error.connect(
            self.show_search_error
        )

        # Cleanup
        self._search_worker.finished.connect(
            self._search_thread.quit
        )

        self._search_worker.finished.connect(
            self._search_worker.deleteLater
        )

        self._search_thread.finished.connect(
            self.on_search_finished
        )

        self._search_thread.finished.connect(
            self._search_thread.deleteLater
        )

        self._search_thread.start()


    def load_initial_games(self):
        self.start_loading(None)


    def resizeEvent(self, event):
        super().resizeEvent(event)

        QTimer.singleShot(0, self.layout_game_cards)


    def layout_game_cards(self):
        if not self._game_cards:
            return

        viewport_width = self.results_scroll_area.viewport().width()

        left, top, right, bottom = self.results_grid.getContentsMargins()

        available_width = viewport_width - left - right

        target_card_width = 250
        spacing = 12

        
        columns = max(
            1,
            (available_width + spacing) // (target_card_width + spacing)
        )

        card_width = (
            available_width - (columns - 1) * spacing
        ) // columns

       
        while self.results_grid.count():
            self.results_grid.takeAt(0)

        
        for column in range(self.results_grid.columnCount()):
            self.results_grid.setColumnStretch(column, 0)

        
        for column in range(columns):
            self.results_grid.setColumnStretch(column, 1)

       
        for index, card in enumerate(self._game_cards):
            row, column = divmod(index, columns)

            card.setFixedWidth(card_width)

            self.results_grid.addWidget(card, row, column)