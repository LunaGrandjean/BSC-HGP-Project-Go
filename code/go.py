from PyQt6.QtWidgets import QMainWindow, QGridLayout, QPushButton, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QSize
from logic import GameLogic  # Import only GameLogic

class GoGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Go Game - 7x7 Board")
        self.setFixedSize(QSize(600, 700))  # Adjusted for additional UI elements

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Add game board layout
        self.grid_layout = QGridLayout()
        layout.addLayout(self.grid_layout)

        # Add turn label
        self.turn_label = QLabel("Black's Turn")
        layout.addWidget(self.turn_label)

        # Add scores label
        self.score_label = QLabel("Black: 0 | White: 0")
        layout.addWidget(self.score_label)

        # Add reset button
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.reset_game)
        layout.addWidget(reset_button)

        # Initialize board and game logic
        self.board_size = 7
        self.buttons = {}  # Store buttons for easy access
        self.create_board()
        self.logic = GameLogic(self.board_size)  # Use GameLogic to handle rules and logic
        self.update_labels()

    def create_board(self):
        """
        Create a 7x7 board with buttons representing intersections.
        """
        for row in range(self.board_size):
            for col in range(self.board_size):
                button = QPushButton()
                button.setStyleSheet("background-color: beige; border: 1px solid black;")
                button.setFixedSize(50, 50)  # Set button size
                button.clicked.connect(lambda _, r=row, c=col: self.place_stone(r, c))
                self.grid_layout.addWidget(button, row, col)
                self.buttons[(row, col)] = button

    def place_stone(self, row, col):
        """
        Handle the placement of a stone on the board.
        """
        if not self.logic.place_stone(row, col):
            return  # Invalid move, no changes made

        # Update the UI based on the game state
        state = self.logic.get_board_state()
        for (r, c), value in state.items():
            button = self.buttons[(r, c)]
            if value == 1:  # Black stone
                button.setText("●")
                button.setStyleSheet("color: black; font-size: 24px; background-color: beige;")
            elif value == -1:  # White stone
                button.setText("○")
                button.setStyleSheet("color: white; font-size: 24px; background-color: beige;")
            else:  # Empty space
                button.setText("")
                button.setStyleSheet("background-color: beige; border: 1px solid black;")

        self.update_labels()

    def reset_game(self):
        """
        Reset the game state and update the UI.
        """
        self.logic.reset_game()
        for (r, c), button in self.buttons.items():
            button.setText("")
            button.setStyleSheet("background-color: beige; border: 1px solid black;")
        self.update_labels()

    def update_labels(self):
        """
        Update the turn and score labels to reflect the current state of the game.
        """
        current_player = "Black" if self.logic.get_current_player() == 1 else "White"
        self.turn_label.setText(f"{current_player}'s Turn")
        scores = self.logic.get_scores()
        self.score_label.setText(f"Black: {scores['black']} | White: {scores['white']}")
