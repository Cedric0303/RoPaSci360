from random import choice, randrange
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
        self.side = Upper if 'u' in side else Lower
        self.enemy_side = Upper if 'u' not in side else Lower
        self.min_throw = 4 if self.side is Upper else -4
        self.max_throw = self.min_throw
        self.turn = 0
        self.board = Board(self.side)
        self.throws = [Rock(self.side, -1, -1), 
                        Rock(self.side, -1, -1), 
                        Rock(self.side, -1, -1),
                        Paper(self.side, -1, -1), 
                        Paper(self.side, -1, -1), 
                        Paper(self.side, -1, -1),
                        Scissors(self.side, -1, -1), 
                        Scissors(self.side, -1, -1), 
                        Scissors(self.side, -1, -1)]
        self.self_tokens = list()
        self.opponent_tokens = list()

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        if self.throws and (not self.turn or not self.self_tokens):
            # throw
            token = self.throws.pop(self.throws.index(choice(self.throws)))
            r = randrange(self.min_throw, self.max_throw + 1)
            q = randrange(-4, 5)
            while not Board.check_bounds(r, q):
                r = randrange(self.min_throw, self.max_throw + 1)
                q = randrange(-4, 5)
            return ("THROW", token.name.lower(), (r, q))
        else:
            # slide
            token = choice(self.self_tokens)
            action = choice([(r, q) for (r, q) in token.get_adj_her(token.r, token.q) if Board.check_bounds(r, q)])
            return ("SLIDE", (token.r, token.q), action)
        # swing : WIP

    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        self.turn += 1
        if 'T' in player_action[0]:
            # self throw
            token_name = player_action[1]
            (r, q) = player_action[2]
            if token_name == 'r':
                self.self_tokens.append(Rock(self.side, r, q))
            elif token_name == 'p':
                self.self_tokens.append(Paper(self.side, r, q))
            elif token_name == 's':
                self.self_tokens.append(Scissors(self.side, r, q))

        elif 'L' in player_action[0] or 'W' in player_action[0]:
            # self swing/slide
            prev_r, prev_q = player_action[1]
            next_r, next_q = player_action[2]
            for i in range(len(self.self_tokens)):
                if (self.self_tokens[i].r == prev_r \
                and self.self_tokens[i].q == prev_q):
                    self.self_tokens[i].move(next_r, next_q)

        if 'T' in opponent_action[0]:
            # opponent throw
            token_name2 = opponent_action[1]
            (r2, q2) = opponent_action[2]
            if token_name2 == 'r':
                self.opponent_tokens.append(Rock(self.enemy_side, r2, q2))
            elif token_name2 == 'p':
                self.opponent_tokens.append(Paper(self.enemy_side, r2, q2))
            elif token_name2 == 's':
                self.opponent_tokens.append(Scissors(self.enemy_side, r2, q2))

        elif 'L' in opponent_action[0] or 'W' in opponent_action[0]:
            # opponent swing/slide
            prev_r, prev_q = opponent_action[1]
            next_r, next_q = opponent_action[2]
            for i in range(len(self.opponent_tokens)):
                if (self.opponent_tokens[i].r == prev_r \
                and self.opponent_tokens[i].q == prev_q):
                    self.opponent_tokens[i].move(next_r, next_q)