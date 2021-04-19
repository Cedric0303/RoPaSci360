from random import choice, randrange
from math import dist, log1p
import numpy as np
from CedSam.board import Board
from CedSam.side import Lower, Upper
from CedSam.token import Rock, Paper, Scissors
from CedSam.gametheory2 import solve_game
# from copy import copy, deepcopy

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
            token_best_move = dict()
            for token in self.self_tokens:
                ori_r, ori_q = token.r, token.q
                moves = [(r, q) for (r, q) in token.get_adj_hex(ori_r, ori_q) if Board.check_bounds(r, q)]
                # moves = [(r, q) for (r, q) in token.get_adj_hex(token.r, token.q) if Board.check_bounds(r, q)]

                # get both targets and enemies of a given token
                both = [target for target in self.opponent_tokens if isinstance(target, token.enemy)] + [enemy for enemy in self.opponent_tokens if isinstance(enemy, token.avoid)]
                best_moves = dict()
                if both:
                    while both:
                        # generate all util values for each target/enemy for a token
                        opponent = both.pop(0)
                        for r, q in moves:
                            self_tokens = self.self_tokens.copy()
                            self_oppo = self.opponent_tokens.copy()
                            self_tokens = self.adjust_list(token, self_tokens, r, q)
                            best, util_matrix, moves_util, opp_moves, best_idx, val, sol = self.lookahead(token, opponent, self_tokens, self_oppo, depth=0)
                            if (r,q) not in best_moves:
                                best_moves[(r, q)] = [best]
                            else:
                                best_moves[(r, q)].append(best)
                            print(util_matrix)
                            print(best)
                    # select max util value for a token
                    for coord, best_val in best_moves.items():
                        best_moves[coord] = max(best_val)
                    token.r, token.q = ori_r, ori_q
                    token_best_move[token] = max(best_moves, key=lambda key: best_moves[key])
                
            # choose the best token to move based on max util value of each token
            best_token = max(token_best_move, key=lambda key: token_best_move[key][1])
            (best_r, best_q) = token_best_move[best_token]

            return ("SLIDE", (best_token.r, best_token.q), ( best_r, best_q))
    
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

        token_list[token_list.index(token)].move(new_r, new_q)
        # if token.name.upper() == 'R':
        #     token_list.append(Rock(token.side, new_r, new_q))
        # elif token.name.upper() == 'P':
        #     token_list.append(Paper(token.side, new_r, new_q))
        # elif token.name.upper() == 'S':
        #     token_list.append(Scissors(token.side, new_r, new_q))

        return token_list

    """
    Builds a 2-d utility matrix in a list of lists.
    Also returns a list of the valid moves we and the opponent can make.
    token_considered: our token, which we're calculating utility for
    enemy_token: opponent's token, can be either target to kill, or enemy to avoid

    e.g. [[1,2,4,5], [2,4,8,6]]
    """
    def build_utility(self, token_considered, enemy_token, self_tokens, opponent_tokens):
        
        util_matrix = list()
        possible = token_considered.get_adj_hex(token_considered.r, token_considered.q)
        enemy_moves = enemy_token.get_adj_hex(enemy_token.r, enemy_token.q)
        target_enemy = 1 if isinstance(enemy_token, token_considered.enemy) else -1

        opp_valid_moves = list()
        my_valid_moves = list()

        # enumerate all possible moves for our token
        for move_r, move_q in possible:
            
            shallow_self = self_tokens.copy()
            if Board.check_bounds(move_r, move_q):
                shallow_self = self.adjust_list(token_considered, shallow_self, move_r, move_q)
                my_valid_moves.append((move_r, move_q))
                row_utility = list()

                for opp_r, opp_q in enemy_moves:
                    shallow_opp = opponent_tokens.copy()
                    if Board.check_bounds(opp_r, opp_q):
                        shallow_opp = self.adjust_list(enemy_token, shallow_opp, opp_r, opp_q)
                        opp_valid_moves.append((opp_r, opp_q))

                        # now we have the modified lists of tokens, i.e. a gamestate where two moves have been taken
                        alive_self, alive_opp = self.board.battle(shallow_self, shallow_opp)

                        row_utility.append(self.simple_eval(token_considered, move_r, move_q, alive_self, alive_opp, target_enemy))
                
                # don't add in an empty list if the opp move was invalid
                if len(row_utility) != 0:
                    util_matrix.append(row_utility)                     

        return util_matrix, my_valid_moves, opp_valid_moves


    # Returns simple evaluation of player tokens minus opponent tokens
    def simple_eval(self, cur_token, r, q, self_tokens, opponent_tokens, target_enemy):
        difference = 10
        difference += self.target_enemy_eval(cur_token, r, q, opponent_tokens, target_enemy)
        difference += self.ally_eval(cur_token, r, q, self_tokens)
        return difference

    def target_enemy_eval(self, cur_token, r, q, opponent_tokens, target_enemy):
        w = 30 * target_enemy
        targets = [token for token in opponent_tokens if isinstance(token, cur_token.enemy)]
        # distance = [cur_token.manhattan_distance([r, q], [target.r, target.q]) for target in targets]
        distance = [dist([r, q], [target.r, target.q]) for target in targets]
        return round((w / (min(distance) + 1)) * (min(distance) + 2)) if distance else 0
    
    def ally_eval(self, cur_token, r, q, self_tokens):
        w = -100
        team_kill = [(token.r, token.q) for token in self_tokens if isinstance(token, cur_token.enemy) or isinstance(token, cur_token.avoid) or 
                                                                    isinstance(cur_token, token.avoid) or isinstance(cur_token, token.enemy)]
        return w if (r, q) in team_kill else 0

    # def swing_eval(self, cur_token, r, q, self_tokens):
    #     w = 2
    #     adj = set(cur_token.get_adj_hex(r, q))
    #     allies = set([(token.r, token.q) for token in self_tokens])
    #     return w if adj.intersection(allies) else 0
    
    """
    Carries out the search in a tree of utility matrices to find the best action for our token
    token_considered: a token of ours that we're thinking to move
    depth: terminal limit, i.e. number of moves we're looking ahead

    # wip: pruning, and maybe recognizing repeated states
    """
    def lookahead(self, token_considered, target, self_tokens, opponent_tokens, depth):

        # we stop recursing if we hit a limit, and returns the value of playing to this gamestate
        if depth == 2:
            util_matrix, my_moves, opp_moves = self.build_utility(token_considered, target, self_tokens, opponent_tokens)
            sol, val = solve_game(np.array(util_matrix), maximiser=True, rowplayer=True)
            sol = sol.tolist()
            return max(sol) * val, util_matrix, my_moves, opp_moves, sol.index(max(sol)), val, sol

        util_matrix, my_moves, opp_moves = self.build_utility(token_considered, target, self_tokens, opponent_tokens)
        sol_best, val_best = solve_game(np.array(util_matrix), maximiser=True, rowplayer=True)
        sol_opp, val_opp = solve_game(np.array(util_matrix), maximiser=False, rowplayer=False)

        sol_best = sol_best.tolist()
        sol_opp = sol_opp.tolist()
        (best_r, best_q) = my_moves[sol_best.index(max(sol_best))]
        (opp_r, opp_q) = opp_moves[sol_opp.index(max(sol_opp))]

        # now adjust the list, and recurse
        new_self = self.adjust_list(token_considered, self_tokens, best_r, best_q)
        new_opp = self.adjust_list(target, opponent_tokens, opp_r, opp_q)
        return self.lookahead(token_considered, target, new_self, new_opp, depth + 1)








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
        


