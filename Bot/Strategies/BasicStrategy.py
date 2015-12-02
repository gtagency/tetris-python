from random import randint
from AbstractStrategy import AbstractStrategy
from math import log

def score_heuristic(new_field):
    score = 0
    for row in field:
        if all(row):
            score += 1
    return float(score) / len(new_field.field)

def height_heuristic(new_field):
    for row in new_field:
        if any(row):
            return float(len(new_field) - i) / len(new_field)

def dfs(node, depth):
    currentDepth = depth
    for child in node.state.getAllChildren():
        if not child in node.children and currentDepth > 0:
            node.children.append(child)
            dfs(child, currentDepth-1)

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
        currentState = self._game.me.field
        root = Node(currentState, None)

        stateChildren = root.state.getChildren(self._game.piece)
        for i in xrange(len(stateChildren)):
            child = Node(stateChildren[i], root)
            dfs(child, 3)
            root.children.append(child)
        return root

    def pickBestChild(self, root):
        C = 2**(1/2)
        currentVisits = root.visits
        # exploration / exploitation
        score = lambda x: ((float(x.reward) / x.visits) + C * (2 * log(float(x.visits) / currentVisits))**(1/2))
        childList = root.children
        _, best = max([(score(child), child) for child in childList])
        return best

    def evaluate(self, root):
        weights = [1, 1]
        field = root.state.field
        score = weights[0] * score_heuristic(field) + weights[1] * height_heuristic(field)
        return float(score) / sum(weights)

    def searchMCBranch(self, root):
        root.visits += 1

        if not root.children:
            utility = self.evaluate(root)
            if utility > 0.5:
                root.reward += 1
            return utility

        child = self.pickBestChild(root)

        utility = self.searchMCBranch(child)
        if utility > 0.5:
            root.reward += 1

    def searchMCTree(self, tree):
        for i in range(500):
            self.searchMCBranch(tree)

        return self.pickBestChild(tree)

    def choose(self):
        # Generate Monte Carlo Tree.
        tree = self.generateMCTree()

        # Pick a goal.
        goal = self.searchMCTree(tree).state

        # Find actions to goal.
        # TODO

        # let's just output the goal we want:
        print goal

        # Fallback to random strategy.
        ind = [randint(0, 4) for _ in range(1, 10)]
        moves = map(lambda x: self._actions[x], ind)
        moves.append('drop')

        return moves

