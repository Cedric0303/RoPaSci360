from CedSam.board import Board
from CedSam.side import Lower, Upper
from CedSam.token import Rock, Paper, Scissors

class Player:
    def __init__(self, side):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        self.board = Board()
        self.side = Upper if 'u' in side else Lower
        print(self.side)
        self.throws = {Rock: 3, Paper: 3, Scissors: 3}
        exit() # exit for now, not done implementation

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        # put your code here
    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        # put your code here