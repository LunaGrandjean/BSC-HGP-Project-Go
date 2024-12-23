"""
File: __main__.py
Entry point to launch the Go application.
"""

from go import GoGame
from PyQt6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    # Create the PyQt Application
    app = QApplication(sys.argv)

    # Create the main window (GoGame) and show it
    window = GoGame()
    window.show()

    # Execute the application event loop
    sys.exit(app.exec())
