from mediaatlas.gui.main_window import MainWindow
from PySide6.QtWidgets import QApplication
import sys


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
    



if __name__ == "__main__":
    main()