class Piece:
    """
    A class representing a piece on the Checkers board.

    attributes:
        parent - player owning the piece (class Player)
        _is_king - whether the piece is king (bool)
    """

    def __init__(self, parent=None):
        self.parent = parent
        self._is_king = False

    def is_king(self):
        return self._is_king

    def set_king(self):
        self._is_king = True

    def __str__(self):
        return f"{self.parent}({'k' if self.is_king() else 'm'})"

    def __repr__(self):
        return self.__str__()


class Cell:
    """
    A class representing a cell in the Checkers board.

    attributes:
        piece - piece inside the cell (class Piece)
        blocked - whether the cell allows an attack to be performed on the cell (bool)
    """

    def __init__(self, piece=None):
        self.piece = piece
        self.blocked = False

    def has_piece(self):
        return self.piece is not None

    def is_empty(self):
        return self.piece is None

    def empty(self):
        self.piece = None

    def set_piece(self, piece):
        self.piece = piece

    def is_blocked(self):
        return self.blocked

    def block(self):
        self.blocked = True

    def unblock(self):
        self.blocked = False

    def __str__(self):
        return str(self.piece) if self.has_piece() else "_____"

    def __repr__(self):
        return self.__str__()


class Player:
    """
    A class representing a player in the Checkers game.

    static variables:
        num - unique id of the next created player (if name is not specified) (int)

    attributes:
        name - username (str)
        pieces - a set of pieces (set of class Piece entities)
    """

    num = 0

    def __init__(self, name=None):
        self.name = name if name is not None else f"p{type(self).num + 1}"
        self.pieces = set()
        type(self).num += 1

    def is_alive(self):
        return True if len(self.pieces) else False

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Board:
    """
    A class representing a Checkers board.

    attributes:
        width - width and height of the board (int)
        cells - a list of rows - rows are lists of cells (list(list(class Cell)))
    """

    def __init__(self, width, cell_arguments=None):
        self.width = width
        self.cells = None
        self.create_board(cell_arguments)

    def create_board(self, cell_arguments=None):
        if cell_arguments is None:
            cell_arguments = {}
        self.cells = [
            [Cell(**cell_arguments) for h in range(self.width)]
            for w in range(self.width)
        ]

    def in_bounds(self, row, col):
        if 0 <= row < self.width and 0 <= col < self.width:
            return True
        else:
            return False

    def remove_piece(self, piece):
        if isinstance(piece, Piece):
            for r, row in enumerate(self.cells):
                for c, cell in enumerate(row):
                    if cell.piece == piece:
                        cell.piece.empty()
                        return
        elif isinstance(piece, tuple):
            assert len(piece) == 2, f"Wrong piece tuple: {piece}"
            row, col = piece
            assert self.in_bounds(row, col)
            cell = self.cells[row][col]
            self.cells[row][col].empty()
        else:
            raise Exception(f"Wrong piece type: {piece}")

    def __getitem__(self, row):
        # bracket operator
        return self.cells[row]  # returns a list - mutable - no need for __setitem__

    def __str__(self):
        string = "  \t"
        for i in range(self.width):
            string += "  " + chr(ord("a") + i) + "  \t"
        string += "\n"
        for i, row in enumerate(self.cells):
            string += f"{self.width - i}\t"
            for cell in row:
                string += f"{cell}\t"
            string += "\n"
        return string

    def __repr__(self):
        return f"Board of width {self.width}"
