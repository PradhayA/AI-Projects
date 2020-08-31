from copy import deepcopy
import numpy
import math

O = "O"
X = "X"
EMPTY = None


def transpose(board):
    new_board = deepcopy(board)
    new_board = zip(*new_board)
    return new_board


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if any(any(item != EMPTY for item in row) for row in board) or winner(board) or all(all(item != EMPTY for item in row) for row in board) :  # Keeps going through this conditional as long as
        # there are still empty spots

        array = numpy.array(board)  # Creates an array
        O_frequency = (array == O).sum()  # Finds the sum of the O frequency
        X_frequency = (array == X).sum()
        # Figures which player's turn it is
        return O if (X_frequency > O_frequency) else X
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()  # Creates a set whereby all actions can be stored
    for i, row in enumerate(board):  # Iterates through the board and returns possible actions
        for num, item in enumerate(row):
            if item is EMPTY:
                possible_actions.add((i, num))
    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    j, i = action
    if board[j][i] != EMPTY:
        raise Exception("invalid board move")
    mark = player(board)
    new_board = deepcopy(board)
    new_board[j][i] = mark
    return new_board


def check_diagonal_winner(board, mark):
    off_diag = [board[i][i] for i in range(3)]
    main_diag = [board[i][2 - i] for i in range(3)]
    return all(item == mark for item in off_diag) or all(item == mark for item in main_diag)


def check_column_winner(board, mark):
    firstcol = [board[i][0] for i in range(0,3)]
    secondcol = [board[i][1] for i in range(0,3)]
    thirdcol = [board[i][2] for i in range(0,3)]
    return all(item == mark for item in firstcol) or all(item == mark for item in secondcol) or all(item == mark for item in thirdcol)


def winner_check(board, mark):
    return any(all(item == mark for item in row) for row in board)


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    transposed_board = transpose(board)
    if winner_check(board, O) or winner_check(transposed_board, O) or check_diagonal_winner(board, O) or check_column_winner(board,O):
        return O
    if winner_check(board, X) or winner_check(transposed_board, X) or check_diagonal_winner(board, X) or check_column_winner(board,X):
        return X
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    return winner(board) or all(all(item != EMPTY for item in row) for row in board)


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    s = winner(board)
    if s == X:
        return 1
    elif s == O:
        return -1
    else:
        return 0


def max_value(board):
    if terminal(board):
        return utility(board), None
    sample = float("-inf")
    best = None
    for action in actions(board):
        min_v = min_value(result(board, action))[0]
        if min_v > sample:
            sample = min_v
            best = action
    return sample, best


def min_value(board):
    if terminal(board):
        return utility(board), None
    sample = float("inf")
    best = None
    for action in actions(board):
        max_v = max_value(result(board, action))[0]
        if max_v < sample:
            sample = max_v
            best = action
    return sample, best


def minimax_without_sample2_sample1_pruning(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    if player(board) == X:
        return max_value(board)[1]
    elif player(board) == O:
        return min_value(board)[1]
    else:
        raise Exception("We have encountered an error")


def maxvalues(board, sample2, sample1):
    if terminal(board):
        return utility(board), None
    sample = float("-inf")
    best = None
    for action in actions(board):
        min_v = minvalues(result(board, action), sample2, sample1)[0]
        if min_v > sample:
            sample = min_v
            best = action
        sample2 = max(sample2, sample)
        if sample1 <= sample2:
            break
    return sample, best


def minvalues(board, sample2, sample1):
    if terminal(board):
        return utility(board), None
    sample = float("inf")
    best = None
    for action in actions(board):
        max_v = maxvalues(result(board, action), sample2, sample1)[0]
        if max_v < sample:
            sample = max_v
            best = action
        sample1 = min(sample1, sample)
        if sample1 <= sample2:
            break
    return sample, best


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    if player(board) == X:
        return maxvalues(board, float("-inf"), float("inf"))[1]
    elif player(board) == O:
        return minvalues(board, float("-inf"), float("inf"))[1]
    else:
        raise Exception("We have encountered an error")