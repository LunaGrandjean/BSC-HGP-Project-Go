"""
File: piece.py
Defines a simple Piece class that can hold color, position,
and track liberties. (Optional usage in advanced group tracking.)
"""

class Piece:
    def __init__(self, color, position):
        """
        Initialize a Piece with a color and position.
        :param color: 1 for Black, -1 for White
        :param position: Tuple (row, col)
        """
        self.color = color  # 1 for Black, -1 for White
        self.position = position  # (row, col)
        self.liberties = set()  # adjacent empty intersections
        self.group = None  # reference to the group this piece belongs to

    def set_liberties(self, liberties):
        """
        Set the liberties of this piece.
        :param liberties: set of (row, col) positions
        """
        self.liberties = liberties

    def remove_liberty(self, position):
        """
        Remove one liberty from the set.
        """
        if position in self.liberties:
            self.liberties.remove(position)

    def add_liberty(self, position):
        """
        Add one liberty to the set.
        """
        self.liberties.add(position)

    def is_captured(self):
        """
        Determine if the piece has zero liberties.
        """
        return len(self.liberties) == 0

    def __repr__(self):
        color_str = "Black" if self.color == 1 else "White"
        return f"Piece({color_str}, Position={self.position}, Liberties={len(self.liberties)})"
