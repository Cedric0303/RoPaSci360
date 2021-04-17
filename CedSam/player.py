from random import choice, randrange
from math import dist
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

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        tokens = list(map(type, self.self_tokens + self.opponent_tokens))
        ttypes_on_board = int(Paper in tokens) + int(Rock in tokens) + int(Scissors in tokens)
        if self.throws and (not self.self_tokens or ttypes_on_board == 1 or not self.turn % 10):
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
        if 'T' in player_action[0]:
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
                self.max_throw  += 1

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
            if 'r' in token_name2:
                self.opponent_tokens.append(Rock(self.enemy_side, r2, q2))
            elif 'p' in token_name2:
                self.opponent_tokens.append(Paper(self.enemy_side, r2, q2))
            elif 's' in token_name2:
                self.opponent_tokens.append(Scissors(self.enemy_side, r2, q2))

        elif 'L' in opponent_action[0] or 'W' in opponent_action[0]:
            # opponent swing/slide
            prev_r, prev_q = opponent_action[1]
            next_r, next_q = opponent_action[2]
            for i in range(len(self.opponent_tokens)):
                if (self.opponent_tokens[i].r == prev_r \
                and self.opponent_tokens[i].q == prev_q):
                    self.opponent_tokens[i].move(next_r, next_q)
        self.self_tokens, self.opponent_tokens = \
            self.board.battle(self.self_tokens, self.opponent_tokens)
        self.turn += 1

    # Adjusts a list of tokens to provide updated list
    def adjust_list(self, token, token_list, new_r, new_q):

        token_list.remove(token)
        if token.name.upper() == 'R':
            token_list.append(Rock(token.side, new_r, new_q))
        elif token.name.upper() == 'P':
            token_list.append(Paper(token.side, new_r, new_q))
        elif token.name.upper() == 'S':
            token_list.append(Scissors(token.side, new_r, new_q))

        return token_list

    """
    Builds a 2-d utility matrix. Dict keys are the possible moves.
    token_considered: our token, which we're calculating utility for
    target_token: enemy token which we're trying to kill
    enemy_token: enemy token to avoid

    e.g. {(2,3):[1,2,4,5], (2,4):[2,4,8,6]}
    """
    def build_utility(self, token_considered, target_token, enemy_token, self_tokens, opponent_tokens):
        
        util_matrix = dict()
        possible = token_considered.get_adj_hex()

        # enumerate all possible moves for our token
        for move_r, move_q in possible:
            
            shallow_self = self_tokens.copy()
            if Board.check_bounds(move_r, move_q):
                self.adjust_list(token_considered, shallow_self, move_r, move_q)

                target_moves = target_token.get_adj_hex()
                enemy_moves = enemy_token.get_adj_hex()

                for opp_r, opp_q in target_moves:
                    shallow_opp = opponent_tokens.copy()
                    if Board.check_bounds(opp_r, opp_q):
                        self.adjust_list(target_token, shallow_opp, opp_r, opp_q)

                        # now we have the modified lists of tokens, i.e. a gamestate where two moves have been taken
                        alive_self, alive_opp = Board.battle(shallow_self, shallow_opp)

                        if (move_r, move_q) not in util_matrix:
                            util_matrix[(move_r, move_q)] = [self.simple_eval(token_considered, move_r, move_q, alive_self, alive_opp)]
                        else:
                            util_matrix[(move_r, move_q)].append(self.simple_eval(alive_self, alive_opp))

                for opp_r, opp_q in enemy_moves:
                    shallow_opp = opponent_tokens.copy()
                    if Board.check_bounds(opp_r, opp_q):
                        self.adjust_list(enemy_token, shallow_opp, opp_r, opp_q)

                        # any way to modularise?
                        alive_self, alive_opp = Board.battle(shallow_self, shallow_opp)

                        if (move_r, move_q) not in util_matrix:
                            util_matrix[(move_r, move_q)] = [self.simple_eval(alive_self, alive_opp)]
                        else:
                            util_matrix[(move_r, move_q)].append(self.simple_eval(alive_self, alive_opp))

        return util_matrix


    # Returns simple evaluation of player tokens minus opponent tokens
    def simple_eval(self, token_considered, r, q, self_tokens, opponent_tokens):
    
        difference = len(self_tokens) - len(opponent_tokens)
        difference += self.target_eval(token_considered, opponent_tokens)    
        difference += self.ally_eval(token_considered, r, q, self_tokens)
        difference += self.avoid_eval(token_considered, opponent_tokens)

        return difference

    def target_eval(self, token_considered, opponent_tokens):
        w = 0.5
        targets = [token for token in opponent_tokens 
                   if isinstance(token, token_considered.enemy)]
        distance = min([dist([token_considered.r, token_considered.q], [target.r, target.q]) for target in targets])

        return w * distance

    def ally_eval(self, token_considered, r, q, self_tokens):
        w = -10.0
        team_kill = [(token.r, token.q) for token in self_tokens if isinstance(token, token_considered.enemy) or isinstance(token, token_considered.avoid)]
        return w if (r, q) in team_kill else 0

    
    def avoid_eval(self, token_considered, opponent_tokens):
        w = 0.3
        enemies = [token for token in opponent_tokens if isinstance(token, token_considered.avoid)]
        distance = min([dist([token_considered.r, token_considered.q], [target.r, target.q]) for target in enemies])

        return w * distance

    def swing_eval(self, token_considered, r, q, self_tokens):
        w = 2.0
        adj = set(token_considered.get_adj_hex(r, q))
        allies = set([(token.r, token.q) for token in self_tokens])
        return w if bool(adj.intersection(allies)) else 0
        
    # """Carries out simultaneous move alpha beta pruning, once for each token

    # state: A game state, i.e. a board configuration (self_tokens + opponent_tokens)
    # alpha: lower bound
    # beta: upper bound
    # depth: terminal limit
    # token_considered: A single token of our player's side, whose moves are being evaluated
    # seen: A dictionary of board configs to maintain what has been seen, and at what depth level
    # """
    # def smab(self, self_tokens, opponent_tokens, alpha, beta, depth, token_considered, seen):

    #     # terminal state if it has reached depth limit, then just evaluate
    #     if seen[state] == 1:
    #         v = self.simple_eval(self_tokens, opponent_tokens)
    #         return v
        


