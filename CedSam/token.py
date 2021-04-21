from CedSam.side import Upper
from math import sqrt

class Token():

    def __init__(self, name, side, r, q):
        self.side = side
        self.name = name.upper() if side is Upper else name
        self.r = r
        self.q = q

    # move token and print move to console
    def move(self, r, q):
        self.r = r
        self.q = q

    # generate list of adjacent her tiles of current her tile
    def get_adj_hex(self, r, q):
        return [(r, q-1), (r-1, q), (r+1, q), 
                (r, q+1), (r-1, q+1), (r+1, q-1)]

    def hex_distance(self, a, b):
        a_r, a_q = a
        b_r, b_q = b
        return (abs(a_q - b_q) + abs(a_q + a_r - b_q - b_r) + abs(a_r - b_r)) / 2

    def euclidean_distance(self, a, b):
        a_r, a_q = a
        b_r, b_q = b
        return sqrt((a_r - b_r)**2 + (a_q - b_q)**2 - ((a_r - b_r)*(a_q - b_q)))

class Rock(Token):
    def __init__(self, side, r, q):
        self.avoid = Paper
        self.enemy = Scissors
        super().__init__('r', side, r, q)

class Paper(Token):
    def __init__(self, side, r, q):
        self.avoid = Scissors
        self.enemy = Rock
        super().__init__('p', side, r, q)

class Scissors(Token):
    def __init__(self, side, r, q):
        self.avoid = Rock
        self.enemy = Paper
        super().__init__('s', side, r, q)