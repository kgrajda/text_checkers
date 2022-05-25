from Checkers import Checkers
import copy


class State:
    """
    A class that holds a complete copy of the Checkers game.

    attributes:
        game - copy (deepcopy) of the game
        next - a state assigned in an alphabeta algorithm as the best child state
        moves - a list of moves to achieve the given state from the primary state (primary state holds an empty list)
    """

    def __init__(self, game: Checkers):
        self.game = copy.deepcopy(game)  # copy the board and players as new objects
        self.next = None
        self.moves = []

    def get_score(self):
        return self.game.get_score(self.game.player1)

    def is_end_of_game(self):
        return self.game.is_end_of_game()

    def is_player1_playing(self):
        return self.game.current_player == self.game.player1

    def get_children(self):
        moves = self.game.get_possible_moves(self.game.current_player)
        children = []
        for move in moves:
            current_pos, dest_pos = move
            child = copy.deepcopy(self)
            # move method return value tells whether the player must continue the move
            still_moving = child.game.move(current_pos, dest_pos)
            child.moves.append((current_pos, dest_pos))
            while still_moving:
                current_pos = dest_pos
                _moves = child.game.possible_moves(current_pos)
                dest_pos = _moves[0]
                if len(_moves) > 1:
                    for _move in _moves[1:]:
                        another_child = copy.deepcopy(child)
                        type(self)._add_another_move(
                            children, another_child, current_pos, _move
                        )
                still_moving = child.game.move(current_pos, dest_pos)
                child.moves.append((current_pos, dest_pos))
            child.game.next_player()
            children.append(child)
        return children

    @classmethod
    def _add_another_move(cls, list_of_children, child, current_pos, dest_pos):
        still_moving = child.game.move(current_pos, dest_pos)
        child.moves.append((current_pos, dest_pos))
        while still_moving:
            moves = child.game.possible_moves(current_pos)
            if len(moves) > 1:
                for move in moves[1:]:
                    another_child = copy.deepcopy(child)
                    cls._add_another_move(
                        list_of_children, another_child, current_pos, move
                    )
            still_moving = child.game.move(current_pos, dest_pos)
            child.moves.append((current_pos, dest_pos))
        child.game.next_player()
        list_of_children.append(child)

    def apply_moves(self, game):
        state = self
        if state.next is not None:
            for move in state.next.moves:
                game.move(*move)

    def __str__(self):
        return f"state: {self.game}"

    def __repr__(self):
        return f"state: {self.game.__repr__()}"
