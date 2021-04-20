from random import choice, randrange
from math import dist, sqrt
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
        beatable = [type(opponent) for token in self.self_tokens for opponent in self.opponent_tokens if isinstance(opponent, token.enemy)]
        
        if self.self_tokens and beatable:
            token_best_move = dict()

            # save current opponent coords
            if self.opponent_tokens:
                cache_oppo = [(each.r, each.q) for each in self.opponent_tokens]
            if self.self_tokens:
                cache_self = [(each.r, each.q) for each in self.self_tokens]
                
            for token in self.self_tokens:
                ori_r, ori_q = token.r, token.q
                moves = [(r, q) for (r, q) in token.get_adj_hex(ori_r, ori_q) if Board.check_bounds(r, q)]
                print("CHECKING", token.name)
                # get both targets and enemies of a given token
                both = [target for target in self.opponent_tokens if isinstance(target, token.enemy)] + [enemy for enemy in self.opponent_tokens if isinstance(enemy, token.avoid)]
                # print(both)
                best_moves = dict()
                if both:
                    while both:
                        # generate all util values for each target/enemy for a token
                        opponent = both.pop(0)
                        for r, q in moves:
                            self_tokens = self.self_tokens.copy()
                            self_oppo = self.opponent_tokens.copy()
                            self_tokens = self.adjust_list(token, self_tokens, r, q)
                            val = self.lookahead(token, opponent, self_tokens, self_oppo, depth=0)
                            if (r,q) not in best_moves:
                                best_moves[(r, q)] = [val]
                            else:
                                best_moves[(r, q)].append(val)
                    # select max util value for a token
                    for coord, best_val in best_moves.items():
                        best_moves[coord] = max(best_val)
                        print(coord, best_moves[coord])
                    token.r, token.q = ori_r, ori_q
                    token_best_move[token] =[max(best_moves, key=lambda key: best_moves[key]), max(best_moves.values())]
                # replace opponent coord to original ones
            if self.opponent_tokens:
                for i in range(len(cache_oppo)):
                    c_r, c_q = cache_oppo[i]
                    self.opponent_tokens[i].move(c_r, c_q)
            if self.self_tokens:
                for i in range(len(cache_self)):
                    c_r, c_q = cache_self[i]
                    self.self_tokens[i].move(c_r, c_q)

            # choose the best token to move based on max util value of each token
            if token_best_move:
                print(token_best_move)
                best_token = max(token_best_move, key=lambda key: token_best_move[key][1])
                (best_r, best_q) = token_best_move[best_token][0]
                if dist([best_token.r, best_token.q], [best_r, best_q]) > sqrt(2):
                    return ("SWING", (best_token.r, best_token.q), (best_r, best_q))
                else:
                    return ("SLIDE", (best_token.r, best_token.q), (best_r, best_q))
        
        tokens = list(map(type, self.self_tokens + self.opponent_tokens))
        ttypes_on_board = int(Paper in tokens) + int(Rock in tokens) + int(Scissors in tokens)

        if self.throws and (not self.self_tokens or ttypes_on_board == 1 or not beatable):#  or not self.turn % 10):
            # throw
            if self.opponent_tokens:
                random_enemy = choice(self.opponent_tokens)
                token = choice([each for each in self.throws if isinstance(each, random_enemy.avoid)])
                self.throws.remove(token)
            else:
                token = self.throws.pop(self.throws.index(choice(self.throws)))
            r = randrange(min(self.min_throw, self.max_throw), max(self.min_throw, self.max_throw))
            q = randrange(-4, 5)
            while not Board.check_bounds(r, q):
                r = randrange(min(self.min_throw, self.max_throw), max(self.min_throw, self.max_throw))
                q = randrange(-4, 5)
            return ("THROW", token.name.lower(), (r, q))
    
    
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
                self.max_throw  += 1

        elif "SLIDE" == player_action[0] or "SWING" == player_action[0]:
            # self swing/slide
            prev_r, prev_q = player_action[1]
            next_r, next_q = player_action[2]
            for i in range(len(self.self_tokens)):
                if (self.self_tokens[i].r == prev_r \
                and self.self_tokens[i].q == prev_q):
                    self.self_tokens[i].move(next_r, next_q)

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

                        row_utility.append(self.simple_eval(token_considered, alive_self, alive_opp, target_enemy))
                
                # don't add in an empty list if the opp move was invalid
                if len(row_utility) != 0:
                    util_matrix.append(row_utility)                     

        return util_matrix, my_valid_moves, opp_valid_moves


    # Returns simple evaluation of player tokens minus opponent tokens
    def simple_eval(self, cur_token, self_tokens, opponent_tokens, target_enemy):
        difference = 1
        
        if target_enemy == 1:
            difference += self.target_eval(cur_token, opponent_tokens)
        else:
            difference += self.enemy_eval(cur_token, opponent_tokens)
        difference += self.ally_eval(cur_token, self_tokens)
        # difference += self.border_eval(cur_token)
        return difference

    def target_eval(self, cur_token, opponent_tokens):
        w = 1
        targets = [token for token in opponent_tokens if isinstance(token, cur_token.enemy)]
        distance = [cur_token.euclidean_distance([cur_token.r, cur_token.q], [target.r, target.q]) for target in targets]
        if distance:
                return w * (50/min(distance) * (min(distance) + 1))
        return 0

    def enemy_eval(self, cur_token, opponent_tokens):
        w = 1
        targets = [token for token in opponent_tokens if isinstance(token, cur_token.avoid)]
        distance = [cur_token.euclidean_distance([cur_token.r, cur_token.q], [target.r, target.q]) for target in targets]
        if distance:
            if min(distance) == 0:
                return 500
            else:
                return -w * (50/min(distance) * (min(distance) + 1))
        return 0

    def border_eval(self, cur_token):
        w = -100
        # lower value if at board border
        border = [(r, q) for (r, q) in cur_token.get_adj_hex(cur_token.r, cur_token.q) if self.board.check_bounds(r, q)] != 6
        return w if border else 0
    
    def ally_eval(self, cur_token, self_tokens):
        w = -1
        team_kill = [(token.r, token.q) for token in self_tokens if isinstance(token, cur_token.enemy) or isinstance(token, cur_token.avoid) or 
                                                                    isinstance(cur_token, token.avoid) or isinstance(cur_token, token.enemy)]
        return w if (cur_token.r, cur_token.q) in team_kill else 0

    # def swing_eval(self, cur_token, r, q, self_tokens):
    #     w = 2
    #     adj = set(cur_token.get_adj_hex(r, q))
    #     allies = set([(token.r, token.q) for token in self_tokens])
    #     return w if adj.intersection(allies) else 0
    
    """
    Carries out the search in a tree of utility matrices to find the best action for our token.
    Returns the SUM utility of best moves seen
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
            return val

        util_matrix, my_moves, opp_moves = self.build_utility(token_considered, target, self_tokens, opponent_tokens)
        sol_best, val_best = solve_game(np.array(util_matrix), maximiser=True, rowplayer=True)
        
        # fix what our best move is
        sol_best = sol_best.tolist()
        (best_r, best_q) = my_moves[sol_best.index(max(sol_best))]
        new_self = self.adjust_list(token_considered, self_tokens, best_r, best_q)

        max_value = 0

        # explore the possible moves opp can take
        for move in opp_moves:
            opp_r, opp_q = move
            # adjust opp's list, and recurse
            new_opp = self.adjust_list(target, opponent_tokens, opp_r, opp_q)
            temp = self.lookahead(token_considered, target, new_self, new_opp, depth + 1)

            if temp > max_value:
                max_value = temp
        
        return val_best + max_value
        
        
        
    


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
        


