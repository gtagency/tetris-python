from random import randint

from AbstractStrategy import AbstractStrategy

class AnacondaPlan(AbstractStrategy):
    def __init__(self, game):
        AbstractStrategy.__init__(self, game)
        self.actions = ['left', 'right', 'turnleft', 'turnright', 'down', 'drop']

    def choose(self):
        ind = [randint(0, 4) for _ in range(1, 10)]
        moves = map(lambda x: self.actions[x], ind)
        moves.append('drop')

        #output
        return moves
