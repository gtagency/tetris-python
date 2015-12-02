from random import randint, choice
from AbstractStrategy import AbstractStrategy
from math import log
from operator import add
import copy

def score_heuristic(new_field):
    score = 0
    for row in new_field:
        if all(row):
            score += 1
    return float(score) / len(new_field)

def height_heuristic(new_field):
    for i, row in enumerate(new_field):
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
        self.visits = 1
        self.reward = 0

class MonteCarloStrategy(AbstractStrategy):
    def __init__(self, game):
        AbstractStrategy.__init__(self, game)
        self._actions = ['left', 'right', 'turnleft', 'turnright', 'down', 'drop']
        # self.isFirstPiece = True

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
        childList = root.children
        if currentVisits == 0:
            return choice(childList)
        else:
            # exploration / exploitation
            score = lambda x: ((float(x.reward) / x.visits) + C * (2 * log(float(x.visits) / currentVisits))**(1/2))
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
        print goal.field

        # Find actions to goal.
        # TODO
        actions = self.reverseDFS(goal, self._game.piecePosition, self._game.piece);
        print actions
        # let's just output the goal we want:

        # Fallback to random strategy.
        ind = [randint(0, 4) for _ in range(1, 10)]
        moves = map(lambda x: self._actions[x], ind)
        moves.append('drop')

        return moves

    def reverseDFS(self, goal, piecePos, piece, closed=[]):
        # this recurses - so I guess it's a reverse recurse DFS :D
        #currentState is a Game obj, goal is a field
        currentField = self._game.me.field
        piecePos = self._game.piecePosition #tuple
        piece = self._game.piece
        children = []
        #normal moves
        for move in [[1,0],[0,1],[0,-1]]:
            offset = currentField._offsetPiece(piece.positions(), map(add, piecePos, move))
            if currentField._checkIfPieceFits(offset):
                newState = (map(add, piecePos, move), copy.deepcopy(piece), "left" if move == [0,-1] else ("right" if move == [0,1] else "down"))
                if newState not in closed:
                    children.append(newState)
                    closed.append(newState)
        #rotations
        copyPiece = copy.deepcopy(piece)
        if copyPiece.turnLeft() and currentField._checkIfPieceFits(currentField._offsetPiece(copyPiece.positions(), piecePos)):
            newState = (copy.deepcopy(piecePos), copy.deepcopy(copyPiece), "turnLeft")
            if newState not in closed:
                children.append(newState)
                closed.append(newState)
        copyPiece = copy.deepcopy(piece)
        if copyPiece.turnRight() and currentField._checkIfPieceFits(currentField._offsetPiece(copyPiece.positions(), piecePos)):
            newState = (copy.deepcopy(piecePos), copy.deepcopy(copyPiece), "turnRight")
            if newState not in closed:
                children.append(newState)
                closed.append(newState)

        #recursion time!
        for child in children:
            if (goal.field == currentField.fitPiece(child[1].positions(), child[0])).all()
            :
                return [child[2]]
            else:
                rec = self.reverseDFS(goal, child[0], child[1], closed)
                if rec != None:
                    return rec.append(child[2])

        return None
