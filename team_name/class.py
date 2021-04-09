import collections
import board
import sys
from token import Token, Rock, Paper, Scissors, Block

class Player():

    token_list = list()

    def clear_token_list(self):
        self.token_list.clear()

    # return the enemy token nearest to the supplied Upper token
    def pick_nearest(self, token, lowers):
        nearest = sys.maxsize
        best_target = False
        for target in lowers.token_list:
            if isinstance(target, token.enemy):
                distance = token.calc_distance(token.coord, target.coord)
                if distance < nearest:
                    nearest = distance
                    best_target = target
        return best_target

class Upper(Player):

    token_list = list()

    def __init__(self, token_data):
        self.name = 'upper'
        for token, x, y in token_data:
            if token == 'r':
                self.token_list.append(Rock(token.upper(), x, y))
            elif token == 'p':
                self.token_list.append(Paper(token.upper(), x, y))
            elif token == 's':
                self.token_list.append(Scissors(token.upper(), x, y))

    # def get_path(token, blocks, enemies, token_list):
    #     queue = collections.deque([[token.coord]])
    #     seen = set([token.coord])
    #     other_enemies = set(enemies)
    #     other_enemies.remove(token.target.coord)

    #     while queue:
    #         path = queue.popleft()
    #         x, y = path[-1]
    #         if (x, y) == token.target.coord:
    #             path.pop(0)
    #             return path
    #         temp_list = Token.get_adj_hex((x,y))
    #         for coord in [each.coord for each in token_list]:
    #             immediate_adj = Token.get_adj_hex((token.coord))
    #             if coord in immediate_adj and coord in temp_list:
    #                 temp_list.remove(coord)
    #                 adjacent = Token.get_adj_hex(coord)
    #                 for (x3, y3) in adjacent:
    #                     temp_list.append((x3, y3))
    #         for (x2, y2) in temp_list:
    #             if board.Board.check_bounds(x2, y2) and \
    #             (x2, y2) not in blocks and (x2, y2) not in seen and \
    #             (x2, y2) not in other_enemies:
    #                 queue.append(path + [(x2, y2)])
    #                 seen.add((x2, y2))
    #     return False

    # carry out moves for Upper player each turn
    def play(self, board):
        return

class Lower(Player):
    
    token_list = list()

    def __init__(self, token_data):
        self.name = 'lower'
        for token, x, y in token_data:
            if token == 'r':
                self.token_list.append(Rock(token.lower(), x, y))
            elif token == 'p':
                self.token_list.append(Paper(token.lower(), x, y))
            elif token == 's':
                self.token_list.append(Scissors(token.lower(), x, y))


