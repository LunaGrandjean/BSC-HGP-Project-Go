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
        super().__init__()
        self.size = size
        self.grid = [[0] * size for _ in range(size)]  # 0 = empty, 1 = Black, -1 = White
        self.cell_size = 60

        # Animations
        self.animations = []
        self.animation_timer = QTimer(self)
        self.animation_timer.setInterval(16)  # ~60 FPS
        self.animation_timer.timeout.connect(self.update_animations)
        self.animation_timer.start()

    def animate_piece_placement(self, row, col, piece):
        anim = {
            "row": row,
            "col": col,
            "piece": piece,
            "anim_type": "placement",
            "start_time": QTime.currentTime().msecsSinceStartOfDay(),
            "duration": 250
        }
        self.animations.append(anim)

    def animate_capture(self, captured_positions, captured_piece_color):
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
        now = QTime.currentTime().msecsSinceStartOfDay()
        ongoing = []
        for anim in self.animations:
            elapsed = now - anim["start_time"]
            if elapsed < anim["duration"]:
                ongoing.append(anim)
        self.animations = ongoing
        self.update()

    def reset(self):
        self.grid = [[0] * self.size for _ in range(self.size)]
        self.animations.clear()
        self.update()

    def place_stone(self, row, col, player):
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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.draw_board(painter)
        self.draw_pieces(painter)
        self.draw_animations(painter)

    def draw_board(self, painter):
        painter.setBrush(QColor(210, 180, 140))  # Lighter wood texture
        painter.drawRect(self.rect())

        pen = QPen(Qt.GlobalColor.black, 2)
        painter.setPen(pen)

        for i in range(self.size):
            x = i * self.cell_size + self.cell_size // 2
            painter.drawLine(x, self.cell_size // 2, x, self.size * self.cell_size - self.cell_size // 2)

            y = i * self.cell_size + self.cell_size // 2
            painter.drawLine(self.cell_size // 2, y, self.size * self.cell_size - self.cell_size // 2, y)

    def draw_pieces(self, painter):
        for row in range(self.size):
            for col in range(self.size):
                piece = self.grid[row][col]
                if piece == 0:
                    continue

                is_anim_placement = any(
                    (a["row"] == row and a["col"] == col and a["anim_type"] == "placement")
                    for a in self.animations
                )
                if is_anim_placement:
                    continue

                self.draw_stone(painter, row, col, piece, size_factor=1.0, alpha_val=255)

    def draw_stone(self, painter, row, col, piece, size_factor=1.0, alpha_val=255):
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

        painter.drawEllipse(
            int(center_x - radius),
            int(center_y - radius),
            int(radius * 2),
            int(radius * 2)
        )

    def draw_animations(self, painter):
        now = QTime.currentTime().msecsSinceStartOfDay()
        for anim in self.animations:
            elapsed = now - anim["start_time"]
            progress = min(elapsed / anim["duration"], 1.0)
            atype = anim["anim_type"]
            piece = anim["piece"]

            if atype == "winner":
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
                    size_factor = progress
                    alpha_val = int(255 * progress)
                    self.draw_stone(painter, row, col, piece, size_factor, alpha_val)

                elif atype == "capture":
                    size_factor = 1.0 - progress
                    alpha_val = int(255 * (1.0 - progress))
                    self.draw_stone(painter, row, col, piece, size_factor, alpha_val)

    def sizeHint(self):
        return QSize(self.size * self.cell_size, self.size * self.cell_size)

    def minimumSizeHint(self):
        return QSize(self.size * self.cell_size, self.size * self.cell_size)

    def mousePressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()

        col = round((x - self.cell_size // 2) / self.cell_size)
        row = round((y - self.cell_size // 2) / self.cell_size)

        if 0 <= row < self.size and 0 <= col < self.size:
            self.stonePlaced.emit(row, col)

    def __repr__(self):
        board_representation = "\n".join(
            [
                " ".join("●" if cell == 1 else "○" if cell == -1 else "." for cell in row)
                for row in self.grid
            ]
        )
        return f"Board:\n{board_representation}"
