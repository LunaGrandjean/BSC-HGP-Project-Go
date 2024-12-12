from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QRadialGradient

class Board(QFrame):
    def __init__(self, size):
        """
        Initialize the board with a given size.
        :param size: Size of the board (e.g., 7 for a 7x7 board)
        """
        super().__init__()
        self.size = size
        self.grid = [[0] * size for _ in range(size)]  # 0 = empty, 1 = Black, -1 = White
        self.cell_size = 60  # Size of each cell in pixels

    def reset(self):
        """
        Reset the board to its initial empty state.
        """
        self.grid = [[0] * self.size for _ in range(self.size)]
        self.update()  # Refresh the UI

    def place_stone(self, row, col, player):
        """
        Place a stone on the board for the given player.
        :param row: Row index
        :param col: Column index
        :param player: 1 for Black, -1 for White
        :return: True if the stone was placed successfully, False otherwise
        """
        if self.is_within_bounds(row, col) and self.grid[row][col] == 0:
            self.grid[row][col] = player
            self.update()  # Refresh the UI
            return True
        return False

    def remove_stone(self, row, col):
        """
        Remove a stone from the board.
        :param row: Row index
        :param col: Column index
        """
        if self.is_within_bounds(row, col):
            self.grid[row][col] = 0
            self.update()  # Refresh the UI

    def is_within_bounds(self, row, col):
        """
        Check if the given position is within the board boundaries.
        :param row: Row index
        :param col: Column index
        :return: True if the position is within bounds, False otherwise
        """
        return 0 <= row < self.size and 0 <= col < self.size

    def get_neighbors(self, row, col):
        """
        Get all valid neighbors of a position on the board.
        :param row: Row index
        :param col: Column index
        :return: List of tuples representing valid neighboring positions
        """
        neighbors = []
        if row > 0:
            neighbors.append((row - 1, col))  # Top
        if row < self.size - 1:
            neighbors.append((row + 1, col))  # Bottom
        if col > 0:
            neighbors.append((row, col - 1))  # Left
        if col < self.size - 1:
            neighbors.append((row, col + 1))  # Right
        return neighbors

    def get_liberties(self, row, col):
        """
        Calculate the liberties for a stone at the given position.
        :param row: Row index
        :param col: Column index
        :return: Set of tuples representing liberties (empty adjacent positions)
        """
        if self.grid[row][col] == 0:
            return set()  # No liberties for an empty position

        liberties = set()
        for neighbor in self.get_neighbors(row, col):
            r, c = neighbor
            if self.grid[r][c] == 0:  # Empty space
                liberties.add((r, c))
        return liberties

    def calculate_territories(self):
        """
        Calculate the territories for both players on the board.
        :return: Dictionary with territory counts for Black and White
        """
        visited = set()
        territories = {"black": 0, "white": 0}

        for row in range(self.size):
            for col in range(self.size):
                if (row, col) not in visited and self.grid[row][col] == 0:
                    territory, owner = self._explore_territory(row, col, visited)
                    if owner == 1:
                        territories["black"] += territory
                    elif owner == -1:
                        territories["white"] += territory

        return territories

    def _explore_territory(self, row, col, visited):
        """
        Explore a potential territory starting from a given position.
        :param row: Starting row index
        :param col: Starting column index
        :param visited: Set of already visited positions
        :return: (Size of the territory, Owner of the territory: 1 = Black, -1 = White, 0 = Neutral)
        """
        queue = [(row, col)]
        visited.add((row, col))
        territory_size = 0
        bordering_colors = set()

        while queue:
            r, c = queue.pop(0)
            territory_size += 1

            for neighbor in self.get_neighbors(r, c):
                nr, nc = neighbor
                if neighbor not in visited:
                    visited.add(neighbor)
                    if self.grid[nr][nc] == 0:
                        queue.append(neighbor)
                    else:
                        bordering_colors.add(self.grid[nr][nc])

        if len(bordering_colors) == 1:
            return territory_size, bordering_colors.pop()  # Controlled by one player
        return territory_size, 0  # Neutral territory

    def paintEvent(self, event):
        """
        Draw the board and pieces.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.draw_board(painter)
        self.draw_pieces(painter)

    def draw_board(self, painter):
        """
        Draw the grid and background.
        """
        # Draw background
        painter.setBrush(QColor(181, 137, 0))  # Golden background
        painter.drawRect(self.rect())

        # Draw grid lines
        pen = QPen(Qt.GlobalColor.black, 2)
        painter.setPen(pen)

        for i in range(self.size + 1):
            # Vertical lines
            x = i * self.cell_size
            painter.drawLine(x, 0, x, self.size * self.cell_size)
            # Horizontal lines
            y = i * self.cell_size
            painter.drawLine(0, y, self.size * self.cell_size, y)

    def draw_pieces(self, painter):
        """
        Draw the stones on the board.
        """
        for row in range(self.size):
            for col in range(self.size):
                piece = self.grid[row][col]
                if piece != 0:
                    self.draw_stone(painter, row, col, piece)

    def draw_stone(self, painter, row, col, piece):
        """
        Draw a single stone with a 3D effect.
        :param painter: QPainter instance
        :param row: Row index
        :param col: Column index
        :param piece: 1 for Black, -1 for White
        """
        center_x = col * self.cell_size + self.cell_size // 2
        center_y = row * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 2 - 5

        # Create gradient for 3D effect
        gradient = QRadialGradient(center_x, center_y, radius)
        if piece == 1:  # Black stone
            gradient.setColorAt(0, QColor(50, 50, 50))  # Dark center
            gradient.setColorAt(1, QColor(0, 0, 0))  # Black edges
        else:  # White stone
            gradient.setColorAt(0, QColor(255, 255, 255))  # White center
            gradient.setColorAt(1, QColor(200, 200, 200))  # Gray edges

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.GlobalColor.transparent)
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

    def __repr__(self):
        """
        String representation of the board for debugging.
        """
        board_representation = "\n".join(
            [" ".join(["●" if cell == 1 else "○" if cell == -1 else "." for cell in row]) for row in self.grid]
        )
        return f"Board:\n{board_representation}"

    def sizeHint(self):
        """
        Recommended size for the board widget.
        """
        return QSize(self.size * self.cell_size, self.size * self.cell_size)

    def minimumSizeHint(self):
        """
        Minimum size for the board widget.
        """
        return QSize(self.size * self.cell_size, self.size * self.cell_size)