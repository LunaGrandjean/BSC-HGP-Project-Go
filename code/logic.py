class GameLogic:
    def __init__(self, board_size):
        """
        Initialize the game logic with an empty board and default settings.
        """
        self.board_size = board_size
        self.reset_game()

    def reset_game(self):
        """
        Reset the game state to the initial state.
        """
        self.board_state = [[0] * self.board_size for _ in range(self.board_size)]
        self.current_player = 1  # 1 for Black, -1 for White
        self.pass_count = 0
        self.black_score = 0
        self.white_score = 0

    def place_stone(self, row, col):
        """
        Place a stone on the board. Returns True if the move is valid, False otherwise.
        """
        if row < 0 or col < 0 or row >= self.board_size or col >= self.board_size:
            return False  # Out of bounds

        if self.board_state[row][col] != 0:
            return False  # Spot already taken

        # Temporarily place the stone
        self.board_state[row][col] = self.current_player

        # Check for suicide
        if self.is_suicide(row, col):
            self.board_state[row][col] = 0  # Undo the move
            return False  # Invalid move

        # Capture opponent stones if applicable
        captured = self.capture_stones(row, col)
        if self.current_player == 1:
            self.black_score += captured
        else:
            self.white_score += captured

        # Switch to the other player
        self.current_player *= -1
        return True

    def is_suicide(self, row, col):
        """
        Check if placing a stone at (row, col) is a suicide.
        """
        if self.count_liberties(row, col) > 0:
            return False  # Not a suicide if there are liberties

        # Check if the move captures any opponent stones
        opponent = -self.current_player
        for neighbor in self.get_neighbors(row, col):
            r, c = neighbor
            if self.board_state[r][c] == opponent and self.count_liberties(r, c) == 0:
                return False  # Not a suicide if it captures opponent stones

        return True

    def capture_stones(self, row, col):
        """
        Capture any opponent groups with no liberties after a move.
        """
        opponent = -self.current_player
        captured_positions = []

        for neighbor in self.get_neighbors(row, col):
            r, c = neighbor
            if self.board_state[r][c] == opponent:
                visited = set()
                if self.count_liberties(r, c, visited) == 0:
                    captured_positions.extend(visited)

        # Remove captured stones from the board
        for r, c in captured_positions:
            self.board_state[r][c] = 0

        return len(captured_positions)

    def count_liberties(self, row, col, visited=None):
        """
        Count the number of liberties (empty adjacent spaces) for the stone at (row, col).
        """
        if visited is None:
            visited = set()

        if (row, col) in visited:
            return 0
        visited.add((row, col))

        liberties = 0
        for neighbor in self.get_neighbors(row, col):
            r, c = neighbor
            if self.board_state[r][c] == 0:  # Empty space
                liberties += 1
            elif self.board_state[r][c] == self.board_state[row][col]:  # Connected stone
                liberties += self.count_liberties(r, c, visited)

        return liberties

    def get_neighbors(self, row, col):
        """
        Get all valid neighbors of a cell at (row, col).
        """
        neighbors = []
        if row > 0:
            neighbors.append((row - 1, col))  # Top
        if row < self.board_size - 1:
            neighbors.append((row + 1, col))  # Bottom
        if col > 0:
            neighbors.append((row, col - 1))  # Left
        if col < self.board_size - 1:
            neighbors.append((row, col + 1))  # Right
        return neighbors

    def get_board_state(self):
        """
        Return the current state of the board as a dictionary.
        """
        return {(r, c): self.board_state[r][c] for r in range(self.board_size) for c in range(self.board_size)}

    def get_current_player(self):
        """
        Return the current player (1 for Black, -1 for White).
        """
        return self.current_player

    def get_scores(self):
        """
        Return the current scores as a dictionary.
        """
        return {"black": self.black_score, "white": self.white_score}
