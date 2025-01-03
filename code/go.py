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
    QWidget, QMessageBox, QMenuBar, QHBoxLayout, QSizePolicy
)
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QAction, QFont
from logic import GameLogic
from board import Board

class GoGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Go Game - 7x7 Board")
        self.resize(QSize(800, 900))

        # Initialize theme
        self.current_theme = "light"
        self.apply_theme()

        self.black_timer = 120
        self.white_timer = 120
        self.current_timer = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.create_menu()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Turn Label
        self.turn_label = QLabel("Black's Turn")
        self.turn_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.turn_label.setStyleSheet("margin-bottom: 10px;")
        main_layout.addWidget(self.turn_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Score Label
        self.score_label = QLabel("Black: 0 | White: 0")
        self.score_label.setFont(QFont("Arial", 14))
        self.score_label.setStyleSheet("margin-bottom: 20px;")
        main_layout.addWidget(self.score_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Timer Labels
        self.black_timer_label = QLabel("Black Timer: 02:00")
        self.black_timer_label.setFont(QFont("Arial", 14))
        self.black_timer_label.setStyleSheet("margin-bottom: 5px;")
        main_layout.addWidget(self.black_timer_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.white_timer_label = QLabel("White Timer: 02:00")
        self.white_timer_label.setFont(QFont("Arial", 14))
        self.white_timer_label.setStyleSheet("margin-bottom: 20px;")
        main_layout.addWidget(self.white_timer_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Board Layout
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        board_widget = QWidget()
        board_widget.setObjectName("boardWidget")
        board_widget.setLayout(self.grid_layout)
        board_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(board_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        # Control Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        self.pass_button = QPushButton("PASS")
        self.pass_button.clicked.connect(self.pass_turn)

        self.undo_button = QPushButton("UNDO")
        self.undo_button.clicked.connect(self.undo_move)

        self.redo_button = QPushButton("REDO")
        self.redo_button.clicked.connect(self.redo_move)

        self.reset_button = QPushButton("RESET")
        self.reset_button.clicked.connect(self.reset_game)

        button_layout.addWidget(self.pass_button)
        button_layout.addWidget(self.undo_button)
        button_layout.addWidget(self.redo_button)
        button_layout.addWidget(self.reset_button)
        main_layout.addLayout(button_layout)

        self.board_size = 7
        self.buttons = {}
        self.move_history = []
        self.redo_stack = []

        self.logic = GameLogic(self.board_size)

        # Board Widget
        self.board_widget = Board(self.board_size)
        self.board_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.grid_layout.addWidget(self.board_widget, 0, 0, self.board_size, self.board_size)

        self.board_widget.stonePlaced.connect(self.place_stone)

        self.update_labels()

    def create_menu(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        help_menu = menu_bar.addMenu("Help")
        how_to_play_action = QAction("How to Play", self)
        how_to_play_action.triggered.connect(self.show_how_to_play)
        help_menu.addAction(how_to_play_action)

        handicap_menu = menu_bar.addMenu("Handicap")
        handicap_2_action = QAction("Handicap 2 Stones", self)
        handicap_2_action.triggered.connect(lambda: self.apply_handicap(2))
        handicap_menu.addAction(handicap_2_action)
        handicap_3_action = QAction("Handicap 3 Stones", self)
        handicap_3_action.triggered.connect(lambda: self.apply_handicap(3))
        handicap_menu.addAction(handicap_3_action)

        # Theme menu
        theme_menu = menu_bar.addMenu("Theme")
        toggle_theme_action = QAction("Day/Night Theme", self)
        toggle_theme_action.triggered.connect(self.toggle_theme)
        theme_menu.addAction(toggle_theme_action)

    def apply_theme(self):
        if self.current_theme == "light":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #FFFFFF;
                }
                QLabel {
                    color: #000000;
                }
                QPushButton {
                    background-color: #D3D3D3;
                    color: #000000;
                    border-radius: 10px;
                    padding: 10px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #B0C4DE;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2D2D2D;
                }
                QLabel {
                    color: #FFFFFF;
                }
                QPushButton {
                    background-color: #3333CC;
                    color: #FFFFFF;
                    border-radius: 10px;
                    padding: 10px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #5555FF;
                }
            """)

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()

    def show_how_to_play(self):
        rules = (
            "Go Game Rules:\n"
            "- Players take turns placing stones on the board.\n"
            "- A group of stones is captured if it has no liberties.\n"
            "- The game ends when both players pass consecutively.\n"
            "- The player controlling the most territory wins.\n\n"
            "Learn More:\n"
            "- https://www.britgo.org/intro/intro2.html\n"
            "- https://www.youtube.com/watch?v=Jq5SObMdV3o"
        )
        QMessageBox.information(self, "How to Play", rules)

    def apply_handicap(self, stones_count):
        state = self.logic.get_board_state()
        any_stone = any(v != 0 for v in state.values())
        if any_stone:
            QMessageBox.warning(self, "Handicap Error", "Handicap can only be applied on an empty board.")
            return

        coords = [(0, 0), (0, self.board_size - 1),
                  (self.board_size - 1, 0), (self.board_size - 1, self.board_size - 1)]

        original_player = self.logic.get_current_player()
        self.logic.current_player = 1  # black
        for i in range(min(stones_count, len(coords))):
            r, c = coords[i]
            result = self.logic.place_stone(r, c)
            if result is None:
                break
            self.logic.current_player = 1
        self.logic.current_player = original_player

        self.update_board_ui()
        self.update_labels()

    def place_stone(self, row, col):
        captured_positions = self.logic.place_stone(row, col)
        if captured_positions is None:
            QMessageBox.warning(self, "Invalid Move", "This move is not valid.")
            return

        just_played = self.logic.get_current_player() * -1

        self.move_history.append((row, col, just_played, captured_positions))
        self.redo_stack.clear()

        if captured_positions:
            self.board_widget.animate_capture(captured_positions, -just_played)

        self.board_widget.place_stone(row, col, just_played)

        if self.current_timer == "black":
            self.white_timer = 120
            self.current_timer = "white"
        else:
            self.black_timer = 120
            self.current_timer = "black"
        self.start_timer()

        self.update_board_ui()
        self.update_labels()
        self.update_timer_labels()

    def undo_move(self):
        if not self.move_history:
            QMessageBox.warning(self, "Undo Error", "No moves to undo.")
            return

        last_move = self.move_history.pop()
        row, col, player_of_move, captured_positions = last_move

        self.logic.undo_stone(row, col, player_of_move, captured_positions)
        self.redo_stack.append(last_move)

        self.update_board_ui()
        self.update_labels()

    def redo_move(self):
        if not self.redo_stack:
            QMessageBox.warning(self, "Redo Error", "No moves to redo.")
            return

        move = self.redo_stack.pop()
        row, col, player_of_move, captured_positions = move
        original_player = self.logic.get_current_player()
        self.logic.current_player = player_of_move

        recaptured = self.logic.place_stone(row, col)
        if recaptured is None:
            self.logic.current_player = original_player
            return

        self.move_history.append((row, col, player_of_move, recaptured))
        self.logic.current_player = original_player

        if recaptured:
            self.board_widget.animate_capture(recaptured, -player_of_move)
        self.board_widget.place_stone(row, col, player_of_move)

        self.update_board_ui()
        self.update_labels()

    def reset_game(self):
        self.logic.reset_game()
        self.move_history.clear()
        self.redo_stack.clear()

        self.black_timer = 120
        self.white_timer = 120
        self.timer.stop()
        self.start_timer()
        self.update_timer_labels()
        self.update_board_ui()
        self.update_labels()

    def pass_turn(self):
        self.logic.pass_turn()
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
        territories = self.logic.calculate_territories()
        final_scores = self.logic.get_final_scores(territories)
        black_final = final_scores["black"]
        white_final = final_scores["white"]
        winner = "Black" if black_final > white_final else "White"

        self.board_widget.animate_winner(winner)

        msg = (
            f"Game Over!\n\n"
            f"Final Scores:\n"
            f"Black = {black_final}\n"
            f"White = {white_final}\n\n"
            f"Winner: {winner}"
        )
        QTimer.singleShot(2100, lambda: QMessageBox.information(self, "Game Over", msg))

    def start_timer(self):
        self.current_timer = "black" if self.logic.get_current_player() == 1 else "white"
        self.timer.start(1000)

    def update_timer(self):
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
        self.black_timer_label.setText(
            f"Black Timer: {self.black_timer // 60:02}:{self.black_timer % 60:02}"
        )
        self.white_timer_label.setText(
            f"White Timer: {self.white_timer // 60:02}:{self.white_timer % 60:02}"
        )

    def update_board_ui(self):
        board_state = self.logic.get_board_state()
        for (r, c), val in board_state.items():
            self.board_widget.grid[r][c] = val
        self.board_widget.update()

    def update_labels(self):
        current_player = "Black" if self.logic.get_current_player() == 1 else "White"
        self.turn_label.setText(f"{current_player}'s Turn")

        scores = self.logic.get_scores()
        black_score = scores["black"]
        white_score = scores["white"]

        captures_black = self.logic.captured_stones["black"]
        captures_white = self.logic.captured_stones["white"]

        self.score_label.setText(
            f"Black: {black_score} | White: {white_score}\n"
            f"Captured by Black: {captures_black} | Captured by White: {captures_white}"
        )
