from CedSam.token import Paper, Rock, Scissors

class Board():

    # default size of board
    size = range(-4, +4+1)

    # check if a coordinate is within board boundaries
    @staticmethod
    def check_bounds(x, y):
        return x in Board.size and y in Board.size and ((-x) - y) in Board.size

    # generate token classes of players 
    # with their coordinates and block tokens
    def __init__(self, side):
        self.side = side

    # create dict of tokens on occupied hex tiles
    # from tokens of player classes
    def create_dict(self, self_tokens, opponent_tokens):
        output_dict = dict()
        for token in self_tokens +  opponent_tokens:
            token_coord = (token.r, token.q)
            if token_coord not in output_dict:
                output_dict[token_coord] = [token]
            else:
                output_dict[token_coord].append(token)
        return output_dict

    # set up fighting mechanic, 
    # where it takes a dict of all tokens on all coords, 
    # updates surviving tokens of Upper & Lower class after battle
    # and update board Upper and Lower classes
    def battle(self, self_tokens, opponent_tokens):
        
        alive_tokens = list()
        coord_dict = self.create_dict(self_tokens, opponent_tokens)

        # decide what token dies
        for coord, tokens in coord_dict.items():

            if len(tokens) > 1:
                paper_die = False
                scissor_die = False
                rock_die = False

                for token in tokens:
                    if isinstance(token, Paper): rock_die = True
                    if isinstance(token, Rock): scissor_die = True
                    if isinstance(token, Scissors): paper_die = True

                # create list of surviving tokens
                for token in tokens:
                    if (isinstance(token, Paper) and paper_die == False) or \
                        (isinstance(token, Rock) and rock_die == False) or \
                        (isinstance(token, Scissors) and scissor_die == False):
                            alive_tokens.append(token)
            
            # single token or tokens of same type on a hex tile
            else:
                [token] = tokens
                alive_tokens.append(token)
        alive_self = list()
        alive_oppo = list()
        for token in alive_tokens:
            if token in self_tokens:
                alive_self.append(token)
            else:
                alive_oppo.append(token)
        return alive_self, alive_oppo