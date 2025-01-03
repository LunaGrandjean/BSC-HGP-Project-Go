"""
File: board.py
Provides a QFrame-based Board class with drawing logic for a Go board.
It supports storing stone placements in a 2D grid structure.
"""

from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer, QTime
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QRadialGradient


class Board(QFrame):
    stonePlaced = pyqtSignal(int, int)  # Signal emitted with row, col of the placed stone

    def __init__(self, size):
        """
        Initialize the board with a given size (e.g., 7 for a 7x7 board).
        :param size: int, the dimension of the board (7 => 7x7 intersections).
        """
        super().__init__()
        self.size = size
        # 0 = empty, 1 = Black, -1 = White
        self.grid = [[0] * size for _ in range(size)]
        self.cell_size = 60  # Same as your old code

        # A list to store ongoing animations
        self.animations = []

        # A QTimer (~60 FPS) to update animations
        self.animation_timer = QTimer(self)
        self.animation_timer.setInterval(16)  # ~60 FPS
        self.animation_timer.timeout.connect(self.update_animations)
        self.animation_timer.start()

    # ----------------------------------------
    # Animation API
    # ----------------------------------------
    def animate_piece_placement(self, row, col, piece):
        """
        Animate a new stone placement:
         - Grows from size=0 to full over 2 seconds (or 1s, up to you)
         - Also fades in alpha=0 -> 255 if we want it more obvious
        """
        anim = {
            "row": row,
            "col": col,
            "piece": piece,
            "anim_type": "placement",
            "start_time": QTime.currentTime().msecsSinceStartOfDay(),
            "duration": 250  # 2 seconds to see it more clearly
        }
        self.animations.append(anim)

    def animate_capture(self, captured_positions, captured_piece_color):
        """
        Animate captures by shrinking stones from full size to 0 over 0.5s.
        Also fade alpha from 255 -> 0 for a vanish effect.
        """
        start_t = QTime.currentTime().msecsSinceStartOfDay()
        for (r, c) in captured_positions:
            anim = {
                "row": r,
                "col": c,
                "piece": captured_piece_color,
                "anim_type": "capture",
                "start_time": start_t,
                "duration": 500
            }
            self.animations.append(anim)

    def animate_winner(self, winner_name):
        """
        Flash/fade overlay effect upon game end, over 2 seconds.
        winner_name is "Black" or "White".
        """
        piece_val = 1 if winner_name == "Black" else -1
        anim = {
            "row": -1,
            "col": -1,
            "piece": piece_val,
            "anim_type": "winner",
            "start_time": QTime.currentTime().msecsSinceStartOfDay(),
            "duration": 5000
        }
        self.animations.append(anim)

    def update_animations(self):
        """
        Called ~60 times/second; remove finished animations and repaint.
        """
        now = QTime.currentTime().msecsSinceStartOfDay()
        ongoing = []
        for anim in self.animations:
            elapsed = now - anim["start_time"]
            if elapsed < anim["duration"]:
                ongoing.append(anim)
        self.animations = ongoing
        self.update()  # redraw

    # ----------------------------------------
    # Board logic (unchanged from your old code except we also do animations)
    # ----------------------------------------
    def reset(self):
        """
        Reset the board to its initial empty state.
        """
        self.grid = [[0] * self.size for _ in range(self.size)]
        self.animations.clear()
        self.update()

    def place_stone(self, row, col, player):
        """
        Place a stone on the board for the given player.
        Also triggers a "grow" animation.
        """
        if self.is_within_bounds(row, col) and self.grid[row][col] == 0:
            self.grid[row][col] = player
            self.animate_piece_placement(row, col, player)
            self.update()
            return True
        return False

    def remove_stone(self, row, col):
        if self.is_within_bounds(row, col):
            self.grid[row][col] = 0
            self.update()

    def is_within_bounds(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size

    def get_neighbors(self, row, col):
        # same as your old code
        neighbors = []
        if row > 0:
            neighbors.append((row - 1, col))
        if row < self.size - 1:
            neighbors.append((row + 1, col))
        if col > 0:
            neighbors.append((row, col - 1))
        if col < self.size - 1:
            neighbors.append((row, col + 1))
        return neighbors

    def get_liberties(self, row, col):
        # same as your old code
        pass

    def calculate_territories(self):
        # same as your old code
        pass

    def _explore_territory(self, row, col, visited):
        # same as your old code
        pass

    # ----------------------------------------
    # Painting
    # ----------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.draw_board(painter)
        self.draw_pieces(painter)
        self.draw_animations(painter)

    def draw_board(self, painter):
        """
        Exactly your old approach: golden background, black lines for a 7x7
        with cell_size=60.
        """
        # 1) Fill with golden color
        painter.setBrush(QColor(181, 137, 0))
        painter.drawRect(self.rect())

        # 2) Draw grid lines in black
        pen = QPen(Qt.GlobalColor.black, 2)
        painter.setPen(pen)

        for i in range(self.size):
            # vertical line
            x = i * self.cell_size + self.cell_size // 2
            painter.drawLine(
                x,
                self.cell_size // 2,
                x,
                self.size * self.cell_size - self.cell_size // 2
            )
            # horizontal line
            y = i * self.cell_size + self.cell_size // 2
            painter.drawLine(
                self.cell_size // 2,
                y,
                self.size * self.cell_size - self.cell_size // 2,
                y
            )

    def draw_pieces(self, painter):
        """
        Draw stones that are NOT in the middle of a "placement" animation,
        so the growing stone isn't overlapped by a full stone.
        """
        for row in range(self.size):
            for col in range(self.size):
                piece = self.grid[row][col]
                if piece == 0:
                    continue

                # Skip if there's an active "placement" anim for this cell
                is_anim_placement = any(
                    (a["row"] == row and a["col"] == col and a["anim_type"] == "placement")
                    for a in self.animations
                )
                if is_anim_placement:
                    continue

                # otherwise, draw full stone
                self.draw_stone(painter, row, col, piece, size_factor=1.0, alpha_val=255)

    def draw_stone(self, painter, row, col, piece, size_factor=1.0, alpha_val=255):
        """
        Draw a single stone with radial gradient, scaled by size_factor,
        with partial alpha=alpha_val if needed.
        """
        center_x = col * self.cell_size + self.cell_size // 2
        center_y = row * self.cell_size + self.cell_size // 2
        base_radius = (self.cell_size // 2) - 5
        radius = base_radius * size_factor

        gradient = QRadialGradient(center_x, center_y, radius)
        if piece == 1:  # Black
            gradient.setColorAt(0, QColor(50, 50, 50, alpha_val))
            gradient.setColorAt(1, QColor(0, 0, 0, alpha_val))
        else:  # White
            gradient.setColorAt(0, QColor(255, 255, 255, alpha_val))
            gradient.setColorAt(1, QColor(200, 200, 200, alpha_val))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.GlobalColor.transparent)

        # cast to int so PyQt6 won't complain about float
        painter.drawEllipse(
            int(center_x - radius),
            int(center_y - radius),
            int(radius * 2),
            int(radius * 2)
        )

    def draw_animations(self, painter):
        """
        Draw ongoing animations for placement, capture, winner flash.
        """
        now = QTime.currentTime().msecsSinceStartOfDay()
        for anim in self.animations:
            elapsed = now - anim["start_time"]
            progress = min(elapsed / anim["duration"], 1.0)
            atype = anim["anim_type"]
            piece = anim["piece"]

            if atype == "winner":
                # fade overlay from alpha=255 -> 0
                alpha = int(255 * (1.0 - progress))
                color = Qt.GlobalColor.white if piece == -1 else Qt.GlobalColor.black
                painter.setPen(Qt.GlobalColor.transparent)
                overlay = QColor(color)
                overlay.setAlpha(alpha)
                painter.setBrush(QBrush(overlay))
                painter.drawRect(self.rect())

            else:
                row, col = anim["row"], anim["col"]
                if atype == "placement":
                    # size=0->1, alpha=0->255
                    size_factor = progress
                    alpha_val = int(255 * progress)
                    self.draw_stone(painter, row, col, piece, size_factor, alpha_val)

                elif atype == "capture":
                    # size=1->0, alpha=255->0
                    size_factor = 1.0 - progress
                    alpha_val = int(255 * (1.0 - progress))
                    self.draw_stone(painter, row, col, piece, size_factor, alpha_val)

    # ----------------------------------------
    # Sizing
    # ----------------------------------------
    def sizeHint(self):
        return QSize(self.size * self.cell_size, self.size * self.cell_size)

    def minimumSizeHint(self):
        return QSize(self.size * self.cell_size, self.size * self.cell_size)

    # ----------------------------------------
    # Mouse
    # ----------------------------------------
    def mousePressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()

        col = round((x - self.cell_size // 2) / self.cell_size)
        row = round((y - self.cell_size // 2) / self.cell_size)

        if 0 <= row < self.size and 0 <= col < self.size:
            self.stonePlaced.emit(row, col)
        else:
            print("Click outside grid boundaries!")

    def __repr__(self):
        board_representation = "\n".join(
            [
                " ".join("●" if cell == 1 else "○" if cell == -1 else "." for cell in row)
                for row in self.grid
            ]
        )
        return f"Board:\n{board_representation}"
