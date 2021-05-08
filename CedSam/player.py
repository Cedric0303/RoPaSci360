from random import choice, randrange
import numpy as np
from numpy.lib.function_base import diff
from scipy.sparse.linalg.isolve.iterative import qmr
from CedSam.board import Board
from CedSam.side import Lower, Upper
from CedSam.token import Rock, Paper, Scissors
from CedSam.gametheory2 import solve_game
from timeit import default_timer as timer

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
        if len(self.history) > 5: 
            del self.history[0]

        beatable = [type(opponent) for token in self.self_tokens for opponent in self.opponent_tokens if isinstance(opponent, token.enemy)]
        
        if self.self_tokens: 
            if beatable:# and self.turn % 10:
                token_best_move = dict()

                # save current opponent coords
                if self.opponent_tokens:
                    cache_oppo = [(each.r, each.q) for each in self.opponent_tokens]
                if self.self_tokens:
                    cache_self = [(each.r, each.q) for each in self.self_tokens]
                
                if len(self.self_tokens) > 1:
                    for token in self.self_tokens:
                        best_val = -100
                        both = [target for target in self.opponent_tokens if isinstance(target, token.enemy)] + [enemy for enemy in self.opponent_tokens if isinstance(enemy, token.avoid)]
                        if both:
                            while both:
                                opponent = both.pop(0)
                                val = self.target_eval(token, opponent)
                                if val > best_val:
                                    best_val = val
                        else:
                            continue
                        token_best_move[token] = best_val
                    move_token = max(token_best_move, key=lambda key: token_best_move[key])
                else:
                    move_token = self.self_tokens[0]
                    
                ori_r, ori_q = move_token.r, move_token.q
                (best_r, best_q) = False, False
                best_val = -100
                targets = sorted([(target, move_token.euclidean_distance([move_token.r, move_token.q], [target.r, target.q])) for target in self.opponent_tokens if isinstance(target, move_token.enemy)], key=lambda targets:targets[1])
                enemies = sorted([(enemy, move_token.euclidean_distance([move_token.r, move_token.q], [enemy.r, enemy.q])) for enemy in self.opponent_tokens if isinstance(enemy, move_token.avoid)], key=lambda enemies:enemies[1])
                if len(targets) > 2:
                    targets = targets[:1]
                if len(enemies) > 2:
                    enemies = enemies[:1]
                both = targets + enemies
                while both:
                    opponent, dist = both.pop(0)
                    self_tokens = self.self_tokens.copy()
                    self_oppo = self.opponent_tokens.copy()
                    start = timer()
                    val, move = self.lookahead(move_token, opponent, self_tokens, self_oppo, depth = 0)
                    end = timer()
                    if val > best_val:
                        best_val = val
                        (best_r, best_q) = move
                    move_token.r, move_token.q = ori_r, ori_q
                if best_val == -100:
                    (best_r, best_r) = choice([(r, q) for (r, q) in move_token.get_adj_hex(move_token.r, move_token.q) if Board.check_bounds(r, q)])

                if self.opponent_tokens:
                    for i in range(len(cache_oppo)):
                        c_r, c_q = cache_oppo[i]
                        self.opponent_tokens[i].move(c_r, c_q)
                if self.self_tokens:
                    for i in range(len(cache_self)):
                        c_r, c_q = cache_self[i]
                        self.self_tokens[i].move(c_r, c_q)

                self.history.append((move_token, best_r, best_q))
                if move_token.hex_distance([move_token.r, move_token.q], [best_r, best_q]) > 1:
                    return ("SWING", (move_token.r, move_token.q), (best_r, best_q))
                else:
                    return ("SLIDE", (move_token.r, move_token.q), (best_r, best_q))

            elif not self.throws:
                token = choice(self.self_tokens) if len(self.self_tokens) > 1 else self.self_tokens[0]
                (best_r, best_q) = choice([(r, q) for (r, q) in token.get_adj_hex(token.r, token.q) if Board.check_bounds(r, q)])
                if token.hex_distance([token.r, token.q], [best_r, best_q]) > 1:
                    return ("SWING", (token.r, token.q), (best_r, best_q))
                else:
                    return ("SLIDE", (token.r, token.q), (best_r, best_q))
        
        tokens = list(map(type, self.self_tokens + self.opponent_tokens))
        ttypes_on_board = int(Paper in tokens) + int(Rock in tokens) + int(Scissors in tokens)

        if self.throws and (not self.self_tokens or ttypes_on_board == 1 or not beatable  or not self.turn % 10):
            # throw
            if self.opponent_tokens:
                random_enemy = choice(self.opponent_tokens)
                find_enemy = [each for each in self.throws if isinstance(each, random_enemy.avoid)]
                if find_enemy:
                    token = choice(find_enemy)
                    self.throws.remove(token)
                else:
                    token = self.throws.pop(self.throws.index(choice(self.throws)))
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
                self.max_throw += 1

        elif "SLIDE" == player_action[0] or "SWING" == player_action[0]:
            # self swing/slide
            prev_r, prev_q = player_action[1]
            next_r, next_q = player_action[2]
            for i in range(len(self.self_tokens)):
                if (self.self_tokens[i].r == prev_r and self.self_tokens[i].q == prev_q):
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
                    self.opponent_tokens[i].move(next_r, next_q)
                    break

        new_self, new_oppo = self.board.battle(self.self_tokens, self.opponent_tokens)
        self.kills += (len(self.opponent_tokens) - len(new_oppo))
        self.deaths += (len(self.self_tokens) - len(new_self))
        self.self_tokens, self.opponent_tokens = new_self, new_oppo
        self.turn += 1

    # Adjusts a list of tokens to provide updated list
    def adjust_list(self, token, token_list, new_r, new_q):
        token_list[token_list.index(token)].move(new_r, new_q)
        return token_list

    """
    Builds a 2-d utility matrix in a list of lists.
    Also returns a list of the valid moves we and the opponent can make.
    token_considered: our token, which we're calculating utility for
    enemy_token: opponent's token, can be either target to kill, or enemy to avoid

    e.g. [[1,2,4,5], [2,4,8,6]]
    """
    def build_utility(self, token_considered, enemy_token, self_tokens, opponent_tokens):
        
        self_coord = [(token_considered.r, token_considered.q)]
        oppo_coord = [(enemy_token.r, enemy_token.q)]
        util_matrix = list()
        token_adj = [(r, q) for (r, q) in token_considered.get_adj_hex(token_considered.r, token_considered.q) if Board.check_bounds(r, q)]
        for token in self_tokens:
            if (token.r, token.q) in token_adj:
                token_adj += [(r, q) for (r, q) in token.get_adj_hex(token.r, token.q) if Board.check_bounds(r, q)]
                self_coord.append((token.r, token.q))
        enemy_adj = [(r, q) for (r, q) in enemy_token.get_adj_hex(enemy_token.r, enemy_token.q) if Board.check_bounds(r, q)]
        for token in opponent_tokens:
            if (token.r, token.q) in enemy_adj:
                enemy_adj += [(r, q) for (r, q) in token.get_adj_hex(token.r, token.q) if Board.check_bounds(r, q)]
                self_coord.append((token.r, token.q))
        token_adj = [coord for coord in token_adj if coord not in self_coord]
        enemy_adj = [coord for coord in enemy_adj if coord not in oppo_coord]

        opp_valid_moves = list()
        my_valid_moves = list()

        # possible = token_adj
        # enemy_moves = enemy_adj

        possible = {(r,q): token_considered.euclidean_distance((r,q), (enemy_token.r, enemy_token.q)) for (r, q) in token_adj}
        enemy_moves = {(r,q): token_considered.euclidean_distance((r,q), (token_considered.r, token_considered.q)) for (r, q) in enemy_adj}

        if isinstance(enemy_token, token_considered.enemy):
            possible = sorted(possible.items(), key=lambda possible:possible[1])
            enemy_moves = sorted(enemy_moves.items(), key=lambda enemy_moves:enemy_moves[1], reverse=True)
        else:
            possible = sorted(possible.items(), key=lambda possible:possible[1], reverse=True)
            enemy_moves = sorted(enemy_moves.items(), key=lambda enemy_moves:enemy_moves[1])
        
        if len(possible) > 2:
            possible = possible [:(len(possible) // 2) + 1]
        if len(enemy_moves) > 2:
            enemy_moves = enemy_moves[:(len(enemy_moves) // 2) + 1]
        possible = [coord for coord, val in possible]
        enemy_moves = [coord for coord, val in enemy_moves]

        # enumerate all possible moves for our token
        for move_r, move_q in possible:
            shallow_self = self_tokens.copy()
            shallow_self = self.adjust_list(token_considered, shallow_self, move_r, move_q)
            my_valid_moves.append((move_r, move_q))

            row_utility = list()

            for opp_r, opp_q in enemy_moves:
                shallow_opp = opponent_tokens.copy()
                shallow_opp = self.adjust_list(enemy_token, shallow_opp, opp_r, opp_q)
                opp_valid_moves.append((opp_r, opp_q))

                # now we have the modified lists of tokens, i.e. a gamestate where two moves have been taken
                alive_self, alive_opp = self.board.battle(shallow_self, shallow_opp)

                row_utility.append(self.simple_eval(token_considered, alive_self, alive_opp, enemy_token))
        
            # don't add in an empty list if the opp move was invalid
            if len(row_utility) != 0:
                util_matrix.append(row_utility)                     
        return util_matrix, my_valid_moves, opp_valid_moves

    # Returns simple evaluation of player tokens minus opponent tokens
    def simple_eval(self, cur_token, self_tokens, opponent_tokens, enemy_token):
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
        w = 1
        distance = cur_token.hex_distance([cur_token.r, cur_token.q], [enemy_token.r, enemy_token.q])
        if distance:
            return w * (((10/distance) * (distance + 1)) / 10)
        return w

    def kill_eval(self, cur_token, enemy_token):
        w = 40
        distance = cur_token.euclidean_distance([cur_token.r, cur_token.q], [enemy_token.r, enemy_token.q])
        if distance == 0:
            return w
        return 0

    def avoid_eval(self, cur_token, enemy_token):
        w = 10
        distance = cur_token.hex_distance([cur_token.r, cur_token.q], [enemy_token.r, enemy_token.q])
        if distance:
            return w * (((10/distance) * (distance + 1)) / 10)
        return w
    
    def death_eval(self, cur_token, enemy_token):
        w = 50
        distance = cur_token.euclidean_distance([cur_token.r, cur_token.q], [enemy_token.r, enemy_token.q])
        if distance == 0:
            return w
        return 0

    def ally_eval(self, cur_token, self_tokens):
        w = 50
        team_kill = [(token.r, token.q) for token in self_tokens if isinstance(token, cur_token.enemy) or isinstance(token, cur_token.avoid) or 
                                                                    isinstance(cur_token, token.avoid) or isinstance(cur_token, token.enemy)]
        return w if (cur_token.r, cur_token.q) in team_kill else 0

    def border_eval(self, cur_token):
        w = 50
        border = len([(r, q) for (r, q) in cur_token.get_adj_hex(cur_token.r, cur_token.q) if self.board.check_bounds(r, q)]) != 6
        return w if border else 0
    
    def swing_eval(self, cur_token, self_tokens):
        w = 10
        adj = set(cur_token.get_adj_hex(cur_token.r, cur_token.q))
        allies = set([(token.r, token.q) for token in self_tokens])
        return w if adj.intersection(allies) else 0
    
    """
    Carries out the search in a tree of utility matrices to find the best action for our token.
    Returns the SUM utility of best moves seen
    token_considered: a token of ours that we're thinking to move
    depth: terminal limit, i.e. number of moves we're looking ahead

    # wip: pruning, and maybe recognizing repeated states
    """
    def lookahead(self, token_considered, target, self_tokens, opponent_tokens, depth):
        ori_r, ori_q = token_considered.r, token_considered.q
        opp_r, opp_q = target.r, target.q

        # we stop recursing if we hit a limit, and returns the value of playing to this gamestate
        if depth == 3:
            util_matrix, my_moves, opp_moves = self.build_utility(token_considered, target, self_tokens, opponent_tokens)
            sol, val = solve_game(np.array(util_matrix), maximiser=True, rowplayer=True)
            return val, my_moves

        util_matrix, my_moves, opp_moves = self.build_utility(token_considered, target, self_tokens, opponent_tokens)
        sol_best, val_best = solve_game(np.array(util_matrix), maximiser=True, rowplayer=True)
        token_considered.move(ori_r, ori_q)

        # fix what our best move is
        sol_best = sol_best.tolist()
        (best_r, best_q) = my_moves[sol_best.index(max(sol_best))]
        if (token_considered, best_r, best_q) in self.history and len(my_moves) > 1 and len(self.history) == 5:
            my_moves.remove((best_r, best_q))
            sol_best.remove(max(sol_best))
            (best_r, best_q) = my_moves[sol_best.index(max(sol_best))]
        new_self = self.adjust_list(token_considered, self_tokens, best_r, best_q)

        max_value = 0

        # explore the possible moves opp can take
        for move in opp_moves:
            opp_r, opp_q = move
            # adjust opp's list, and recurse
            new_opp = self.adjust_list(target, opponent_tokens, opp_r, opp_q)
            val, best_move = self.lookahead(token_considered, target, new_self, new_opp, depth + 1)
            target.move(opp_r, opp_q)

            if val > max_value:
                max_value = val
        
        return val_best + max_value, (best_r, best_q)