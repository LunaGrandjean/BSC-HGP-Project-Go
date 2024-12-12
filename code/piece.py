class Piece:
    def __init__(self, color, position):
        """
        Initialize a Piece with a color and position.
        :param color: 1 for Black, -1 for White
        :param position: Tuple (row, col) representing the position on the board
        """
        self.color = color  # 1 for Black, -1 for White
        self.position = position  # (row, col)
        self.liberties = set()  # Set of liberties (empty adjacent positions)
        self.group = None  # Reference to the group this piece belongs to

    def set_liberties(self, liberties):
        """
        Set the liberties of this piece.
        :param liberties: Set of tuples representing empty adjacent positions
        """
        self.liberties = liberties

    def remove_liberty(self, position):
        """
        Remove a specific position from the liberties.
        :param position: Tuple (row, col) of the position to remove
        """
        if position in self.liberties:
            self.liberties.remove(position)

    def add_liberty(self, position):
        """
        Add a specific position to the liberties.
        :param position: Tuple (row, col) of the position to add
        """
        self.liberties.add(position)

    def is_captured(self):
        """
        Check if the piece is captured (no liberties remaining).
        :return: True if captured, False otherwise
        """
        return len(self.liberties) == 0

    def __repr__(self):
        """
        String representation of the Piece for debugging.
        """
        color = "Black" if self.color == 1 else "White"
        return f"Piece({color}, Position={self.position}, Liberties={len(self.liberties)})"
