from random import choice, randrange
from math import dist
from dummy_2.board import Board
from dummy_2.side import Lower, Upper
from dummy_2.token import Rock, Paper, Scissors
from pympler import muppy, summary
from dummy_2.gametheory2 import solve_game
import itertools

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
        # self.all_objects = muppy.get_objects()

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
            # summary.print_(summary.summarize(self.all_objects))
            return ("THROW", token.name.lower(), (r, q))
        else:
            # slide
            token_utils = dict()
            for token in self.self_tokens:
                targets = [target for target in self.opponent_tokens if isinstance(target, token.enemy)]
                enemies = [enemy for enemy in self.opponent_tokens if isinstance(enemy, token.avoid)]
                both  = list(itertools.zip_longest(targets, enemies))
                while both:
                    t, e = both.pop(0)
                    if token not in token_utils:
                        token_utils[token] = [self.build_utility(token, t, e, self.self_tokens, self.opponent_tokens)]
                    else:
                        token_utils[token].append(self.build_utility(token, t, e, self.self_tokens, self.opponent_tokens))            
            for token, each_util in token_utils.items():
                util_move = [move for move in each_util[0].keys()]
                util_matrix = [util for util in each_util[0].values()]
                s, v = solve_game(util_matrix)
                # print(token, s, v)
                s = s.tolist()
                if s.count(s[0]) == len(s):
                    action = choice(util_move)
                else:
                    action = util_move[s.index(max(s))]
                token_utils[token] = [action, v]
            # print(token_utils)
            token = max(token_utils, key=lambda key: token_utils[key][1])
            action = token_utils[token][0]
            # summary.print_(summary.summarize(self.all_objects))
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
    cur_token: our token, which we're calculating utility for
    target_token: enemy token which we're trying to kill
    enemy_token: enemy token to avoid

    e.g. {(2,3):[1,2,4,5], (2,4):[2,4,8,6]}
    """
    def build_utility(self, cur_token, target_token, enemy_token, self_tokens, opponent_tokens):
        
        util_matrix = dict()
        possible = cur_token.get_adj_hex(cur_token.r, cur_token.q)
        
        # enumerate all possible moves for our token
        for move_r, move_q in possible:
            shallow_self = self_tokens.copy()
            if Board.check_bounds(move_r, move_q):
                shallow_self = self.adjust_list(cur_token, shallow_self, move_r, move_q)

                # print("-----------")
                # print(move_r, move_q)
                if target_token:
                    target_moves = target_token.get_adj_hex(target_token.r, target_token.q)
                    for opp_r, opp_q in target_moves:
                        shallow_opp = opponent_tokens.copy()
                        if Board.check_bounds(opp_r, opp_q):
                            shallow_opp = self.adjust_list(target_token, shallow_opp, opp_r, opp_q)

                            # now we have the modified lists of tokens, i.e. a gamestate where two moves have been taken
                            alive_self, alive_opp = self.board.battle(shallow_self, shallow_opp)

                            if (move_r, move_q) not in util_matrix:
                                util_matrix[(move_r, move_q)] = [self.simple_eval(cur_token, move_r, move_q, alive_self, alive_opp)]
                            else:
                                util_matrix[(move_r, move_q)].append(self.simple_eval(cur_token, move_r, move_q, alive_self, alive_opp))
                if enemy_token:
                    enemy_moves = enemy_token.get_adj_hex(enemy_token.r, enemy_token.q)
                    for opp_r, opp_q in enemy_moves:
                        shallow_opp = opponent_tokens.copy()
                        if Board.check_bounds(opp_r, opp_q):
                            shallow_opp = self.adjust_list(enemy_token, shallow_opp, opp_r, opp_q)

                            # any way to modularise?
                            alive_self, alive_opp = self.board.battle(shallow_self, shallow_opp)

                            if (move_r, move_q) not in util_matrix:
                                util_matrix[(move_r, move_q)] = [self.simple_eval(cur_token, move_r, move_q, alive_self, alive_opp)]
                            else:
                                util_matrix[(move_r, move_q)].append(self.simple_eval(cur_token, move_r, move_q, alive_self, alive_opp))
        return util_matrix

    # Returns simple evaluation of player tokens minus opponent tokens
    def simple_eval(self, cur_token, r, q, self_tokens, opponent_tokens):
        # print("target", self.target_eval(cur_token, r, q, opponent_tokens))
        # print("ally", self.ally_eval(cur_token, r, q, self_tokens))
        # print("avoid", self.avoid_eval(cur_token, r, q, opponent_tokens))
        difference = 0
        difference += self.target_eval(cur_token, r, q, opponent_tokens)
        difference += self.ally_eval(cur_token, r, q, self_tokens)
        difference += self.avoid_eval(cur_token, r, q, opponent_tokens)
        # print("diff", difference)
        return difference

    def target_eval(self, cur_token, r, q, opponent_tokens):
        w = 10
        targets = [token for token in opponent_tokens if isinstance(token, cur_token.enemy)]
        distance = [cur_token.manhattan_distance([r, q], [target.r, target.q]) for target in targets]
        # distance = [dist([r, q], [target.r, target.q]) for target in targets]
        return round((w / (min(distance) + 1)) * (min(distance) + 2)) if distance else 0
    
    def ally_eval(self, cur_token, r, q, self_tokens):
        w = -5
        team_kill = [(token.r, token.q) for token in self_tokens if isinstance(token, cur_token.enemy) or isinstance(token, cur_token.avoid)]
        return w if (r, q) in team_kill else 0

    def avoid_eval(self, cur_token, r, q, opponent_tokens):
        w = 1
        enemies = [token for token in opponent_tokens if isinstance(token, cur_token.avoid)]
        distance = [cur_token.manhattan_distance([r, q], [enemy.r, enemy.q]) for enemy in enemies]
        # distance = [dist([r, q], [enemy.r, enemy.q]) for enemy in enemies]
        return round(w * (min(distance) + 1)) if distance else 0

    def swing_eval(self, cur_token, r, q, self_tokens):
        w = 2
        adj = set(cur_token.get_adj_hex(r, q))
        allies = set([(token.r, token.q) for token in self_tokens])
        return w if adj.intersection(allies) else 0