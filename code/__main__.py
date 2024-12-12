from go import GoGame
from PyQt6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GoGame()
    window.show()
    sys.exit(app.exec())
