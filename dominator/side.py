from sys import maxsize

class Side():

    # return the enemy token nearest to the supplied Upper token
    def pick_nearest(self, token, lowers):
        nearest = maxsize
        best_target = False
        for target in lowers.token_list:
            if isinstance(target, token.enemy):
                distance = token.hex_distance(token.coord, target.coord)
                if distance < nearest:
                    nearest = distance
                    best_target = target
        return best_target

class Upper(Side):
    def __init__(self):
        pass

class Lower(Side):
    def __init__(self):
        pass


