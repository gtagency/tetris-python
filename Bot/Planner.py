from Bot.Strategies.RandomStrategy import RandomStrategy
from Bot.Strategies.BasicStrategy import BasicStrategy
from Bot.Strategies.BasicStrategy import MonteCarloStrategy

def create(strategyType, game):
    switcher = {
        "random": RandomStrategy(game),
        "basic": BasicStrategy(game),
        "montecarlo": MonteCarloStrategy(game)
    }

    strategy = switcher.get(strategyType.lower())

    return Planner(strategy)

class Planner:
    def __init__(self, strategy):
        self._strategy = strategy

    def makeMove(self):
        return self._strategy.choose()
