from sys import stdin, stdout

from Bot import Planner
from Bot.Game.Game import Game
from Bot.Parser import Parser


class Bot:
    def __init__(self, strategy):
        self.game = Game()
        self._parser = Parser(self.game)
        self._planner = Planner.create(strategy, self.game)

    def run(self):
        while not stdin.closed:
            try:
                line = stdin.readline().strip()

                if len(line) == 0:
                    continue

                moves = self.interpret(line)

                if moves:
                    self.sendMoves(moves)

            except EOFError:
                return

    def interpret(self, line):
        if line.startswith('action'):
            return self._planner.makeMove()
        else:
            self._parser.parse(line)

    @staticmethod
    def sendMoves(moves):
        stdout.write(','.join(moves) + '\n')
        stdout.flush()


if __name__ == '__main__':
    Bot("random").run()