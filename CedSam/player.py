from random import choice, randrange
import numpy as np
from CedSam.board import Board
from CedSam.side import Lower, Upper
from CedSam.token import Rock, Paper, Scissors
from CedSam.gametheory2 import solve_game

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
        self.max_throw = 4 if self.side is Upper else -4
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
        if len(self.history) > 5: 
            del self.history[0]

        beatable = [type(opponent) for token in self.self_tokens 
                    for opponent in self.opponent_tokens 
                    if isinstance(opponent, token.enemy)]
        
        # move tokens
        if self.self_tokens: 
            if beatable and self.turn % 15:
                token_best_move = dict()

                # save current opponent coords
                if self.opponent_tokens:
                    cache_oppo = [(each.r, each.q) 
                                    for each in self.opponent_tokens]
                if self.self_tokens:
                    cache_self = [(each.r, each.q) 
                                    for each in self.self_tokens]
                
                if len(self.self_tokens) > 1:
                    for token in self.self_tokens:
                        best_val = -100
                        both = [target for target in self.opponent_tokens 
                                if isinstance(target, token.enemy)] + \
                                [enemy for enemy in self.opponent_tokens 
                                if isinstance(enemy, token.avoid)]
                        if both:
                            while both:
                                opponent = both.pop(0)
                                val = self.target_eval(token, opponent)
                                if val > best_val:
                                    best_val = val
                        else:
                            continue
                        token_best_move[token] = best_val
                    move = max(token_best_move, 
                                key=lambda key: token_best_move[key])
                else:
                    move = self.self_tokens[0]
                    
                ori_r, ori_q = move.r, move.q
                (best_r, best_q) = False, False
                best_val = -100
                both = [target for target in self.opponent_tokens 
                        if isinstance(target, move.enemy)] + \
                        [enemy for enemy in self.opponent_tokens 
                        if isinstance(enemy, move.avoid)]
                while both:
                    opponent = both.pop(0)
                    self_tokens = self.self_tokens.copy()
                    self_oppo = self.opponent_tokens.copy()
                    val, new_move = self.lookahead(move, opponent, self_tokens, 
                                                    self_oppo, depth = 0)
                    if val > best_val:
                        best_val = val
                        (best_r, best_q) = new_move
                    move.r, move.q = ori_r, ori_q
                if best_val == -100:
                    (best_r, best_r) = choice([(r, q) for (r, q) in 
                                            move.get_adj_hex(move.r, move.q) 
                                            if Board.check_bounds(r, q)])

                if self.opponent_tokens:
                    for i in range(len(cache_oppo)):
                        c_r, c_q = cache_oppo[i]
                        self.opponent_tokens[i].move(c_r, c_q)
                if self.self_tokens:
                    for i in range(len(cache_self)):
                        c_r, c_q = cache_self[i]
                        self.self_tokens[i].move(c_r, c_q)

                self.history.append((move, best_r, best_q))
                if move.hex_distance([move.r, move.q], [best_r, best_q]) > 1:
                    return ("SWING", (move.r, move.q), (best_r, best_q))
                else:
                    return ("SLIDE", (move.r, move.q), (best_r, best_q))

            elif not beatable:
                if len(self.self_tokens) > 1:
                    token = choice(self.self_tokens)
                else :
                    token = self.self_tokens[0]
                (best_r, best_q) = choice([(r, q) for (r, q) in 
                                            token.get_adj_hex(token.r, token.q) 
                                            if Board.check_bounds(r, q)])
                if token.hex_distance([token.r, token.q], [best_r, best_q]) > 1:
                    return ("SWING", (token.r, token.q), (best_r, best_q))
                else:
                    return ("SLIDE", (token.r, token.q), (best_r, best_q))
        
        tokens = list(map(type, self.self_tokens + self.opponent_tokens))
        ttypes_on_board = int(Paper in tokens) + \
                        int(Rock in tokens) + \
                        int(Scissors in tokens)

        # do throws
        if self.throws and \
        (not self.self_tokens or \
        ttypes_on_board == 1 or \
        not beatable or not self.turn % 15):
            
            current_hex = [(token.r, token.q) for token in self.self_tokens]
            # throw
            if self.opponent_tokens:
                for opponent in self.opponent_tokens:
                    token = [throw for throw in self.throws 
                            if isinstance(throw, opponent.avoid)]
                    if token and self.min_throw <= opponent.r <= self.max_throw:
                        chosen = token.pop(0)
                        self.throws.remove(chosen)
                        return ("THROW", chosen.name.lower(), 
                                (opponent.r, opponent.q))
                else:
                    token = \
                        self.throws.pop(self.throws.index(choice(self.throws)))
            else:
                token = self.throws.pop(self.throws.index(choice(self.throws)))
            r = randrange(min(self.min_throw, self.max_throw), 
                                max(self.min_throw, self.max_throw)+1)
            q = randrange(-4, 5)
            while not Board.check_bounds(r, q) and (r, q) not in current_hex:
                r = randrange(min(self.min_throw, self.max_throw), 
                                max(self.min_throw, self.max_throw)+1)
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
        # self throw
        if "THROW" == player_action[0]:
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

        # self swing/slide
        elif "SLIDE" == player_action[0] or "SWING" == player_action[0]:
            prev_r, prev_q = player_action[1]
            next_r, next_q = player_action[2]
            for i in range(len(self.self_tokens)):
                if (self.self_tokens[i].r == prev_r 
                and self.self_tokens[i].q == prev_q):
                    self.self_tokens[i].move(next_r, next_q)
                    break

        # opponent throw
        if "THROW" == opponent_action[0]:
            token_name2 = opponent_action[1]
            (r2, q2) = opponent_action[2]
            if 'r' in token_name2:
                self.opponent_tokens.append(Rock(self.enemy_side, r2, q2))
            elif 'p' in token_name2:
                self.opponent_tokens.append(Paper(self.enemy_side, r2, q2))
            elif 's' in token_name2:
                self.opponent_tokens.append(Scissors(self.enemy_side, r2, q2))

        # opponent swing/slide
        elif "SLIDE" == opponent_action[0] or "SWING" == opponent_action[0]:
            prev_r, prev_q = opponent_action[1]
            next_r, next_q = opponent_action[2]
            for i in range(len(self.opponent_tokens)):
                if (self.opponent_tokens[i].r == prev_r 
                and self.opponent_tokens[i].q == prev_q):
                    self.opponent_tokens[i].move(next_r, next_q)
                    break

        new_self, new_oppo = \
            self.board.battle(self.self_tokens, self.opponent_tokens)
        self.kills += (len(self.opponent_tokens) - len(new_oppo))
        self.deaths += (len(self.self_tokens) - len(new_self))
        self.self_tokens, self.opponent_tokens = new_self, new_oppo
        self.turn += 1

    def adjust_list(self, token, token_list, new_r, new_q):
        """
        Adjusts a list of tokens to provide updated list
        """
        token_list[token_list.index(token)].move(new_r, new_q)
        return token_list

    def build_utility(self, consider, enemy_token, 
                        self_tokens, opponent_tokens):
        """
        Builds a 2-d utility matrix in a list of lists.
        Also returns a list of the valid moves we and the opponent can make.
        consider: our token, which we're calculating utility for
        enemy_token: opponent's token, can be either target to kill, 
        or enemy to avoid

        e.g. [[1,2,4,5], [2,4,8,6]]
        """

        util_matrix = list()
        
        possible = [(r, q) for (r, q) in 
                    consider.get_adj_hex(consider.r, consider.q) 
                    if Board.check_bounds(r, q)]
        enemy_moves = [(r, q) for (r, q) in 
                        enemy_token.get_adj_hex(enemy_token.r, enemy_token.q) 
                        if Board.check_bounds(r, q)]

        # cache original token coords
        (ori_r, ori_q) = (consider.r, consider.q)

        for (move_r, move_q) in possible:
            shallow_self = self_tokens.copy()
            shallow_self = \
                self.adjust_list(consider, shallow_self, move_r, move_q)

            shallow_opp = opponent_tokens.copy()
            row_utility = self.build_by_row(consider, enemy_token, enemy_moves, 
                                            shallow_self, shallow_opp)

            # put it back to its original spot
            shallow_self = \
                self.adjust_list(consider, shallow_self, ori_r, ori_q)

            if len(row_utility) != 0:
                util_matrix.append(row_utility)
                          
        return util_matrix, possible, enemy_moves
    
    def build_by_row(self, consider, enemy_token, 
                    enemy_moves, shallow_self, shallow_opp):

        row_utility = list()
        (ori_r, ori_q) = (enemy_token.r, enemy_token.q)

        for (opp_r, opp_q) in enemy_moves:
            shallow_opp = \
                self.adjust_list(enemy_token, shallow_opp, opp_r, opp_q)
        
            # now we have the modified lists of tokens, 
            # i.e. a gamestate where two moves have been taken
            alive_self, alive_opp = self.board.battle(shallow_self, shallow_opp)

            row_utility.append(self.simple_eval(consider, 
                                alive_self, alive_opp, enemy_token))

            shallow_opp = \
                self.adjust_list(enemy_token, shallow_opp, ori_r, ori_q)
        
        return row_utility

    def simple_eval(self, cur_token, self_tokens, opponent_tokens, enemy_token):
        """
        return evaluation of player tokens moves
        """
        difference = 10
        if isinstance(enemy_token, cur_token.enemy):
            difference += self.target_eval(cur_token, enemy_token)
            difference += self.kill_eval(cur_token, enemy_token)
        else:
            difference -= self.avoid_eval(cur_token, enemy_token)
            difference -= self.death_eval(cur_token, enemy_token)
        difference -= self.ally_eval(cur_token, self_tokens)
        difference -= self.border_eval(cur_token)
        return difference

    def target_eval(self, cur_token, enemy_token):
        """
        return evaluation score based on distance to a target token to attack
        """
        w = 1
        distance = cur_token.hex_distance([cur_token.r, cur_token.q], 
                                            [enemy_token.r, enemy_token.q])
        if distance:
            return w * (((10/distance) * (distance + 1)) / 10)
        return w

    def kill_eval(self, cur_token, enemy_token):
        """
        return evaluation score based on ability to kill a token
        """
        w = 40
        distance = cur_token.euclidean_distance([cur_token.r, cur_token.q], 
                                                [enemy_token.r, enemy_token.q])
        if distance == 0:
            return w
        return 0

    def avoid_eval(self, cur_token, enemy_token):
        """
        return evaluation score based on 
        distance to an enemy token to escape from
        """
        w = 10
        distance = cur_token.hex_distance([cur_token.r, cur_token.q], 
                                        [enemy_token.r, enemy_token.q])
        if distance:
            return w * (((10/distance) * (distance + 1)) / 10)
        return w
    
    def death_eval(self, cur_token, enemy_token):
        """
        return evaluation score based on ability for a token to die from enemy
        """
        w = 50
        distance = cur_token.euclidean_distance([cur_token.r, cur_token.q], 
                                                [enemy_token.r, enemy_token.q])
        if distance == 0:
            return w
        return 0

    def ally_eval(self, cur_token, self_tokens):
        """
        return evaluation score based on ability to kill an ally token
        """
        w = 50
        team_kill = [(token.r, token.q) for token in self_tokens 
                    if isinstance(token, cur_token.enemy) or 
                    isinstance(token, cur_token.avoid) or 
                    isinstance(cur_token, token.avoid) or 
                    isinstance(cur_token, token.enemy)]
        return w if (cur_token.r, cur_token.q) in team_kill else 0

    def border_eval(self, cur_token):
        """
        return evaluation score based on if the token is on a border tile
        """
        w = 50
        border = len([(r, q) for (r, q) in 
                    cur_token.get_adj_hex(cur_token.r, cur_token.q) 
                    if self.board.check_bounds(r, q)]) != 6
        return w if border else 0
    
    def swing_eval(self, cur_token, self_tokens):
        """
        return evaluation score based on ability for a token to swing
        """
        w = 10
        adj = set(cur_token.get_adj_hex(cur_token.r, cur_token.q))
        allies = set([(token.r, token.q) for token in self_tokens])
        return w if adj.intersection(allies) else 0
    
    def lookahead(self, consider, target, self_tokens, opponent_tokens, depth):
        """
        Carries out the search in a tree of utility matrices 
        to find the best action for our token.
        Returns the SUM utility of best moves seen
        consider: a token of ours that we're thinking to move
        depth: terminal limit, i.e. number of moves we're looking ahead

        # wip: pruning, and maybe recognizing repeated states
        """
        # cache original token & enemy token coords
        ori_r, ori_q = consider.r, consider.q
        opp_r, opp_q = target.r, target.q

        # we stop recursing if we hit a limit, and returns the value of playing to this gamestate
        if depth == 3:
            util_matrix, my_moves, opp_moves = self.build_utility(consider, target, self_tokens, opponent_tokens)
            opp_util, _a, _b = self.build_utility(target, consider, opponent_tokens, self_tokens)
            util_matrix = self.remove_dom(np.array(util_matrix), np.array(opp_util), my_moves, opp_moves)
            sol, val = solve_game(np.array(util_matrix), maximiser=True, rowplayer=True)
            return val, my_moves

        util_matrix, my_moves, opp_moves = self.build_utility(consider, target, self_tokens, opponent_tokens)
        # change is here! carry out iterative removal
        opp_util, _a, _b = self.build_utility(target, consider, opponent_tokens, self_tokens)
        util_matrix = self.remove_dom(np.array(util_matrix), np.array(opp_util), my_moves, opp_moves)
        
        sol_best, val_best = solve_game(util_matrix, maximiser=True, rowplayer=True)
        consider.move(ori_r, ori_q)

        # fix what our best move is
        sol_best = sol_best.tolist()
        (best_r, best_q) = my_moves[sol_best.index(max(sol_best))]
        if (consider, best_r, best_q) in self.history and len(my_moves) > 1 and len(self.history) >= 5:
            my_moves.remove((best_r, best_q))
            sol_best.remove(max(sol_best))
            (best_r, best_q) = my_moves[sol_best.index(max(sol_best))]
        new_self = self.adjust_list(consider, self_tokens, best_r, best_q)

        max_value = 0

        # explore the possible moves opp can take
        for move in opp_moves:
            opp_r, opp_q = move
            # adjust opp's list, and recurse
            new_opp = self.adjust_list(target, opponent_tokens, opp_r, opp_q)
            val, best_move = self.lookahead(consider, 
                                    target, new_self, new_opp, depth + 1)
            target.move(opp_r, opp_q)

            if val > max_value:
                max_value = val
        
        return val_best + max_value, (best_r, best_q)

    """
    Carry out iterated removal of dominated strategies
    """
    def remove_dom(self, my_util, opp_util, my_valid_moves, opp_valid_moves):
    
        # check if there's any dominated strategies in the matrices
        has_change1 = True
        has_change2 = True

        while has_change1 or has_change2:
            my_util, my_valid_moves, opp_util, has_change1 = \
                self.check_for_dom(my_util, my_valid_moves, opp_util)
            opp_util, opp_valid_moves, my_util, has_change2 = \
                self.check_for_dom(opp_util, opp_valid_moves, my_util)
        return my_util

    """
    Carries out dominated strategy removal, 
    to result in a smaller payoff matrix
    my_util: Utility matrix for token in consideration
    my_valid_moves: List of corresponding moves
    """
    def check_for_dom(self, my_util, my_valid_moves, opp_util):
        
        # print("my util's shape: " + str(my_util.shape) + "len of moves: " + str(len(my_valid_moves)))
        # print("opp util's shape: " + str(opp_util.shape))

        # sort in descending order by sum, in order to get what most likely will be dominator
        sorted_util = sorted(my_util, key=sum, reverse=True)
        has_change = False

        # check to see if any ROW dominates another
        dominator = sorted_util[0]
        to_remove = list()
        for i in range(len(my_util)):
            
            row = my_util[i]
            if self.dominates(dominator, row):
                to_remove.append(i)
                has_change = True

        # remove the dominated strategies
        my_util = np.delete(my_util, to_remove, axis = 0)
        opp_util = np.delete(opp_util, to_remove, axis = 1)
        
        # remove from move list
        for j in sorted(to_remove, reverse=True):
            del my_valid_moves[j]

        return my_util, my_valid_moves, opp_util, has_change

    def dominates(self, row1, row2):
        dom = row1 > row2
        return dom.all()