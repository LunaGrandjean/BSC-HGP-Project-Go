"""
File: score_board.py
Implements a simple ScoreBoard class to track and calculate scores
(including territory, captures, etc.). This can be used or
you can rely on logic.py's internal approach. 
"""

class ScoreBoard:
    def __init__(self):
        """
        Initialize the scoreboard with basic zeroed-out fields.
        """
        self.black_score = 0
        self.white_score = 0
        self.captured_black = 0  # Stones captured by White
        self.captured_white = 0  # Stones captured by Black
        self.territories = {"black": 0, "white": 0}

    def add_score(self, player, points):
        """
        Add points to a player (1=Black, -1=White).
        """
        if player == 1:
            self.black_score += points
        else:
            self.white_score += points

    def add_captured_stone(self, player):
        """
        Increment the count of stones captured by the *opponent*.
        For example, if 'player'=1 (Black), then white captured a black stone => captured_black++ 
        """
        if player == 1:
            self.captured_white += 1
        else:
            self.captured_black += 1

    def calculate_final_score(self, komi=6.5):
        """
        Calculate the final score with captured stones + territory + komi for White.
        """
        final_black_score = self.black_score + self.captured_black + self.territories["black"]
        final_white_score = self.white_score + self.captured_white + self.territories["white"] + komi
        return {
            "black": final_black_score,
            "white": final_white_score
        }

    def update_territory(self, player, points):
        """
        Update the territory count for a given player (1=Black, -1=White).
        """
        if player == 1:
            self.territories["black"] += points
        else:
            self.territories["white"] += points

    def reset_scores(self):
        """
        Reset everything to zero.
        """
        self.black_score = 0
        self.white_score = 0
        self.captured_black = 0
        self.captured_white = 0
        self.territories = {"black": 0, "white": 0}

    def get_scores(self):
        """
        Return a dictionary of the scoreboard fields for debugging or display.
        """
        return {
            "black_score": self.black_score,
            "white_score": self.white_score,
            "captured_black": self.captured_black,
            "captured_white": self.captured_white,
            "territories": self.territories
        }

    def __repr__(self):
        """
        String representation for debugging.
        """
        return (
            f"ScoreBoard("
            f"Black Score: {self.black_score}, Captured by Black: {self.captured_black}, "
            f"Territories(Black): {self.territories['black']} | "
            f"White Score: {self.white_score}, Captured by White: {self.captured_white}, "
            f"Territories(White): {self.territories['white']})"
        )
