from random import randint, choice
from AbstractStrategy import AbstractStrategy
from math import log
from operator import add
import copy
import sys

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
            child = Node(stateChildren[i], root)
            childStateChildren = child.state.getChildren(self._game.nextPiece)
            for j in xrange(len(childStateChildren)):
                childsChild = Node(childStateChildren[j], child)
                leafUtilities.extend(self.dfs(childsChild, 1))
                child.children.append(childsChild)
            root.children.append(child)

        # generate average utility of leaf nodes
        avgLeafUtil = float(sum(leafUtilities)) / len(leafUtilities) + 0.04

        # sys.stderr.write('avgLeafUtil' + str(avgLeafUtil) + '\n')

        return root, avgLeafUtil

    def pickBestChild(self, root, final=False, isTreeRoot=False):
        C = 2**(0.5)
        currentVisits = root.visits
        childList = root.children

        if currentVisits == 0:
            return choice(childList)
        else:
            # exploration / exploitation
            score = lambda x: ((float(x.reward) / x.visits) + C * (log(float(currentVisits)) / float(x.visits))**(0.5))
            if isTreeRoot and False:
                sys.stderr.write(str([(score(child), child.visits) for child in childList]) + '\n')
            sc, best = max([(score(child), child) for child in childList])
            if final and False:
                sys.stderr.write(str(best.state.field) + '\n')
                sys.stderr.write(str(sc) + '\n')
                sys.stderr.write(str(self.evaluate(best)) + '\n')
            return best

    def evaluate(self, root, debug=False):
        weights = [0, 1]
        field = root.state.field
        if debug:
            print 'scoreH:', score_heuristic(field)
            print 'heightH:', height_heuristic(field)
        score = weights[0] * score_heuristic(field) + weights[1] * height_heuristic(field)
        return float(score) / sum(weights)

    def searchMCBranch(self, root, avgUtil=0.5, isTreeRoot=False):
        root.visits += 1

        if len(root.children) == 0:
            utility = self.evaluate(root)
            if utility > avgUtil:
                root.reward += 1
            return utility

        child = self.pickBestChild(root, isTreeRoot=isTreeRoot)

        utility = self.searchMCBranch(child)
        if utility > avgUtil:
            root.reward += 1

    def searchMCTree(self, tree, avgUtil):
        for i in range(500):
            self.searchMCBranch(tree, avgUtil, isTreeRoot=True)

        return self.pickBestChild(tree, final=True)

    def choose(self):
        sys.stderr.write('making a decision')
        # Generate Monte Carlo Tree.
        tree, avgUtil = self.generateMCTree()

        # Pick a goal.
        goal = self.searchMCTree(tree, avgUtil).state

        # sys.stderr.write('root visits: ' + str(tree.visits) + '\n')
        # sys.stderr.write('root reward: ' + str(tree.reward) + '\n')
        # childVisits = [(child.visits, child.reward) for child in tree.children]
        # sys.stderr.write('childVisitsAndRewards: \n' + str(childVisits) + '\n')

        # i = 0
        # for child in tree.children[0].children[0].children:
            # if i > 15:
                # break
            # sys.stderr.write(str(child.state.field) + '\n')
            # sys.stderr.write(str(self.evaluate(child)) + '\n')
            # sys.stderr.write('visits: ' + str(child.visits) + '\n')
            # sys.stderr.write('reward: ' + str(child.reward) + '\n')
            # i += 1

        # Find actions to goal.
        actions = self.reverseDFS(goal, self._game.piecePosition, self._game.piece)
        actions.append('drop')

        return actions

    def reverseDFS(self, goal, piecePos, piece):

        closed = set()
        currentField = self._game.me.field
        openList = [(piecePos, piece, [])]
        # print goal.field


        while len(openList) != 0:
            piecePos, piece, intstructions = openList.pop()

            test = goal.field == currentField.fitPiece(piece.positions(), piecePos)
            if type(test) is not bool and test.all():
                #(type(test) is bool and test == True) or
                # print currentField.fitPiece(piece.positions(), piecePos)
                # print piecePos
                # print piece.positions()
                # print piece._rotateIndex
                return intstructions

            #rotations
            copyPiece = copy.deepcopy(piece)
            if copyPiece.turnLeft() and currentField._checkIfPieceFits(currentField._offsetPiece(copyPiece.positions(), piecePos)):
                newState = (copy.deepcopy(piecePos), copy.deepcopy(copyPiece), copy.deepcopy(intstructions))
                newState[2].append("turnleft")
                if (tuple(newState[0]), newState[1]._rotateIndex) not in closed:
                    openList.append(newState)
                    closed.add((tuple(newState[0]), newState[1]._rotateIndex))
            copyPiece = copy.deepcopy(piece)
            if copyPiece.turnRight() and currentField._checkIfPieceFits(currentField._offsetPiece(copyPiece.positions(), piecePos)):
                newState = (copy.deepcopy(piecePos), copy.deepcopy(copyPiece), copy.deepcopy(intstructions))
                newState[2].append("turnright")
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
