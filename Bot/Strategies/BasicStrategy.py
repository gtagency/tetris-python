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
        if any([x > 1 for x in row]):
            return 1 - (float(len(new_field) - i) / len(new_field))


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

    def dfs(self, node, depth):
        if depth == 0:
            # Return this utility
            return [self.evaluate(node)]

        childUtilities = []
        for childField in node.state.getAllChildren():
            child = Node(childField, node)
            if not child in node.children and depth  > 0:
                node.children.append(child)
                childUtilities.extend(self.dfs(child, depth - 1))
        return childUtilities

    def generateMCTree(self):
        currentState = self._game.me.field
        root = Node(currentState, None)

        stateChildren = root.state.getChildren(self._game.piece)
        leafUtilities = []
        for i in xrange(len(stateChildren)):
            # print 'hang tight'
            child = Node(stateChildren[i], root)
            leafUtilities.extend(self.dfs(child, 1))
            root.children.append(child)

        # print leafUtilities
        # generate average utility of leaf nodes
        avgLeafUtil = float(sum(leafUtilities)) / len(leafUtilities)
        # print avgLeafUtil

        return root, avgLeafUtil

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

    def evaluate(self, root, debug=False):
        weights = [1, 3]
        field = root.state.field
        if debug:
            print 'scoreH:', score_heuristic(field)
            print 'heightH:', height_heuristic(field)
        score = weights[0] * score_heuristic(field) + weights[1] * height_heuristic(field)
        return float(score) / sum(weights)

    def searchMCBranch(self, root, avgUtil=0.5):
        root.visits += 1

        if not root.children:
            utility = self.evaluate(root)
            if utility > avgUtil:
                root.reward += 1
            return utility

        child = self.pickBestChild(root)

        utility = self.searchMCBranch(child)
        if utility > avgUtil:
            root.reward += 1

    def searchMCTree(self, tree, avgUtil):
        for i in range(500):
            self.searchMCBranch(tree, avgUtil)

        return self.pickBestChild(tree)

    def choose(self):
        # Generate Monte Carlo Tree.
        tree, avgUtil = self.generateMCTree()

        # Pick a goal.
        goal = self.searchMCTree(tree, avgUtil).state

        # C = 2**(1/2)
        # currentVisits = tree.visits
        # print 'here is trees (', currentVisits, 'visits) field'
        # print tree.state.field
        # print 'and the children'
        # for i in range(7):
            # child = choice(tree.children)
            # score = lambda x: ((float(x.reward) / x.visits) + C * (2 * log(float(x.visits) / currentVisits))**(1/2))
            # print ''
            # print child.state.field
            # evalu = self.evaluate(child)
            # print 'score:', evalu
            # print 'prob:', score(child)

        # print goal.field

        # Find actions to goal.
        actions = self.reverseDFS(goal, self._game.piecePosition, self._game.piece);

        return actions

    def reverseDFS(self, goal, piecePos, piece):

        closed = set()
        currentField = self._game.me.field
        openList = [(piecePos, piece, [])]
        print piecePos

        while len(openList) != 0:
            piecePos, piece, intstructions = openList.pop()

            test = goal.field == currentField.fitPiece(piece.positions(), piecePos)
            if type(test) is not bool and test.all():
                #(type(test) is bool and test == True) or
                return intstructions

            #rotations
            copyPiece = copy.deepcopy(piece)
            if copyPiece.turnLeft() and currentField._checkIfPieceFits(currentField._offsetPiece(copyPiece.positions(), piecePos)):
                newState = (copy.deepcopy(piecePos), copy.deepcopy(copyPiece), copy.deepcopy(intstructions))
                newState[2].append("turnLeft")
                if (tuple(newState[0]), newState[1]._rotateIndex) not in closed:
                    openList.append(newState)
                    closed.add((tuple(newState[0]), newState[1]._rotateIndex))
            copyPiece = copy.deepcopy(piece)
            if copyPiece.turnRight() and currentField._checkIfPieceFits(currentField._offsetPiece(copyPiece.positions(), piecePos)):
                newState = (copy.deepcopy(piecePos), copy.deepcopy(copyPiece), copy.deepcopy(intstructions))
                newState[2].append("turnRight")
                if (tuple(newState[0]), newState[1]._rotateIndex) not in closed:
                    openList.append(newState)
                    closed.add((tuple(newState[0]), newState[1]._rotateIndex))


            #normal moves
            for move in [[1,0],[-1,0],[0,1]]:
                offset = currentField._offsetPiece(piece.positions(), map(add, piecePos, move))
                if currentField._checkIfPieceFits(offset):
                    newState = (map(add, piecePos, move), copy.deepcopy(piece), copy.deepcopy(intstructions))
                    newState[2].append("left" if move == [-1,0] else ("right" if move == [1,0] else "down"))
                    if (tuple(newState[0]), newState[1]._rotateIndex) not in closed:
                        openList.append(newState)
                        closed.add((tuple(newState[0]), newState[1]._rotateIndex))


        return None
