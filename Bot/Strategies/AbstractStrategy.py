class AbstractStrategy:
    def __init__(self, game):
        self._game = game

    def choose(self):
        raise NotImplementedError("Please Implement this method")