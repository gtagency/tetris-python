from random import randint

from AbstractStrategy import AbstractStrategy

def score_heuristic(new_field):
    for row in new_field.field:
        if all(row):
            return True
    return False

def height_heuristic(new_field):
    for row in new_field.rows:
        for i, row in enumerate(new_field.field):
            if any(row):
                return new_field.height - i

def dfs(node, depth):
    currentDepth = depth
    for child in node.getAllChildren():
        if not child in node.children && currentDepth > 0:
            node.children.append(child)
            dfs(child, currentDepth--)

class BasicStrategy(AbstractStrategy):
    def __init__(self, game):
        AbstractStrategy.__init__(self, game)
        self._actions = ['left', 'right', 'turnleft', 'turnright', 'down', 'drop']

    def choose(self):
        ind = [randint(0, 4) for _ in range(1, 10)]
        moves = map(lambda x: self._actions[x], ind)
        moves.append('drop')

        return moves

class Node(object):

    def __init__(self, state, parent):
        self.state = state
        self.children = []
        self.parent = parent
        self.visits = 0
        self.reward = 0

class MonteCarloStrategy(AbstractStrategy):
    def __init__(self, game):
        AbstractStrategy.__init__(self, game)
        self._actions = ['left', 'right', 'turnleft', 'turnright', 'down', 'drop']

    def generateMCTree(self):
        currentState = game.player.field
        root = Node(currentState)

        # DO THIS PLS
        stateChildren = root.state.getChildren(game.piece)
        for i in xrange(len(stateChildren)):
            child = Node(stateChildren[i], root)
            dfs(child, 3)
            root.children.append(child)
        return root

    def choose(self):
        # Generate Monte Carlo Tree.
        tree = self.generateMCTree()

        # Fallback to random strategy.
        ind = [randint(0, 4) for _ in range(1, 10)]
        moves = map(lambda x: self._actions[x], ind)
        moves.append('drop')

        return moves

