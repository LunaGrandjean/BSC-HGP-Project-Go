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
        self.previous_states = []  # For KO rule prevention
        self.captured_stones = {"black": 0, "white": 0}

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

        # Check for KO rule (state repetition)
        if self.is_ko():
            self.board_state[row][col] = 0
            return False  # Invalid move due to KO rule

        # Capture opponent stones if applicable
        captured = self.capture_stones(row, col)
        if self.current_player == 1:
            self.black_score += captured
            self.captured_stones["black"] += captured
        else:
            self.white_score += captured
            self.captured_stones["white"] += captured

        # Save the current board state to prevent KO
        self.previous_states.append(self.get_board_state_snapshot())

        # Switch to the other player
        self.current_player *= -1
        self.pass_count = 0  # Reset pass count since a stone was placed
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

    def is_ko(self):
        """
        Check if the current board state repeats a previous state (KO rule).
        """
        current_state = self.get_board_state_snapshot()
        return current_state in self.previous_states

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

    def calculate_territories(self):
        """
        Calculate the territories for both players on the board.
        :return: Dictionary with territory counts for Black and White
        """
        visited = set()
        territories = {"black": 0, "white": 0}

        for row in range(self.board_size):
            for col in range(self.board_size):
                if (row, col) not in visited and self.board_state[row][col] == 0:
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
                    if self.board_state[nr][nc] == 0:
                        queue.append(neighbor)
                    else:
                        bordering_colors.add(self.board_state[nr][nc])

        if len(bordering_colors) == 1:
            return territory_size, bordering_colors.pop()  # Controlled by one player
        return territory_size, 0  # Neutral territory

    def pass_turn(self):
        """
        Handle a player passing their turn.
        """
        self.pass_count += 1
        self.current_player *= -1  # Switch player

    def is_game_over(self):
        """
        Check if the game is over (two consecutive passes).
        """
        return self.pass_count >= 2

    def get_board_state(self):
        """
        Return the current state of the board as a dictionary.
        """
        return {(r, c): self.board_state[r][c] for r in range(self.board_size) for c in range(self.board_size)}

    def get_board_state_snapshot(self):
        """
        Return a snapshot of the current board state for KO rule checking.
        """
        return tuple(tuple(row) for row in self.board_state)

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

    def get_current_player(self):
        """
        Return the current player (1 for Black, -1 for White).
        """
        return self.current_player

    def get_final_scores(self, territories):
        """
        Calculate the final scores including captured stones and territories.
        :param territories: Dictionary with territory counts for Black and White
        :return: Dictionary with final scores
        """
        final_black_score = self.black_score + self.captured_stones["black"] + territories["black"]
        final_white_score = self.white_score + self.captured_stones["white"] + territories["white"] + 6.5  # Komi for White
        return {
            "black": final_black_score,
            "white": final_white_score,
            "captured_black": self.captured_stones["black"],
            "captured_white": self.captured_stones["white"]
        }
    def get_scores(self):
        """
        Return the current scores including captured stones and territories.
        """
        territories = self.calculate_territories()
        return {
            "black": self.black_score + self.captured_stones["black"] + territories["black"],
            "white": self.white_score + self.captured_stones["white"] + territories["white"]
        }