class ScoreBoard:
    def __init__(self):
        self.black_score = 0
        self.white_score = 0

    def add_score(self, player, points):
        if player == 1:
            self.black_score += points
        else:
            self.white_score += points
