"""
File: logic.py
Contains the core Go game rules logic:
- Placing stones with suicide rule & ko rule
- Capturing stones
- Tracking scores (captures + territory + komi)
- Undoing moves
- Passing & game over checks
"""

class GameLogic:
    def __init__(self, board_size):
        """
        Initialize the game logic with an empty board of the specified size.
        current_player = 1 (Black), -1 (White).
        pass_count tracks consecutive passes. 
        black_score and white_score track the raw count of captures only (for partial scoring).
        captured_stones is a dict to track how many stones each color has captured.
        previous_states is used to detect KO.
        """
        self.board_size = board_size
        self.reset_game()

    def reset_game(self):
        """
        Reset the game state to the initial state, clearing board, pass counts, scores, etc.
        """
        self.board_state = [[0] * self.board_size for _ in range(self.board_size)]
        self.current_player = 1  # 1 for Black, -1 for White
        self.pass_count = 0
        self.black_score = 0
        self.white_score = 0
        self.previous_states = []  # For KO rule prevention
        self.captured_stones = {"black": 0, "white": 0}

    def get_board_state_snapshot(self):
        """
        Return an immutable snapshot (tuple of tuples) of the board to check for repeated states (KO).
        """
        return tuple(tuple(row) for row in self.board_state)

    def get_board_state(self):
        """
        Return the current board state as a dictionary {(r, c): value}
        for easier consumption in the UI.
        """
        return {(r, c): self.board_state[r][c]
                for r in range(self.board_size)
                for c in range(self.board_size)}

    def place_stone(self, row, col):
        """
        Place a stone at (row, col) for the current_player.
        Returns None if invalid move, otherwise returns list of captured positions.
        Steps:
         1) Check bounds and emptiness
         2) Temporarily place stone
         3) Check suicide rule
         4) Check KO rule
         5) Capture opponent stones if any
         6) Save new board state in previous_states to prevent Ko
         7) Switch player, reset pass_count
        """
        if row < 0 or col < 0 or row >= self.board_size or col >= self.board_size:
            return None  # Out of bounds
        if self.board_state[row][col] != 0:
            return None  # Position already occupied

        # Temporarily place the stone
        self.board_state[row][col] = self.current_player

        # Check for suicide
        if self.is_suicide(row, col):
            # Undo the move
            self.board_state[row][col] = 0
            return None

        # Check for KO (repeated board state)
        snapshot_after_move = self.get_board_state_snapshot()
        if snapshot_after_move in self.previous_states:
            # Undo the move
            self.board_state[row][col] = 0
            return None

        # Capture opponent stones
        captured_positions = self.capture_stones(row, col)
        num_captured = len(captured_positions)

        # Update the scores for the current_player
        if self.current_player == 1:
            self.black_score += num_captured
            self.captured_stones["black"] += num_captured
        else:
            self.white_score += num_captured
            self.captured_stones["white"] += num_captured

        # Store this new state for KO rule prevention
        self.previous_states.append(snapshot_after_move)

        # Switch the player
        self.current_player *= -1
        # Because a stone was placed, reset pass_count
        self.pass_count = 0

        return captured_positions

    def capture_stones(self, row, col):
        """
        Capture any opponent stones that have no liberties after the current_player's move at (row,col).
        This function returns a list of captured positions for restoration if undone.
        """
        opponent = -self.current_player
        captured_positions = []

        # For each neighbor of the newly placed stone:
        neighbors = self.get_neighbors(row, col)
        for (nr, nc) in neighbors:
            if self.board_state[nr][nc] == opponent:
                # Check if that group of opponent stones has zero liberties
                visited = set()
                if self.count_liberties(nr, nc, visited) == 0:
                    # All stones in that group are captured
                    for (rr, cc) in visited:
                        self.board_state[rr][cc] = 0
                    captured_positions.extend(visited)

        return captured_positions

    def is_suicide(self, row, col):
        """
        Check if placing a stone at (row, col) for current_player results in no liberties
        for that stone or group, without capturing any opposing stones.
        If so, it's a suicide move.
        """
        # If we see that the group formed by (row,col) has zero liberties,
        # and we do NOT capture any opponent stones that would otherwise free us, it's suicide.
        visited = set()
        libs_before_capture = self.count_liberties(row, col, visited)
        if libs_before_capture > 0:
            return False  # We have at least one liberty => not suicide

        # Check if we would capture something that frees us. 
        # We can do a quick check by seeing if any neighbor is an opponent group with zero liberties.
        # If so, that group would be removed, giving us liberties => not suicide.
        opponent = -self.current_player
        neighbors = self.get_neighbors(row, col)
        for (nr, nc) in neighbors:
            if self.board_state[nr][nc] == opponent:
                visited_opp = set()
                if self.count_liberties(nr, nc, visited_opp) == 0:
                    # We would capture that group => not suicide
                    return False

        # If we get here, it means we have zero liberties and we do not capture any group => suicide
        return True

    def count_liberties(self, row, col, visited=None):
        """
        Count the number of liberties of the group containing the stone at (row, col).
        A liberty is an empty adjacent cell. 
        visited is a set used in DFS to avoid repeated checks.
        """
        if visited is None:
            visited = set()
        if (row, col) in visited:
            return 0

        visited.add((row, col))
        color = self.board_state[row][col]
        liberties = 0

        for (nr, nc) in self.get_neighbors(row, col):
            if self.board_state[nr][nc] == 0:
                liberties += 1
            elif self.board_state[nr][nc] == color:
                # Recursively check connected stones of same color
                liberties += self.count_liberties(nr, nc, visited)

        return liberties

    def get_neighbors(self, row, col):
        """
        Return the four orthogonal neighbors of (row, col) that are in bounds.
        """
        neighbors = []
        if row > 0:
            neighbors.append((row - 1, col))
        if row < self.board_size - 1:
            neighbors.append((row + 1, col))
        if col > 0:
            neighbors.append((row, col - 1))
        if col < self.board_size - 1:
            neighbors.append((row, col + 1))
        return neighbors

    def is_ko(self):
        """
        (Unused in final) We do the immediate check in place_stone instead.
        """
        current_state = self.get_board_state_snapshot()
        return current_state in self.previous_states

    def pass_turn(self):
        """
        Increment pass_count and switch to the other player.
        If pass_count reaches 2 => game over.
        """
        self.pass_count += 1
        self.current_player *= -1

    def is_game_over(self):
        """
        Return True if pass_count >= 2 => means two consecutive passes => game ends.
        """
        return self.pass_count >= 2

    def undo_stone(self, row, col, color_of_move, captured_positions):
        """
        Undo the last move:
         - Remove the placed stone (row,col)
         - Restore any captured stones
         - Adjust the player's capture count accordingly
         - Switch current_player back
         - We also remove the last snapshot from previous_states to revert Ko logic.
        """
        # Remove the placed stone
        self.board_state[row][col] = 0

        # Re-add any captured stones for the opponent
        opponent = -color_of_move
        for (rr, cc) in captured_positions:
            self.board_state[rr][cc] = opponent

        # Decrease the capturing player's score accordingly
        # Because we are undoing that capture
        if color_of_move == 1:
            self.black_score -= len(captured_positions)
            self.captured_stones["black"] -= len(captured_positions)
        else:
            self.white_score -= len(captured_positions)
            self.captured_stones["white"] -= len(captured_positions)

        # Switch current_player back to the undone player
        self.current_player = color_of_move

        # Also remove the last board snapshot from previous_states if present
        # so that the next placement won't fail KO rule incorrectly.
        if self.previous_states:
            self.previous_states.pop()

    def calculate_territories(self):
        """
        Calculates territory on the current board.
        Returns a dict { 'black': x, 'white': y }
        """
        visited = set()
        territories = {"black": 0, "white": 0}

        for r in range(self.board_size):
            for c in range(self.board_size):
                if (r, c) not in visited and self.board_state[r][c] == 0:
                    territory, owner = self._explore_territory(r, c, visited)
                    if owner == 1:
                        territories["black"] += territory
                    elif owner == -1:
                        territories["white"] += territory
        return territories

    def _explore_territory(self, row, col, visited):
        """
        BFS/DFS to find connected empty space and see which color encloses it.
        If exactly one color is touching this empty space, it's that color's territory.
        If more than one color touches it, it's neutral.
        """
        queue = [(row, col)]
        visited.add((row, col))
        territory_size = 0
        bordering_colors = set()

        while queue:
            r, c = queue.pop(0)
            territory_size += 1

            for (nr, nc) in self.get_neighbors(r, c):
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    if self.board_state[nr][nc] == 0:
                        queue.append((nr, nc))
                    else:
                        bordering_colors.add(self.board_state[nr][nc])

        if len(bordering_colors) == 1:
            return (territory_size, bordering_colors.pop())
        else:
            return (territory_size, 0)  # neutral or multiple colors

    def get_current_player(self):
        """
        Return the current player: 1 (Black) or -1 (White).
        """
        return self.current_player

    def get_scores(self):
        """
        Return a dictionary containing partial scores for black & white:
         black = black_score + capturedStones + territory
         white = white_score + capturedStones + territory
        (Komi is not applied here; this is for 'in-progress' display.)
        """
        territories = self.calculate_territories()
        partial_black = self.black_score + self.captured_stones["black"] + territories["black"]
        partial_white = self.white_score + self.captured_stones["white"] + territories["white"]
        return {
            "black": partial_black,
            "white": partial_white
        }

    def get_final_scores(self, territories):
        """
        Return final scores, factoring in a Komi of 6.5 for White.
        e.g. for end-of-game display.
        """
        final_black_score = self.black_score + self.captured_stones["black"] + territories["black"]
        final_white_score = self.white_score + self.captured_stones["white"] + territories["white"] + 6.5
        return {
            "black": final_black_score,
            "white": final_white_score
        }
