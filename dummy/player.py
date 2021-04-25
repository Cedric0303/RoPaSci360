from random import choice, randrange
from dummy.board import Board
from dummy.side import Lower, Upper
from dummy.token import Rock, Paper, Scissors

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
        self.max_throw = 5 if self.side is Upper else -3
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
        self.kills = 0
        self.deaths = 0
        self.history = list()

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        tokens = list(map(type, self.self_tokens + self.opponent_tokens))
        ttypes_on_board = int(Paper in tokens) + int(Rock in tokens) + int(Scissors in tokens)
        if self.throws and (not self.self_tokens or ttypes_on_board == 1 ):#  or not self.turn % 10):
            # throw
            token = self.throws.pop(self.throws.index(choice(self.throws)))
            r = randrange(min(self.min_throw, self.max_throw), max(self.min_throw, self.max_throw))
            q = randrange(-4, 5)
            while not Board.check_bounds(r, q):
                r = randrange(min(self.min_throw, self.max_throw), max(self.min_throw, self.max_throw))
                q = randrange(-4, 5)
            return ("THROW", token.name.lower(), (r, q))
        else:
            # slide
            token = choice(self.self_tokens) if len(self.self_tokens) > 1 else self.self_tokens[0]
            action = choice([(r, q) for (r, q) in token.get_adj_hex(token.r, token.q) if Board.check_bounds(r, q)])
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
        if "THROW" == player_action[0]:
            # self throw
            token_name = player_action[1]
            (r, q) = player_action[2]
            if 'r' in token_name:
                self.self_tokens.append(Rock(self.side, r, q))
            elif 'p' in token_name:
                self.self_tokens.append(Paper(self.side, r, q))
            elif 's' in token_name:
                self.self_tokens.append(Scissors(self.side, r, q))
            if self.side is Upper:
                self.min_throw -= 1
            else:
                self.max_throw += 1

        elif "SLIDE" == player_action[0] or "SWING" == player_action[0]:
            # self swing/slide
            prev_r, prev_q = player_action[1]
            next_r, next_q = player_action[2]
            for i in range(len(self.self_tokens)):
                if (self.self_tokens[i].r == prev_r and self.self_tokens[i].q == prev_q):
                    # print("CHANGING SELF", (prev_r, prev_q), ( next_r, next_q))
                    self.self_tokens[i].move(next_r, next_q)
                    break

        if "THROW" == opponent_action[0]:
            # opponent throw
            token_name2 = opponent_action[1]
            (r2, q2) = opponent_action[2]
            if 'r' in token_name2:
                self.opponent_tokens.append(Rock(self.enemy_side, r2, q2))
            elif 'p' in token_name2:
                self.opponent_tokens.append(Paper(self.enemy_side, r2, q2))
            elif 's' in token_name2:
                self.opponent_tokens.append(Scissors(self.enemy_side, r2, q2))

        elif "SLIDE" == opponent_action[0] or "SWING" == opponent_action[0]:
            # opponent swing/slide
            prev_r, prev_q = opponent_action[1]
            next_r, next_q = opponent_action[2]
            for i in range(len(self.opponent_tokens)):
                if (self.opponent_tokens[i].r == prev_r and self.opponent_tokens[i].q == prev_q):
                    # print("CHANGING ENEMY", (prev_r, prev_q), (next_r, next_q))
                    self.opponent_tokens[i].move(next_r, next_q)
                    break

        new_self, new_oppo = self.board.battle(self.self_tokens, self.opponent_tokens)
        self.kills += (len(self.opponent_tokens) - len(new_oppo))
        self.deaths += (len(self.self_tokens) - len(new_self))
        self.self_tokens, self.opponent_tokens = new_self, new_oppo
        self.turn += 1