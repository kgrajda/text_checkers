from State import State


def alphabeta(state: State, depth, alpha=float("-inf"), beta=float("+inf")):
    if depth == 0 or state.is_end_of_game():
        return state.get_score()  # score of the player1
    U = state.get_children()
    if state.is_player1_playing():
        best_score = float("-inf")
        for u in U:
            score = alphabeta(u, depth - 1, alpha, beta)
            if score > best_score:
                state.next = u
                best_score = score
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        return best_score
    else:
        best_score = float("+inf")
        for u in U:
            score = alphabeta(u, depth - 1, alpha, beta)
            if score < best_score:
                state.next = u
                best_score = score
            beta = min(beta, score)
            if alpha >= beta:
                break
        return best_score
