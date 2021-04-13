from sys import maxsize
from math import dist

class Token():

    def __init__(self, name, x, y):
        self.name = name
        self.coord = x, y
        self.next_move = None

    # move token and print move to console
    def move(self, coord):
        self.coord = coord

    def initialize_move(self):
        self.next_move = self.path[0]

    # calculate nearest distance of token and it's target,
    # return max value if token has no target,
    # act as key for move_array sorting
    # def nearest_distance(self):
    #     if not self.target:
    #         return maxsize
    #     return dist(self.target.coord, self.next_move)

    # def set_target(self, target):
    #     self.target = target

    # generate list of adjacent hex tiles of current hex tile
    def get_adj_hex(coord):
        (x, y) = coord
        adj_list = [(x, y-1), (x-1, y), (x+1, y), 
                    (x, y+1), (x-1, y+1), (x+1, y-1)]
  
        return adj_list

class Rock(Token):

    def __init__(self, name, x, y):
        self.enemy = Scissors
        super().__init__(name, x, y)

class Paper(Token):

    def __init__(self, name, x, y):
        self.enemy = Rock
        super().__init__(name, x, y)

class Scissors(Token):

    def __init__(self, name, x, y):
        self.enemy = Paper
        super().__init__(name, x, y)