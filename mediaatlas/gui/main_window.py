from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QPushButton

class MainWindow(QMainWindow):

    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MediaAtlas")
        self.resize(1100, 700)
        self.setup_ui()


    def setup_ui(self):

        central_widget = QWidget()
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout) # baska yontem de main_layout = QHBoxLayout(central_widget) # bu sekilde de yapilabilir

        sidebar = self.create_sidebar()
        content_area = self.create_content_area()

        main_layout.addWidget(sidebar, 1) # main_layout.setStretch(0, 1)  # Sidebar takes 1/4 of the width
        main_layout.addWidget(content_area, 3) # main_layout.setStretch(1, 3)  # Content area takes 3/4 of the width

        
        

        self.setCentralWidget(central_widget)


    def create_sidebar(self):

        sidebar = QWidget()
        v_layout = QVBoxLayout()
        sidebar.setLayout(v_layout)

        categories = ["Home", "Games", "Movies", "TV Series", "Anime", "Books", "My Library"]
        for category in categories:
            button = QPushButton(category)
            v_layout.addWidget(button)

        v_layout.addStretch()
        return sidebar

    def create_content_area(self):

        content_area = QWidget()
        v_layout = QVBoxLayout()
        content_area.setLayout(v_layout)

        title = QLabel("Games Catalog")
        description = QLabel("Discover your next game")

        v_layout.addWidget(title)
        v_layout.addWidget(description)
        v_layout.addStretch()

        return content_area