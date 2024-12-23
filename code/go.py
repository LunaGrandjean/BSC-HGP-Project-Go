"""
File: go.py
Defines the main QMainWindow class (GoGame) for the Go GUI:
- Timers
- Menu creation (Help, Handicap, etc.)
- Board layout with buttons
- Pass, Undo, Redo, Reset
- Handling of final game over
- Resizable window
- Handicap stones
"""

from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QLabel, QGridLayout, QPushButton,
    QWidget, QMessageBox, QMenuBar, QHBoxLayout
)
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QAction, QFont
from logic import GameLogic

class GoGame(QMainWindow):
    def __init__(self):
        """
        Initialize the GoGame window with:
        - Resizable window (instead of fixed size)
        - Timers
        - Board (7x7)
        - Buttons for pass, undo, redo, reset
        - Labels for turn, score, and timers
        - Handicap feature
        """
        super().__init__()
        self.setWindowTitle("Go Game - 7x7 Board")

        # Instead of a fixed size, just pick an initial size so the user can resize
        self.resize(QSize(800, 900))

        # Timers (2 minutes each). We reset them after each move for a "simple speed" style.
        self.black_timer = 120
        self.white_timer = 120
        self.current_timer = None

        # QTimer that counts down each player's clock
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        # Create the top menu
        self.create_menu()

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Turn label
        self.turn_label = QLabel("Black's Turn")
        self.turn_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.turn_label.setStyleSheet("color: black; margin-bottom: 10px;")
        main_layout.addWidget(self.turn_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Score label
        self.score_label = QLabel("Black: 0 | White: 0")
        self.score_label.setFont(QFont("Arial", 14))
        self.score_label.setStyleSheet("color: gray; margin-bottom: 20px;")
        main_layout.addWidget(self.score_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Timer labels for each player
        self.black_timer_label = QLabel("Black Timer: 02:00")
        self.black_timer_label.setFont(QFont("Arial", 14))
        self.black_timer_label.setStyleSheet("color: black; margin-bottom: 5px;")
        main_layout.addWidget(self.black_timer_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.white_timer_label = QLabel("White Timer: 02:00")
        self.white_timer_label.setFont(QFont("Arial", 14))
        self.white_timer_label.setStyleSheet("color: gray; margin-bottom: 20px;")
        main_layout.addWidget(self.white_timer_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Board layout
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(50, 50, 50, 50)
        board_widget = QWidget()
        board_widget.setLayout(self.grid_layout)
        # Keep your existing background color / border for the board
        board_widget.setStyleSheet("background-color: #B58500; border: 5px solid black;")
        main_layout.addWidget(board_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        # Buttons for pass, undo, redo, reset
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

        # New REDO button for advanced feature
        self.redo_button = QPushButton("REDO")
        self.redo_button.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.redo_button.setStyleSheet("background-color: #ffffff; color: purple; border: 2px solid purple; border-radius: 10px; padding: 10px;")
        self.redo_button.clicked.connect(self.redo_move)

        self.reset_button = QPushButton("RESET")
        self.reset_button.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.reset_button.setStyleSheet("background-color: #ffffff; color: green; border: 2px solid green; border-radius: 10px; padding: 10px;")
        self.reset_button.clicked.connect(self.reset_game)

        button_layout.addWidget(self.pass_button)
        button_layout.addWidget(self.undo_button)
        button_layout.addWidget(self.redo_button)
        button_layout.addWidget(self.reset_button)
        main_layout.addLayout(button_layout)

        # Initialize logic, board, and move history
        self.board_size = 7
        self.buttons = {}
        # move_history now stores: (row, col, player, captured_positions)
        self.move_history = []
        # stack for undone moves so we can redo them
        self.redo_stack = []

        # Create the game logic (actual rules)
        self.logic = GameLogic(self.board_size)

        # Create the board of buttons
        self.create_board()

        # Start the game with labels updated
        self.update_labels()

    def create_menu(self):
        """
        Create the top-level menu bar, adding a Help menu and a Handicap menu.
        """
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # Help menu
        help_menu = menu_bar.addMenu("Help")
        how_to_play_action = QAction("How to Play", self)
        how_to_play_action.triggered.connect(self.show_how_to_play)
        help_menu.addAction(how_to_play_action)

        # Handicap menu
        handicap_menu = menu_bar.addMenu("Handicap")

        # Example: 2 stones, 3 stones
        handicap_2_action = QAction("Handicap 2 Stones", self)
        handicap_2_action.triggered.connect(lambda: self.apply_handicap(2))
        handicap_menu.addAction(handicap_2_action)

        handicap_3_action = QAction("Handicap 3 Stones", self)
        handicap_3_action.triggered.connect(lambda: self.apply_handicap(3))
        handicap_menu.addAction(handicap_3_action)

    def show_how_to_play(self):
        """
        Show a message box explaining the rules of Go and some helpful links.
        """
        rules = (
            "Go Game Rules:\n"
            "- Players take turns placing stones on the board.\n"
            "- A group of stones is captured if it has no liberties.\n"
            "- The game ends when both players pass consecutively.\n"
            "- The player controlling the most territory wins.\n\n"
            "Learn More:\n"
            "- Read the rules of Go: https://www.britgo.org/intro/intro2.html\n"
            "- How to Play Go in 2 Minutes: https://www.youtube.com/watch?v=Jq5SObMdV3o"
        )
        QMessageBox.information(self, "How to Play", rules)

    def apply_handicap(self, stones_count):
        """
        Place some initial Black stones (if the board is empty).
        For simplicity, put them in a few corners or star points.
        """
        # Check if board is still empty
        state = self.logic.get_board_state()
        any_stone = any(v != 0 for v in state.values())
        if any_stone:
            QMessageBox.warning(self, "Handicap Error", "Handicap can only be applied on an empty board.")
            return

        # Simple approach: put black stones in corners: (0,0), (0,6), (6,0), (6,6)
        # or in star points. We'll just use corners for brevity:
        coords = [(0, 0), (0, 6), (6, 0), (6, 6)]

        # Save the original player
        original_player = self.logic.get_current_player()
        # Force current player to black
        self.logic.current_player = 1

        for i in range(min(stones_count, len(coords))):
            r, c = coords[i]
            # place stone forcibly (logic flips player, so flip back each time)
            result = self.logic.place_stone(r, c)
            if result is None:
                break
            self.logic.current_player = 1

        # Restore original player
        self.logic.current_player = original_player

        # Refresh UI
        self.update_board_ui()
        self.update_labels()

    def create_board(self):
        """
        Create a 7x7 board using QPushButton for each intersection.
        Each button calls place_stone(row, col) when clicked.
        """
        for row in range(self.board_size):
            for col in range(self.board_size):
                button = QPushButton()
                button.setStyleSheet("background-color: #B58500; border: 1px solid black;")
                button.setFixedSize(70, 70)  # Slightly larger to show the stone
                # Use a lambda to pass row, col to place_stone
                button.clicked.connect(lambda _, r=row, c=col: self.place_stone(r, c))
                self.grid_layout.addWidget(button, row, col)
                self.buttons[(row, col)] = button

    def place_stone(self, row, col):
        """
        Attempt to place a stone at the given row/column.
        If valid, record the move, clear redo stack, and switch the timer to the other player.
        """
        # Attempt the move in logic
        captured_positions = self.logic.place_stone(row, col)
        if captured_positions is None:
            QMessageBox.warning(self, "Invalid Move", "This move is not valid.")
            return

        # The logic flips the current_player, so find out who just played
        current_player = self.logic.get_current_player() * -1

        # Save move in history
        self.move_history.append((row, col, current_player, captured_positions))
        # Clear redo stack because we made a new move
        self.redo_stack.clear()

        # Switch the timer
        if self.current_timer == "black":
            self.white_timer = 120
            self.current_timer = "white"
        else:
            self.black_timer = 120
            self.current_timer = "black"

        self.start_timer()

        # Update UI
        self.update_board_ui()
        self.update_labels()
        self.update_timer_labels()

    def undo_move(self):
        """
        Undo the last move:
        - Pop from move_history
        - Revert changes in logic
        - Push undone move onto redo_stack
        """
        if not self.move_history:
            QMessageBox.warning(self, "Undo Error", "No moves to undo.")
            return

        last_move = self.move_history.pop()
        row, col, player_of_move, captured_positions = last_move

        # Revert that move in logic
        self.logic.undo_stone(row, col, player_of_move, captured_positions)

        # Save it for redo
        self.redo_stack.append(last_move)

        self.update_board_ui()
        self.update_labels()

    def redo_move(self):
        """
        Redo the last undone move from redo_stack, if any.
        """
        if not self.redo_stack:
            QMessageBox.warning(self, "Redo Error", "No moves to redo.")
            return

        # Pop from the redo stack
        move = self.redo_stack.pop()
        row, col, player_of_move, captured_positions = move

        # Temporarily set current_player to that color
        original_player = self.logic.get_current_player()
        self.logic.current_player = player_of_move

        # Re-call place_stone in the logic
        recaptured = self.logic.place_stone(row, col)
        if recaptured is None:
            # If for some reason it's invalid now, skip
            self.logic.current_player = original_player
            return

        # The logic flips the player internally
        # Record the redone move in move_history
        self.move_history.append((row, col, player_of_move, recaptured))

        # restore original
        self.logic.current_player = original_player

        self.update_board_ui()
        self.update_labels()

    def reset_game(self):
        """
        Completely reset the game, including logic, scores, timers, and the board UI.
        """
        self.logic.reset_game()
        self.move_history.clear()
        self.redo_stack.clear()

        self.black_timer = 120
        self.white_timer = 120
        self.timer.stop()
        self.start_timer()  # Start a fresh timer for Black
        self.update_timer_labels()
        self.update_board_ui()
        self.update_labels()

    def pass_turn(self):
        """
        Handle the current player passing.
        Increment pass count, switch player, check for game over.
        """
        self.logic.pass_turn()

        # Switch the timer
        if self.current_timer == "black":
            self.white_timer = 120
            self.current_timer = "white"
        else:
            self.black_timer = 120
            self.current_timer = "black"

        self.start_timer()

        if self.logic.is_game_over():
            self.show_game_over()
        else:
            self.update_labels()
            self.update_timer_labels()

    def show_game_over(self):
        """
        Display final scores and the winner in a QMessageBox.
        """
        territories = self.logic.calculate_territories()
        final_scores = self.logic.get_final_scores(territories)
        black_final = final_scores["black"]
        white_final = final_scores["white"]
        winner = "Black" if black_final > white_final else "White"

        msg = (
            f"Game Over!\n\n"
            f"Final Scores:\n"
            f"Black = {black_final}\n"
            f"White = {white_final}\n\n"
            f"Winner: {winner}"
        )
        QMessageBox.information(self, "Game Over", msg)

    def start_timer(self):
        """
        Start the QTimer for the current player's countdown.
        """
        self.current_timer = "black" if self.logic.get_current_player() == 1 else "white"
        self.timer.start(1000)  # update every second

    def update_timer(self):
        """
        Decrement the current player's clock by 1 second.
        If the clock hits 0, that player loses.
        """
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

        self.update_timer_labels()

    def update_timer_labels(self):
        """
        Update the timer display for both players in mm:ss format.
        """
        self.black_timer_label.setText(f"Black Timer: {self.black_timer // 60:02}:{self.black_timer % 60:02}")
        self.white_timer_label.setText(f"White Timer: {self.white_timer // 60:02}:{self.white_timer % 60:02}")

    def update_board_ui(self):
        """
        Update each QPushButton to display the current state (stone or empty).
        The board background and lines remain as in board.py.
        """
        state = self.logic.get_board_state()
        for (r, c), value in state.items():
            button = self.buttons[(r, c)]
            if value == 1:   # Black stone
                button.setText("●")
                button.setStyleSheet("color: black; font-size: 40px; background-color: #B58500; border: none;")
            elif value == -1:  # White stone
                button.setText("●")
                button.setStyleSheet("color: white; font-size: 40px; background-color: #B58500; border: none;")
            else:  # Empty
                button.setText("")
                button.setStyleSheet("background-color: #B58500; border: 1px solid black;")

    def update_labels(self):
        """
        Update the turn label and score label with current data.
        """
        current_player = "Black" if self.logic.get_current_player() == 1 else "White"
        self.turn_label.setText(f"{current_player}'s Turn")

        # Running scores
        scores = self.logic.get_scores()
        black_score = scores["black"]
        white_score = scores["white"]

        # Captured stones
        captures_black = self.logic.captured_stones["black"]
        captures_white = self.logic.captured_stones["white"]

        self.score_label.setText(
            f"Black: {black_score} | White: {white_score}\n"
            f"Captured by Black: {captures_black} | Captured by White: {captures_white}"
        )
