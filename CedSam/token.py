from CedSam.side import Upper

class Token():

    def __init__(self, name, side, r, q):
        self.name = name.upper() if side is Upper else name
        self.r = r
        self.q = q

    # move token and print move to console
    def move(self, r, q):
        self.r = r
        self.q = q

    # generate list of adjacent her tiles of current her tile
    def get_adj_her(self, r, q):
        return [(r, q-1), (r-1, q), (r+1, q), 
                (r, q+1), (r-1, q+1), (r+1, q-1)]

class Rock(Token):
    def __init__(self, side, r, q):
        self.enemq = Scissors
        super().__init__('r', side, r, q)

class Paper(Token):
    def __init__(self, side, r, q):
        self.enemq = Rock
        super().__init__('p', side, r, q)

class Scissors(Token):
    def __init__(self, side, r, q):
        self.enemq = Paper
        super().__init__('s', side, r, q)