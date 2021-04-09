import math
import sys
import board

class Token():

    def __init__(self, name, x, y):
        self.name = name
        self.coord = x, y
        self.target = False
        self.next_move = None
        self.path = False    

    # move token and print move to console
    def move(self, coord):
        distance = self.calc_distance(self.coord, coord)
        self.coord = coord
        if self.target:
            if self.coord == self.target.coord:
                self.target = False
        self.path.pop(0)

    def initialize_move(self):
        self.next_move = self.path[0]
        return self

    # calculate nearest distance of token and it's target,
    # return max value if token has no target,
    # act as key for move_array sorting
    def nearest_distance(self):
        if not self.target:
            return sys.maxsize
        return self.calc_distance(self.target.coord, self.next_move)

    def set_target(self, target):
        self.target = target

    # generate list of adjacent hex tiles of current hex tile
    def get_adj_hex(coord):
        (x, y) = coord
        adj_list = [(x, y-1), (x-1, y), (x+1, y), 
                    (x, y+1), (x-1, y+1), (x+1, y-1)]
  
        return adj_list

    # calculate Euclidean line distance between two tokens' coordinates
    def calc_distance(self, token1, token2):
        (x1, y1) = token1
        (x2, y2) = token2
        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return dist

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