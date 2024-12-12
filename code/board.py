class Board:
    def __init__(self, size):
        self.size = size
        self.grid = [[0] * size for _ in range(size)]

    def reset(self):
        self.grid = [[0] * self.size for _ in range(self.size)]
