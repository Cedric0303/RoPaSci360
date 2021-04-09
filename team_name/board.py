from class import Upper, Lower

class Board():

    # generate token classes of players 
    # with their coordinates and block tokens
    def __init__(self, token_data):
        self.upper = Upper(token_data['upper'])
        self.lower = Lower(token_data['lower'])
        self.turn = 0
        
    # default size of board
    size = range(-4, +4+1)

    # create dict of tokens on occupied hex tiles
    # from tokens of player classes
    def create_dict(self):
        output_dict = dict()
        for token in self.upper.token_list + \
                    self.lower.token_list + \
                    self.block.token_list:
            if token.coord not in output_dict:
                output_dict[token.coord] = [token]
            else:
                output_dict[token.coord].append(token)
        return output_dict

    def next_turn(self):
        self.turn += 1

    # check if a coordinate is within board boundaries
    def check_bounds(x, y):
        return x in Board.size and y in Board.size and ((-x) - y) in Board.size

    # set up fighting mechanic, 
    # where it takes a dict of all tokens on all coords, 
    # updates surviving tokens of Upper & Lower class after battle
    # and update board Upper and Lower classes
    def battle(self, coord_dict):
        
        alive_tokens = dict()

        self.upper.clear_token_list()
        self.lower.clear_token_list()

        # decide what token dies
        for coord, tokens in coord_dict.items():

            # paper_die = False
            # scissor_die = False
            # rock_die = False

            if len(tokens) > 1:

                paper_die = False
                scissor_die = False
                rock_die = False

                for token in tokens:
                    ttype = token.name.lower()
                    if ttype == 'p':
                        rock_die = True
                    elif ttype == 'r':
                        scissor_die = True
                    elif ttype == 's':
                        paper_die = True

                # create list of surviving tokens
                for token in tokens:
                    ttype = token.name.lower()
                    if (ttype == 'p' and paper_die == False) or \
                        (ttype == 'r' and rock_die == False) or \
                        (ttype == 's' and scissor_die == False):
                        if coord not in alive_tokens:
                            alive_tokens[coord] = [token]
                        else:
                            alive_tokens[coord].append(token)
            
            # single token or tokens of same type on a hex tile
            else:
                if coord not in alive_tokens:
                    alive_tokens[coord] = tokens
                else:
                    alive_tokens[coord].append(token)
        # re-insert surviving tokens into player classes
        for (x, y), tokens in alive_tokens.items():
            for token in tokens:
                if token.name.isupper():
                    self.upper = Upper([[token.name.upper(), x ,y]])
                elif token.name.islower():
                    self.lower = Lower([[token.name, x ,y]])
        return alive_tokens