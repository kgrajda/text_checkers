from typing import Tuple
from exceptions import *
from State import State
from alphabeta import alphabeta
from Checkers import Checkers


class TextCheckers(Checkers):
    """
    A class that extends Checkers class. The game is playable through a text interface.

    attributes:
        ai_depth - depth of the AI algorithm used to help the player
    """

    def __init__(self, player1_name="p1", player2_name="p2", arrange_pieces=True):
        super().__init__(
            player_arguments=({"name": player1_name}, {"name": player2_name}),
            arrange_pieces=arrange_pieces,
        )
        self.ai_depth = 3

    @staticmethod
    def tr(place: str) -> Tuple[int, int]:
        """Translate text coordinates to tuple coordinates

        Args:
            place (str): text coordinate, ex. "b6"

        Raises:
            WrongPositionException: Impossible position (possibly out-of-bounds)

        Returns:
            Tuple[int, int]: Row, Column
        """
        if len(place) != 2:
            raise WrongPositionException(place)
        if ord("a") <= ord(place[0]) <= ord("h"):
            col = ord(place[0]) - ord("a")
        else:
            raise WrongPositionException(place)

        try:
            val = int(place[1])
        except ValueError:
            raise WrongPositionException(place)
        if 1 <= val <= 8:
            row = 8 - val
        else:
            raise WrongPositionException(place)

        return row, col

    @classmethod
    def tr_move(cls, move: str):
        move = "".join(move.split()).lower()  # strip from any whitespaces
        if len(move) != 6:
            raise WrongMoveException(move)
        if move[2:4] != "->":
            raise WrongMoveSyntax(move)
        return cls.tr(move[0:2]), cls.tr(move[4:6])

    @staticmethod
    def tr_back(place: Tuple[int, int], dest: Tuple[int, int] = None) -> str:
        """Translate position from tuple to text coordinate

        Args:
            place (Tuple[int, int]): (Row, Column) source position
            dest (Tuple[int, int], optional): (Row, Column) destination position.
                                              Defaults to None.

        Returns:
            str: text coordinate, ex. "b6"
        """
        row, col = place
        if dest is not None:
            dest_row, dest_col = dest
            return f"{chr(ord('a') + col)}{8 - row}->{chr(ord('a') + dest_col)}{8 - dest_row}"
        else:
            return f"{chr(ord('a') + col)}{8 - row}"

    def get_input_and_make_move(self, text=None):
        if text is None:
            text = "Your move: "
        while True:
            try:
                move = input(text)
                if move in ("q", "quit", "exit"):
                    raise KeyboardInterrupt()
                if move in ("p", "h", "help"):
                    while True:
                        try:
                            moves = self.get_possible_moves(self.current_player)
                            if len(moves) == 0:
                                print("No moves possible.")
                            else:
                                print("Possible moves:")
                                first_iter = True
                                for _move in moves:
                                    if first_iter:
                                        print(
                                            f"{self.tr_back(_move[0])} -> {self.tr_back(_move[1])}",
                                            end="",
                                        )
                                        first_iter = False
                                        continue
                                    print(
                                        f", {self.tr_back(_move[0])} -> {self.tr_back(_move[1])}",
                                        end="",
                                    )
                                print()
                                print("Alphabeta algorithm proposal: ", end="")
                                state = State(self)
                                alphabeta(state, 5)
                                if state.next is not None:
                                    if len(state.next.moves) > 0:
                                        print(
                                            self.tr_back(state.next.moves[0][0]), end=""
                                        )
                                    for _move in state.next.moves:
                                        _, dest = _move
                                        print(f" -> {self.tr_back(dest)}", end="")
                                print()
                            break
                        except WrongPositionException as e:
                            print(e)
                    continue
                place, dest = self.tr_move(move)
                row, col = place
                cell = self.board[row][col]
                if cell.is_empty():
                    raise EmptyCellException(move)
                if cell.piece.parent != self.current_player:
                    raise NotYourCellException(move)
                moves = self.get_possible_moves(self.current_player)
                if (place, dest) not in moves:
                    raise ImpossibleMoveException(move)
                self.must_continue = self.move(place, dest)
                break
            except WrongMoveException as e:
                print(e)
            except WrongPositionException as e:
                print(e)
