from random import randint

from AbstractStrategy import AbstractStrategy


class BasicStrategy(AbstractStrategy):
    def __init__(self, game):
        AbstractStrategy.__init__(self, game)
        self._actions = ['left', 'right', 'turnleft', 'turnright', 'down', 'drop']

    def score_heuristic(self, new_field):
        for row in new_field.field:
            if all(row):
                return True
        return False

    def height_heuristic(self, new_field):
        for row in new_field.rows:
            for i, row in enumerate(new_field.field):
                if any(row):
                    return new_field.height - i

    def choose(self):
        ind = [randint(0, 4) for _ in range(1, 10)]
        moves = map(lambda x: self._actions[x], ind)
        moves.append('drop')

        return moves
