from components import *
from exceptions import *
import copy


class Checkers:
    """
    A class of Checkers game.

    class variables:
        default_width - default width of the board,
        pieces_per_player - number of pieces for each player,
        draw_amount - number of rounds with non-attacking king moves before draw

    attributes:
        board - board of cells (class Board),
        player1 - player with white pieces (class Player),
        player2 - player with red pieces (class Player),
        current_player - currently playing player (class Player),
        winner - winner of the game (None or class Player),
        king_moves_since_last_attack - used in draw checking (int),
        blocked_cells - a set of cells removed in the current round (set of tuples (int row, int col),
        must_continue - whether a player must continue his move (bool)
    """

    default_width = 8
    pieces_per_player = 12
    draw_amount = 15

    def __init__(
        self,
        init_players=True,
        init_board=True,
        player_arguments=({}, {}),
        board_arguments=None,
        arrange_pieces=True,
    ):
        if board_arguments is None:
            board_arguments = {}
        if init_players:
            self.player1 = Player(**(player_arguments[0]))
            self.player2 = Player(**(player_arguments[1]))
        else:
            self.player1 = None  # upper player - white pieces
            self.player2 = None  # lower player - red pieces
        self.current_player = self.player1
        self.winner = None
        self.king_moves_since_last_attack = 0
        self.blocked_cells = set()
        self.must_continue = False
        if init_board:
            if len(board_arguments) == 0:
                self.board = Board(width=type(self).default_width)
            elif len(board_arguments) == 1:
                if "width" in board_arguments.keys():
                    self.board = Board(width=board_arguments["width"])
                else:
                    self.board = Board(width=self.default_width, **board_arguments)
            elif len(board_arguments) >= 2:
                if "width" not in board_arguments.keys():
                    self.board = Board(
                        width=type(self).default_width, **board_arguments
                    )
                else:
                    self.board = Board(**board_arguments)
            if arrange_pieces:
                self.arrange_pieces()
        else:
            self.board = None

    @staticmethod
    def is_jump(orig, dest):
        return abs(orig[0] - dest[0]) > 1

    @staticmethod
    def direction(orig, dest):
        row = 1
        col = 1
        if dest[0] - orig[0] < 0:
            row = -1
        if dest[1] - orig[1] < 0:
            col = -1
        return row, col

    def other_player(self, player):
        if player == self.player1:
            return self.player2
        else:
            return self.player1

    def next_player(self):
        assert not self.must_continue, "Current player must continue his moves."
        for row, col in self.blocked_cells:
            self.board[row][col].unblock()
        self.blocked_cells.clear()
        self.calculate_winner()
        self.current_player = self.other_player(self.current_player)

    def arrange_pieces(self):
        self.player1.pieces.clear()
        self.player2.pieces.clear()
        for p in range(type(self).pieces_per_player):
            row = (2 * p) // self.board.width
            while row >= self.board.width:
                row -= 1
            if row % 2 == 0:
                col = (2 * p + 1) % self.board.width
            else:
                col = (2 * p) % self.board.width

            piece = self.board.cells[row][col].piece = Piece(self.player1)
            self.player1.pieces.add(piece)

            row = self.board.width - row - 1
            col = self.board.width - col - 1

            piece = self.board.cells[row][col].piece = Piece(self.player2)
            self.player2.pieces.add(piece)

    def is_end_of_game(self):
        if self.king_moves_since_last_attack > self.draw_amount:
            # draw
            self.winner = None
            return True
        return self.winner is not None

    def get_score(self, player=None):
        if player is None:
            player = self.current_player
        val = 0

        for piece in self.player1.pieces:
            if piece.is_king():
                val += 2
            else:
                val += 1

        for piece in self.player2.pieces:
            if piece.is_king():
                val -= 2
            else:
                val -= 1

        if player == self.player1:
            return val
        else:
            return -val

    def calculate_winner(self):
        other_player = self.other_player(self.current_player)
        # check amount of pieces
        if len(other_player.pieces) == 0:
            self.winner = self.current_player
            return
        if len(other_player.pieces) == 0:
            self.winner = other_player
            return
        # check if any player is blocked
        can_move = False
        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell.piece in other_player.pieces:
                    if len(self.possible_moves((i, j))):
                        can_move = True
                        break
            if can_move:
                break
        if not can_move:
            self.winner = self.current_player
        can_move = False
        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell.piece in self.current_player.pieces:
                    if len(self.possible_moves((i, j))):
                        can_move = True
                        break
            if can_move:
                break
        if not can_move:
            self.winner = other_player

    def remove_piece(self, piece):
        if isinstance(piece, Piece):
            for player in (self.player1, self.player2):
                if piece in player.pieces:
                    player.pieces.remove(piece)
            for row, row_of_pieces in enumerate(self.board):
                for col, cell in enumerate(row_of_pieces):
                    if cell.piece == piece:
                        self.blocked_cells.add((row, col))
                        cell.block()
        elif isinstance(piece, tuple):
            assert len(piece) == 2, f"Wrong piece tuple: {piece}"
            row = piece[0]
            col = piece[1]
            assert self.board.in_bounds(row, col)
            self.blocked_cells.add((row, col))
            self.board[row][col].block()
            cell = self.board[row][col]
            if cell.has_piece():
                for player in (self.player1, self.player2):
                    if cell.piece in player.pieces:
                        player.pieces.remove(cell.piece)
        self.board.remove_piece(piece)

    def get_directions(self, player, all_directions):
        if all_directions:
            return ((-1, -1), (-1, 1), (1, 1), (1, -1))
        if player == self.player1:
            return ((1, -1), (1, 1))
        return ((-1, 1), (-1, -1))

    def move(self, orig, dest):
        """
        Move cell from orig to dest.
        :param orig: origin, (tuple of coordinates - row, column)
        :param dest: destination (tuple of coordinates - row, column)
        :return: whether the move must continue in this round (bool)
        """
        assert self.board.in_bounds(*orig)
        assert self.board.in_bounds(*dest)
        row, col = orig
        dest_row, dest_col = dest
        cell = self.board[row][col]
        assert cell.has_piece(), f"{orig} -> {dest}: Cannot move empty cell."
        assert self.board[dest_row][
            dest_col
        ].is_empty(), f"{orig} -> {dest}: Cannot move into non-empty cell."
        is_attack = False
        if self.is_jump(orig, dest):
            player = self.board.cells[row][col].piece.parent
            enemies = self.enemies_between(orig, dest, player)
            if cell.piece.is_king() and len(enemies) == 0:
                self.king_moves_since_last_attack += 1
            else:
                self.king_moves_since_last_attack = 0
            for enemy in enemies:
                is_attack = True
                self.remove_piece(enemy)
        self.board[row][col], self.board[dest_row][dest_col] = (
            self.board[dest_row][dest_col],
            self.board[row][col],
        )
        if (cell.piece.parent != self.player1 and dest_row == 0) or (
            cell.piece.parent == self.player1 and dest_row == self.board.width - 1
        ):
            if not cell.piece.is_king():
                if not self.can_attack(dest):
                    cell.piece.set_king()
                    self.must_continue = False
                else:
                    self.must_continue = True
                self.calculate_winner()
                return self.must_continue
        if is_attack:
            self.must_continue = self.can_attack(dest)
        else:
            self.must_continue = False
        self.calculate_winner()
        return self.must_continue

    def enemies_between(self, orig, dest, player):
        """
        Get a list of enemies between given cells
        :param orig: origin, (tuple of coordinates - row, column)
        :param dest: destination (tuple of coordinates - row, column)
        :param player: player of the piece in the orig
        :return: a list of positions of enemies (tuples of coordinates - row, column)
        """
        row, col = orig
        direction = self.direction(orig, dest)
        temp_row, temp_col = row + direction[0], col + direction[1]
        enemies = []
        while (temp_row, temp_col) != dest:
            cell = self.board[temp_row][temp_col]
            if cell.has_piece() and cell.piece.parent != player:
                enemies.append((temp_row, temp_col))
            temp_row, temp_col = temp_row + direction[0], temp_col + direction[1]
        return enemies

    def possible_moves(self, place):
        """
        Get possible moves from the given position.
        :param place: position (tuple of coordinates - row, column)
        :return: a list of destination positions (tuples of coordinates - row, column)
        """
        row, col = place
        assert self.board.in_bounds(row, col)
        if not self.board[row][col].has_piece():
            raise WrongPositionException(place)
        piece = self.board[row][col].piece
        player = piece.parent
        if piece.is_king():
            attacks = self.possible_king_attacks(place, player)
            if len(attacks) > 0:
                return attacks
            return self.possible_king_moves(place, player)
        attacks = self.possible_normal_attacks(place, player)
        if len(attacks):
            return attacks
        return self.possible_normal_moves(place, player)

    def possible_normal_moves(self, place, player):
        """
        Get non-attacking moves of a non-king piece.
        :param place: position (tuple of coordinates - row, column)
        :param player: player of the piece
        :return: a list of destination positions (tuples of coordinates - row, column)
        """
        row, col = place
        directions = self.get_directions(player, False)
        moves = []
        for direction in directions:
            new_row, new_col = row + direction[0], col + direction[1]
            if not self.board.in_bounds(new_row, new_col):
                continue
            cell = self.board[new_row][new_col]
            if cell.is_empty():
                moves.append((new_row, new_col))
        return moves

    def possible_king_moves(self, place, player):
        """
        Get non-attacking moves of a king piece.
        :param place: position (tuple of coordinates - row, column)
        :param player: player of the piece
        :return: a list of destination positions (tuples of coordinates - row, column)
        """
        row, col = place
        directions = self.get_directions(player, True)
        moves = []
        for direction in directions:
            new_row, new_col = row, col
            while True:
                new_row, new_col = new_row + direction[0], new_col + direction[1]
                if not self.board.in_bounds(new_row, new_col):
                    break
                cell = self.board[new_row][new_col]
                if cell.is_blocked():
                    break
                if cell.is_empty():
                    moves.append((new_row, new_col))
        return moves

    def can_attack(self, place, player=None):
        """
        Whether player can attack from the given position.
        :param place: position (tuple of coordinates - row, column)
        :param player: player of the piece (optional - can be deduced)
        :return: bool
        """
        if player is None:
            row, col = place
            if self.board[row][col].piece in self.player1.pieces:
                player = self.player1
            else:
                player = self.player2
        return len(self.possible_attacks(place, player)) > 0

    def possible_attacks(self, place, player=None):
        """
        Get attacking moves of a piece.
        :param place: position (tuple of coordinates - row, column)
        :param player: player of the piece (optional - can be deduced)
        :return: a list of destination positions (tuples of coordinates - row, column)
        """
        row, col = place
        if player is None:
            if self.board[row][col].piece in self.player1.pieces:
                player = self.player1
            else:
                player = self.player2

        if self.board[row][col].piece.is_king():
            return self.possible_king_attacks(place, player)
        else:
            return self.possible_normal_attacks(place, player)

    def possible_normal_attacks(self, place, player):
        """
        Get attacking moves of a non-king piece.
        :param place: position (tuple of coordinates - row, column)
        :param player: player of the piece
        :return: a list of destination positions (tuples of coordinates - row, column)
        """
        row, col = place
        directions = self.get_directions(player, True)
        attacks = []
        max_depth = 0
        for direction in directions:
            new_row, new_col = row, col
            is_attack = False
            while True:
                new_row, new_col = new_row + direction[0], new_col + direction[1]
                if not self.board.in_bounds(new_row, new_col):
                    break
                cell = self.board[new_row][new_col]
                if not is_attack:
                    if cell.is_empty() or cell.piece.parent == player:
                        break
                    else:
                        is_attack = True
                elif cell.is_empty():
                    ignored = set()
                    if row == 0 or row == self.board.width:
                        attacks.append((new_row, new_col))
                        break
                    d = self._normal_attack_depth(
                        (new_row, new_col), player, 0, ignored
                    )
                    if d > max_depth:
                        attacks = [(new_row, new_col)]
                        max_depth = d
                    elif d == max_depth:
                        attacks.append((new_row, new_col))
                    break
                else:
                    break
        return attacks

    def _normal_attack_depth(self, place, player, depth, ignored):
        """
        Function used internally. Get depth of the maximum attack from the given position (for non-king piece).
        :param place: position (tuple of coordinates - row, column)
        :param player: player of the piece
        :param depth: depth of the attack
        :param ignored: ignored piece positions (pieces attacked in previous attacks)
        :return: maximum depth of the attack
        """
        row, col = place
        directions = self.get_directions(player, True)
        max_depth = depth
        for direction in directions:
            new_row, new_col = row, col
            is_attack = False
            while True:
                new_row, new_col = new_row + direction[0], new_col + direction[1]
                if not self.board.in_bounds(new_row, new_col):
                    break
                if (new_row, new_col) in ignored:
                    break
                cell = self.board[new_row][new_col]
                if cell.is_blocked():
                    break
                if not is_attack:
                    if cell.is_empty() or cell.piece.parent == player:
                        break
                    else:
                        is_attack = True
                elif cell.is_empty():
                    copied_ignored = copy.copy(ignored)
                    copied_ignored.add((new_row - direction[0], new_col - direction[1]))
                    d = self._normal_attack_depth(
                        (new_row, new_col), player, depth + 1, copied_ignored
                    )
                    max_depth = max(max_depth, d)
                else:
                    break
        return max_depth

    def possible_king_attacks(self, place, player):
        """
        Get attacking moves of a king piece.
        :param place: position (tuple of coordinates - row, column)
        :param player: player of the piece
        :return: a list of destination positions (tuples of coordinates - row, column)
        """
        row, col = place
        directions = self.get_directions(player, True)
        attacks = []
        max_depth = 0
        blocked = False
        for direction in directions:
            new_row, new_col = row, col
            is_attack = False
            attacked_pieces = set()
            while True:
                new_row, new_col = new_row + direction[0], new_col + direction[1]
                if not self.board.in_bounds(new_row, new_col):
                    break
                cell = self.board[new_row][new_col]
                if cell.is_blocked():
                    break
                if not is_attack:
                    if cell.has_piece():
                        if cell.piece.parent == player:
                            break
                        else:
                            attacked_pieces.add((new_row, new_col))
                            is_attack = True
                            blocked = True
                elif cell.has_piece():
                    if cell.piece.parent == player or blocked:
                        break
                    attacked_pieces.add((new_row, new_col))
                else:
                    blocked = False
                    ignored = copy.copy(attacked_pieces)
                    d = self._king_attack_depth((new_row, new_col), player, 0, ignored)
                    if d > max_depth:
                        max_depth = d
                        attacks = [(new_row, new_col)]
                    elif d == max_depth:
                        attacks.append((new_row, new_col))
        return attacks

    def _king_attack_depth(self, place, player, depth, ignored):
        """
        Function used internally. Get depth of the maximum attack from the given position (for king piece).
        :param place: position (tuple of coordinates - row, column)
        :param player: player of the piece
        :param depth: depth of the attack
        :param ignored: ignored piece positions (pieces attacked in previous attacks)
        :return: maximum depth of the attack
        """
        row, col = place
        directions = self.get_directions(player, True)
        max_depth = depth
        for direction in directions:
            new_row, new_col = row, col
            is_attack = False
            attacked_piece = None
            while True:
                new_row, new_col = new_row + direction[0], new_col + direction[1]
                if not self.board.in_bounds(new_row, new_col):
                    break
                if (new_row, new_col) in ignored or (
                    new_row,
                    new_col,
                ) in self.blocked_cells:
                    break
                cell = self.board[new_row][new_col]
                if not is_attack:
                    if cell.has_piece():
                        if cell.piece.parent == player:
                            break
                        else:
                            attacked_piece = (new_row, new_col)
                            is_attack = True
                elif cell.is_empty():
                    copied_ignored = copy.copy(ignored)
                    copied_ignored.add(attacked_piece)
                    d = self._king_attack_depth(
                        (new_row, new_col), player, depth + 1, copied_ignored
                    )
                    max_depth = max(max_depth, d)
                else:
                    break
        return max_depth

    def get_possible_moves(self, player):
        """
        Get possible moves for the player in this round.
        :param player: player of the game
        :return: a list of moves (move is a tuple of positions: origin, destination - positions are
            tuples of coordinates: row, column)
        """
        moves = set()
        is_attack = False
        for row, row_of_pieces in enumerate(self.board):
            for col, cell in enumerate(row_of_pieces):
                if cell.has_piece() and cell.piece.parent == player:
                    if self.can_attack((row, col), cell.piece.parent):
                        if not is_attack:
                            moves = set()
                            is_attack = True
                        for move in self.possible_moves((row, col)):
                            moves.add(((row, col), move))
                    elif not is_attack:
                        for move in self.possible_moves((row, col)):
                            moves.add(((row, col), move))
        return moves

    def __str__(self):
        string = f"Current player: {self.current_player}\n"
        if self.board is not None:
            string += str(self.board)
        return string

    def __repr__(self):
        return f"Checkers({self.player1.__repr__()}, {self.player2.__repr__()})"
