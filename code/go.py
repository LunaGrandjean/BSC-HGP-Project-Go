from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QGridLayout, QPushButton, QWidget, QMessageBox, QMenuBar, QHBoxLayout
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QAction, QFont
from logic import GameLogic

class GoGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Go Game - 7x7 Board")
        self.setFixedSize(QSize(800, 900))

        # Timers
        self.black_timer = 120  # Black player starts with 2 minutes
        self.white_timer = 120  # White player starts with 2 minutes
        self.current_timer = None

        # QTimer for countdown
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        # Create Menu
        self.create_menu()

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add turn label
        self.turn_label = QLabel("Black's Turn")
        self.turn_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.turn_label.setStyleSheet("color: black; margin-bottom: 10px;")
        main_layout.addWidget(self.turn_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add score label
        self.score_label = QLabel("Black: 0 | White: 0")
        self.score_label.setFont(QFont("Arial", 14))
        self.score_label.setStyleSheet("color: gray; margin-bottom: 20px;")
        main_layout.addWidget(self.score_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add timer labels
        self.black_timer_label = QLabel("Black Timer: 02:00")
        self.black_timer_label.setFont(QFont("Arial", 14))
        self.black_timer_label.setStyleSheet("color: black; margin-bottom: 5px;")
        main_layout.addWidget(self.black_timer_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.white_timer_label = QLabel("White Timer: 02:00")
        self.white_timer_label.setFont(QFont("Arial", 14))
        self.white_timer_label.setStyleSheet("color: gray; margin-bottom: 20px;")
        main_layout.addWidget(self.white_timer_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Game board layout
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(50, 50, 50, 50)
        board_widget = QWidget()
        board_widget.setLayout(self.grid_layout)
        board_widget.setStyleSheet("background-color: #B58500; border: 5px solid black;")
        main_layout.addWidget(board_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        self.pass_button = QPushButton("PASS")
        self.pass_button.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.pass_button.setStyleSheet("background-color: #ffffff; color: red; border: 2px solid red; border-radius: 10px; padding: 10px;")
        self.pass_button.clicked.connect(self.pass_turn)

        self.undo_button = QPushButton("UNDO")
        self.undo_button.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.undo_button.setStyleSheet("background-color: #ffffff; color: blue; border: 2px solid blue; border-radius: 10px; padding: 10px;")
        self.undo_button.clicked.connect(self.undo_move)

        self.reset_button = QPushButton("RESET")
        self.reset_button.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.reset_button.setStyleSheet("background-color: #ffffff; color: green; border: 2px solid green; border-radius: 10px; padding: 10px;")
        self.reset_button.clicked.connect(self.reset_game)

        button_layout.addWidget(self.pass_button)
        button_layout.addWidget(self.undo_button)
        button_layout.addWidget(self.reset_button)
        main_layout.addLayout(button_layout)

        # Initialize board and game logic
        self.board_size = 7
        self.buttons = {}
        self.move_history = []  # History of moves (row, col, player)
        self.create_board()
        self.logic = GameLogic(self.board_size)
        self.update_labels()

    
    def start_timer(self):
        """
        Start the timer for the current player.
        """
        self.current_timer = "black" if self.logic.get_current_player() == 1 else "white"
        self.timer.start(1000)  # Timer updates every second

    def update_timer(self):
        """
        Countdown the timer for the current player.
        """
        print(f"Current Timer: {self.current_timer}")  # Debugging print
        if self.current_timer == "black":
            self.black_timer -= 1
            if self.black_timer <= 0:
                self.timer.stop()
                QMessageBox.warning(self, "Game Over", "Black ran out of time! White wins!")
                self.reset_game()
                return
        else:
            self.white_timer -= 1
            if self.white_timer <= 0:
                self.timer.stop()
                QMessageBox.warning(self, "Game Over", "White ran out of time! Black wins!")
                self.reset_game()
                return

        # Update the timer labels
        self.update_timer_labels()


    def update_timer_labels(self):
        """
        Update the timer display for both players.
        """
        self.black_timer_label.setText(f"Black Timer: {self.black_timer // 60:02}:{self.black_timer % 60:02}")
        self.white_timer_label.setText(f"White Timer: {self.white_timer // 60:02}:{self.white_timer % 60:02}")

    def create_menu(self):
        """
        Create the menu bar and add Help menu.
        """
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        help_menu = menu_bar.addMenu("Help")

        # Add "How to Play" option
        how_to_play_action = QAction("How to Play", self)
        how_to_play_action.triggered.connect(self.show_how_to_play)
        help_menu.addAction(how_to_play_action)

    def show_how_to_play(self):
        """
        Display a message box with game rules and links.
        """
        rules = (
            "Go Game Rules:\n"
            "- Players take turns placing stones on the board.\n"
            "- A group of stones is captured if it has no liberties (empty adjacent points).\n"
            "- The game ends when both players pass consecutively.\n"
            "- The player controlling the most territory wins.\n\n"
            "Learn More:\n"
            "- Read the rules of Go: https://www.britgo.org/intro/intro2.html\n"
            "- How to Play Go in 2 Minutes: https://www.youtube.com/watch?v=Jq5SObMdV3o"
        )
        QMessageBox.information(self, "How to Play", rules)

    def create_board(self):
        """
        Create a 7x7 board with buttons representing intersections.
        """
        for row in range(self.board_size):
            for col in range(self.board_size):
                button = QPushButton()
                button.setStyleSheet("background-color: #B58500; border: 1px solid black;")
                button.setFixedSize(70, 70)  # Increased size for larger stones
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

        # Add move to history
        current_player = self.logic.get_current_player()
        self.move_history.append((row, col, current_player))

        # Reset the next player's timer to 2 minutes
        if self.current_timer == "black":
            self.white_timer = 120  # Reset White's timer
            self.current_timer = "white"
        else:
            self.black_timer = 120  # Reset Black's timer
            self.current_timer = "black"

        self.start_timer()  # Restart the timer for the next player

        # Update the UI based on the game state
        self.update_board_ui()
        self.update_labels()
        self.update_timer_labels()  # Ensure the timer labels are updated


    def undo_move(self):
        """
        Undo the last move by removing it from the history and updating the game state.
        """
        if not self.move_history:
            QMessageBox.warning(self, "Undo Error", "No moves to undo.")
            return

        # Get the last move from history
        last_move = self.move_history.pop()
        row, col, player = last_move

        # Undo the move in the game logic
        self.logic.undo_stone(row, col)

        # Update the UI
        self.update_board_ui()
        self.update_labels()

    def reset_game(self):
        """
        Reset the game and timers.
        """
        self.logic.reset_game()
        self.move_history = []
        self.black_timer = 120
        self.white_timer = 120
        self.timer.stop()
        self.start_timer()  # Restart the timer
        self.update_timer_labels()
        self.update_board_ui()
        self.update_labels()

    def pass_turn(self):
        """
        Handle a player passing their turn.
        """
        self.logic.pass_turn()

        # Reset the next player's timer to 2 minutes
        if self.current_timer == "black":
            self.white_timer = 120  # Reset White's timer
            self.current_timer = "white"
        else:
            self.black_timer = 120  # Reset Black's timer
            self.current_timer = "black"

        self.start_timer()  # Restart the timer for the next player

        if self.logic.is_game_over():
            self.show_game_over()
        else:
            self.update_labels()
            self.update_timer_labels()  # Ensure the timer labels are updated


    def show_game_over(self):
        """
        Show a message box with the game result.
        """
        QMessageBox.information(self, "Game Over", "Thank you for playing!")

    def update_board_ui(self):
        """
        Update the board's UI elements to reflect the current state.
        """
        state = self.logic.get_board_state()
        for (r, c), value in state.items():
            button = self.buttons[(r, c)]
            if value == 1:  # Black stone
                button.setText("●")
                button.setStyleSheet("color: black; font-size: 60px; background-color: #B58500; border: none;")
            elif value == -1:  # White stone
                button.setText("●")
                button.setStyleSheet("color: white; font-size: 60px; background-color: #B58500; border: none;")
            else:  # Empty space
                button.setText("")
                button.setStyleSheet("background-color: #B58500; border: 1px solid black;")

    def update_labels(self):
        """
        Update the turn and score labels to reflect the current state of the game.
        """
        current_player = "Black" if self.logic.get_current_player() == 1 else "White"
        self.turn_label.setText(f"{current_player}'s Turn")
        scores = self.logic.get_scores()
        self.score_label.setText(f"Black: {scores['black']} | White: {scores['white']}")
