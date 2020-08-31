import random
import time
from termcolor import cprint


# lIST OF COLOURS

class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    ITALIC = '\033[3m'


class Nim():

    def __init__(self, initial=[1, 3, 5, 7]):
        """
        Initialize game board.
        Each game board has
            - `piles`: a list of how many elements remain in each pile
            - `player`: 0 or 1 to indicate which player's turn
            - `winner`: None, 0, or 1 to indicate who the winner is
        """
        self.piles = initial.copy()
        self.player = 0
        self.winner = None

    @classmethod
    def available_actions(cls, piles):
        """
        Nim.available_actions(piles) takes a `piles` list as input
        and returns all of the available actions `(i, j)` in that state.
        Action `(i, j)` represents the action of removing `j` items
        from pile `i` (where piles are 0-indexed).
        """
        actions = set()
        for i, pile in enumerate(piles):
            for j in range(1, piles[i] + 1):
                actions.add((i, j))
        return actions

    @classmethod
    def other_player(cls, player):
        """
        Nim.other_player(player) returns the player that is not
        `player`. Assumes `player` is either 0 or 1.
        """
        return 0 if player == 1 else 1

    def switch_player(self):
        """
        Switch the current player to the other player.
        """
        self.player = Nim.other_player(self.player)

    def move(self, action):
        """
        Make the move `action` for the current player.
        `action` must be a tuple `(i, j)`.
        """
        pile, count = action

        # Error Checking
        if self.winner is not None:
            raise Exception("Game already won")
        elif pile < 0 or pile >= len(self.piles):
            raise Exception("Invalid pile")
        elif count < 1 or count > self.piles[pile]:
            raise Exception("Invalid number of objects")

        # Pile Updates
        self.piles[pile] -= count
        self.switch_player()

        # Winner Check
        if all(pile == 0 for pile in self.piles):
            self.winner = self.player


class NimAI():

    def __init__(self, alpha=0.5, epsilon=0.1):
        """
        Initialize AI with an empty Q-learning dictionary,
        an alpha (learning) rate, and an epsilon rate.
        The Q-learning dictionary maps `(state, action)`
        pairs to a Q-value (a number).
         - `state` is a tuple of remaining piles, e.g. (1, 1, 4, 4)
         - `action` is a tuple `(i, j)` for an action
        """
        self.q = dict()
        self.alpha = alpha
        self.epsilon = epsilon

    def update(self, old_state, action, new_state, reward):
        """
        Update Q-learning model, given an old state, an action taken
        in that state, a new resulting state, and the reward received
        from taking that action.
        """
        old = self.get_q_value(old_state, action)
        best_future = self.best_future_reward(new_state)
        self.update_q_value(old_state, action, old, reward, best_future)

    def get_q_value(self, state, action):
        """
        Return the Q-value for the state `state` and the action `action`.
        If no Q-value exists yet in `self.q`, return 0.
        """
        return self.q[(tuple(state), action)] if \
            (tuple(state), action) in self.q \
            else 0

    def update_q_value(self, state, action, old_q, reward, future_rewards):
        """
        Update the Q-value for the state `state` and the action `action`
        given the previous Q-value `old_q`, a current reward `reward`,
        and an estimate of future rewards `future_rewards`.
        Use the formula:
        Q(s, a) <- old value estimate
                   + alpha * (new value estimate - old value estimate)
        where `old value estimate` is the previous Q-value,
        `alpha` is the learning rate, and `new value estimate`
        is the sum of the current reward and estimated future rewards.
        """
        self.q[(tuple(state), action)] = old_q + self.alpha * (reward + future_rewards - old_q)

    def best_future_reward(self, state):
        """
        Given a state `state`, consider all possible `(state, action)`
        pairs available in that state and return the maximum of all
        of their Q-values.
        Use 0 as the Q-value if a `(state, action)` pair has no
        Q-value in `self.q`. If there are no available actions in
        `state`, return 0.
        """
        best_reward = 0
        for action in Nim.available_actions(list(state)):
            best_reward = max(self.get_q_value(state, action), best_reward)

        return best_reward

    def choose_action(self, state, epsilon=True):
        """
        Given a state `state`, return an action `(i, j)` to take.
        If `epsilon` is `False`, then return the best action
        available in the state (the one with the highest Q-value,
        using 0 for pairs that have no Q-values).
        If `epsilon` is `True`, then with probability
        `self.epsilon` choose a random available action,
        otherwise choose the best action available.
        If multiple actions have the same Q-value, any of those
        options is an acceptable return value.
        """
        action_to_make = None
        best_reward = 0
        actions = list(Nim.available_actions(list(state)))

        for action in actions:
            if action_to_make is None or self.get_q_value(state, action) > best_reward:
                best_reward = self.get_q_value(state, action)
                action_to_make = action

        if epsilon:
            weigh = [(1 - self.epsilon) if action == action_to_make else
                     (self.epsilon / (len(actions) - 1)) for action in actions]

            action_to_make = random.choices(actions, weights=weigh, k=1)[0]

        return action_to_make


def train(n):
    """
    Train an AI by playing `n` games against itself.
    """

    player = NimAI()

    # Game is played n number of times
    for i in range(n):
        cprint(f"Playing training game {i + 1}", "cyan")
        print()
        game = Nim()

        # Track of last move is kept
        last = {
            0: {"state": None, "action": None},
            1: {"state": None, "action": None}
        }

        while True:

            # Current state and action tracker
            state = game.piles.copy()
            action = player.choose_action(game.piles)

            # Last state and action tracker
            last[game.player]["state"] = state
            last[game.player]["action"] = action

            # Move is then made
            game.move(action)
            new_state = game.piles.copy()

            # Game over and distribution of rewards
            if game.winner is not None:
                player.update(state, action, new_state, -1)
                player.update(
                    last[game.player]["state"],
                    last[game.player]["action"],
                    new_state,
                    1
                )
                break

            # No reward with game continuation
            elif last[game.player]["state"] is not None:
                player.update(
                    last[game.player]["state"],
                    last[game.player]["action"],
                    new_state,
                    0
                )

    cprint(color.BOLD + color.RED + "\nDone training" + color.END)

    # Trained AI is returned
    return player


def play(ai, human_player=None):
    """
    Play human game against the AI.
    `human_player` can be set to 0 or 1 to specify whether
    human player moves first or second.
    """

    if human_player is None:
        human_player = random.randint(0, 1)

    # New game is initiated
    game = Nim()

    while True:

        # Pile contents
        print()
        cprint(color.BOLD + color.UNDERLINE + "Piles:", "green")
        for i, pile in enumerate(game.piles):
            cprint(f"Pile {i}: {pile}", "blue")
        print()

        # Finds available actions
        available_actions = Nim.available_actions(game.piles)
        time.sleep(1)

        # Human move
        if game.player == human_player:
            print(color.BOLD + color.UNDERLINE + color.YELLOW + "Your Turn" + color.END)
            while True:
                pile = int(input("Choose Pile: "))
                count = int(input("Choose Count: "))
                if (pile, count) in available_actions:
                    break
                cprint("Invalid move, try again.", "red")

        # AI move
        else:
            print(color.BOLD + color.UNDERLINE + color.YELLOW + "AI's Turn" + color.END)
            pile, count = ai.choose_action(game.piles, epsilon=False)
            print(f"AI chose to take {count} from pile {pile}.")

        # Depending on player, move is made
        game.move((pile, count))

        # Winner checker
        if game.winner is not None:
            print()
            print(color.BOLD + color.YELLOW + "GAME OVER" + color.END)
            winner = "Human" if game.winner == human_player else "AI"
            cprint(color.BOLD + f"Winner is {winner}" + color.END)
            return
