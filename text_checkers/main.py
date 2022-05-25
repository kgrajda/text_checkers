#!/usr/bin/python3

import sys
from TextCheckers import TextCheckers
from alphabeta import alphabeta
from components import Piece
from State import State


def set_piece(game, place, player):
    """Helper function. Put new piece on the given  position."""
    row, col = place
    game.board[row][col].piece = Piece(player)
    player.pieces.add(game.board[row][col].piece)


def test_particular_situation():
    game = TextCheckers("me", "ai", False)
    """
    # king beats 5 pieces - 2 possible attacks
    set_piece(game, (0, 1), game.player1)
    game.board[0][1].piece.set_king()
    set_piece(game, (1, 2), game.player2)
    set_piece(game, (1, 4), game.player2)
    set_piece(game, (1, 6), game.player2)
    set_piece(game, (6, 1), game.player2)
    set_piece(game, (6, 3), game.player2)
    """

    """
    # 2 possible moves - changed to king
    set_piece(game, (3, 4), game.player1)
    set_piece(game, (4, 3), game.player2)
    set_piece(game, (6, 1), game.player2)
    set_piece(game, (6, 3), game.player2)
    """

    """
    # piece not changed to king
    set_piece(game, (5, 2), game.player1)
    set_piece(game, (6, 1), game.player2)
    set_piece(game, (6, 3), game.player2)
    set_piece(game, (6, 5), game.player2)
    """

    # '''
    # king cannot jump over the same piece two times in the same round - ai wins
    set_piece(game, (0, 3), game.player1)
    game.board[0][3].piece.set_king()
    set_piece(game, (1, 2), game.player1)
    set_piece(game, (2, 5), game.player2)
    set_piece(game, (4, 3), game.player2)
    set_piece(game, (4, 5), game.player2)
    set_piece(game, (5, 6), game.player2)
    set_piece(game, (6, 3), game.player2)
    # '''

    game_loop(game)
    print(interpret_game_result(game))
    return 0


def interpret_game_result(game):
    """Helper function. Interpreting the game result as a string."""
    if game.is_end_of_game():
        if game.winner is None:
            return "State of the game: draw."
        return f"Winner: {game.winner}. {'Congratulations!' if game.winner == game.player1 else ''}"
    return "State of the game: unfinished."


def game_loop(game):
    while True:
        try:
            print(game, end="")
            if game.is_end_of_game():
                break
            game.get_input_and_make_move()
            while game.must_continue:
                print(game, end="")
                game.get_input_and_make_move("Continue your move: ")
            print(f"{game.player1} score: {game.get_score(game.player1)}")
            game.next_player()
            print(game, end="")
            if game.is_end_of_game():
                break

            state = State(game)
            alphabeta(state, 3)
            state.apply_moves(game)

            print(f"{game.player2} moved: ", end="")
            if state.next is not None:
                if len(state.next.moves) > 0:
                    print(game.tr_back(state.next.moves[0][0]), end="")
                for _move in state.next.moves:
                    _, dest = _move
                    print(f" -> {game.tr_back(dest)}", end="")
                print()

            game.next_player()
        except KeyboardInterrupt:
            print(f"{game.player1} score: {game.get_score(game.player1)}")
            print("Exiting...")
            break
        except Exception as e:
            print(e)
            break


def main():
    print("Welcome to TextCheckers game by Krzysztof Grajda!\n")
    c = TextCheckers("me", "ai")

    try:
        c.ai_depth = int(input("Maximum depth of the alpha-beta algorithm: "))
        print()
    except Exception as e:
        print(e)
        print(f"Assuming default value of depth: {c.ai_depth}\n")

    print('Type "q", "quit" or "exit" to terminate program at any point in time.')
    print('Type "p", "h" or "help" to get possible moves.\n')

    game_loop(c)

    print(interpret_game_result(c))
    return 0


if __name__ == "__main__":
    sys.exit(main())
    # sys.exit(test_particular_situation())
