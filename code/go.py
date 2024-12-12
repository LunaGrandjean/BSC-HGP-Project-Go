from PyQt6.QtWidgets import QMainWindow, QGridLayout, QPushButton, QWidget, QVBoxLayout, QLabel, QMessageBox
from PyQt6.QtCore import QSize
from logic import GameLogic

class GoGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Go Game - 7x7 Board")
        self.setFixedSize(QSize(700, 850))

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        layout.setSpacing(10)
        main_widget.setLayout(layout)

        # Add turn label
        self.turn_label = QLabel("Black's Turn")
        self.turn_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.turn_label)

        # Add scores label
        self.score_label = QLabel("Black: 0 | White: 0")
        self.score_label.setStyleSheet("font-size: 16px; color: gray;")
        layout.addWidget(self.score_label)

        # Add game board layout
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(5)
        layout.addLayout(self.grid_layout)

        # Add control buttons
        reset_button = QPushButton("Reset")
        reset_button.setStyleSheet("background-color: #ffcccb; font-size: 14px; padding: 5px;")
        reset_button.clicked.connect(self.reset_game)
        layout.addWidget(reset_button)

        pass_button = QPushButton("Pass")
        pass_button.setStyleSheet("background-color: #d1ffd1; font-size: 14px; padding: 5px;")
        pass_button.clicked.connect(self.pass_turn)
        layout.addWidget(pass_button)

        # Initialize board and game logic
        self.board_size = 7
        self.buttons = {}
        self.create_board()
        self.logic = GameLogic(self.board_size)
        self.update_labels()

    def create_board(self):
        """
        Create a 7x7 board with buttons representing intersections.
        """
        for row in range(self.board_size):
            for col in range(self.board_size):
                button = QPushButton()
                button.setStyleSheet("""
                    background-color: #f7e8b5;
                    border: 2px solid #a68d5c;
                    border-radius: 5px;
                """)
                button.setFixedSize(60, 60)
                button.clicked.connect(lambda _, r=row, c=col: self.place_stone(r, c))
                self.grid_layout.addWidget(button, row, col)
                self.buttons[(row, col)] = button

    def place_stone(self, row, col):
        """
        Handle the placement of a stone on the board.
        """
        if not self.logic.place_stone(row, col):
            QMessageBox.warning(self, "Invalid Move", "This move is not valid.")
            return

        # Update the UI based on the game state
        self.update_board_ui()
        self.update_labels()

    def reset_game(self):
        """
        Reset the game state and update the UI.
        """
        self.logic.reset_game()
        for (r, c), button in self.buttons.items():
            button.setText("")
            button.setStyleSheet("background-color: #f7e8b5; border: 2px solid #a68d5c; border-radius: 5px;")
        self.update_labels()

    def pass_turn(self):
        """
        Handle a player passing their turn.
        """
        self.logic.pass_turn()
        if self.logic.is_game_over():
            self.show_game_over()
        else:
            self.update_labels()

    def show_game_over(self):
        """
        Show a message box with the game result.
        """
        territories = self.logic.calculate_territories()
        scores = self.logic.get_final_scores(territories)
        winner = "Black" if scores["black"] > scores["white"] else "White"
        QMessageBox.information(
            self,
            "Game Over",
            f"Game Over!\nWinner: {winner}\n"
            f"Black Score: {scores['black']} (Captured: {scores['captured_black']}, Territories: {territories['black']})\n"
            f"White Score: {scores['white']} (Captured: {scores['captured_white']}, Territories: {territories['white']})"
        )
        self.reset_game()

    def update_board_ui(self):
        """
        Update the board's UI elements to reflect the current state.
        """
        state = self.logic.get_board_state()
        for (r, c), value in state.items():
            button = self.buttons[(r, c)]
            if value == 1:  # Black stone
                button.setText("●")
                button.setStyleSheet("color: black; font-size: 24px; background-color: #f7e8b5; border: none;")
            elif value == -1:  # White stone
                button.setText("○")
                button.setStyleSheet("color: white; font-size: 24px; background-color: #f7e8b5; border: none;")
            else:  # Empty space
                button.setText("")
                button.setStyleSheet("background-color: #f7e8b5; border: 2px solid #a68d5c; border-radius: 5px;")

    def update_labels(self):
        """
        Update the turn and score labels to reflect the current state of the game.
        """
        current_player = "Black" if self.logic.get_current_player() == 1 else "White"
        self.turn_label.setText(f"{current_player}'s Turn")
        scores = self.logic.get_scores()
        self.score_label.setText(f"Black: {scores['black']} | White: {scores['white']}")
