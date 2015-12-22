from random import randint, choice
from AbstractStrategy import AbstractStrategy
from math import log
from operator import add
import copy
import sys


class Node(object):

    def __init__(self, state, parent, rot_and_pos=None, _piece=None, next_piece=None):
        self.state = state
        self.rot_and_pos = rot_and_pos
        self.children = []  # A list of Nodes
        self.parent = parent
        self.visits = 1
        self.reward = 0

        self.this_piece = this_piece
        self.next_piece = next_piece

        # TODO: initialize with tuples of piece rotations and positions.
        # If this_piece is specified, use only those rotations, else, use all pieces.
        self.possibleChildren = []  # A list of tuples of rotations and positions.

    def getNextChild(self):
        """Returns a child Node with a randomly picked piece, rotation and position."""
        pass

    def getChild(self, rotation, pos):
        """Returns a child Node with the rotation dropped from pos."""
        # Node(new_state, self, rot_and_pos=(rotation, pos), this_piece=self.next_piece)
        pass


class MonteCarloStrategy(AbstractStrategy):
    def __init__(self, game):
        AbstractStrategy.__init__(self, game)
        self._actions = ['left', 'right', 'turnleft', 'turnright', 'down', 'drop']
        self.score = lambda x: (
                (float(x.reward) / x.visits) +
                C * (log(currentVisits) / float(x.visits))**(0.5))

    def has_full_line(self, field):
        for row in field:
            if all(row):
                return True
        return False

    def get_height(self, field):
        for i, row in enumerate(field):
            if any([x > 1 for x in row]):
                return 1 - (len(new_field) - i)
        return 0

    # def dfs(self, node, depth):
        # if depth == 0:
            # # Return this utility
            # return [self.evaluate(node)]

        # childUtilities = []
        # for childField in node.state.getAllChildren():
            # child = Node(childField, node)
            # if not child in node.children and depth > 0:
                # node.children.append(child)
                # childUtilities.extend(self.dfs(child, depth - 1))
        # return childUtilities

    def generateMCTree(self):
        currentState = self._game.me.field
        root = Node(currentState, None)

        stateChildren = root.state.getChildren(self._game.piece)

        for i in xrange(len(stateChildren)):
            child = Node(stateChildren[i], root)
            childStateChildren = child.state.getChildren(self._game.nextPiece)

            for j in xrange(len(childStateChildren)):
                childsChild = Node(childStateChildren[j], child)
                child.children.append(childsChild)

            root.children.append(child)

        return root

    def pickBestChild(self, root, final=False, isTreeRoot=False):
        C = 2**(0.5)
        currentVisits = root.visits
        childList = root.children

        if currentVisits == 0:
            return choice(childList)
        else:
            # exploration / exploitation
            if isTreeRoot and False:
                sys.stderr.write(str([(score(child), child.visits) for child in childList]) + '\n')
            sc, best = max([(score(child), child) for child in childList])
            if final and False:
                sys.stderr.write(str(best.state.field) + '\n')
                sys.stderr.write(str(sc) + '\n')
                sys.stderr.write(str(self.evaluate(best)) + '\n')
            return best

    def evaluate(self, root, debug=False):
        """Returns utility of a state.

        +1 if a full line is formed
        -1 if height goes over maxHeight
        0 if not a sink"""
        field = root.state.field

        if get_height(field) > 14:
            return -1
        elif has_full_line(field):
            return +1
        else:
            return 0

    def searchMCBranch(self, root, avgUtil=0.5, isTreeRoot=False):
        root.visits += 1

        if len(root.children) == 0:
            utility = self.evaluate(root)
            if utility > avgUtil:
                root.reward += 1
            return utility

        child = self.pickBestChild(root, isTreeRoot=isTreeRoot)

        utility = self.searchMCBranch(child, avgUtil)
        if utility > avgUtil:
            root.reward += 1
        return utility

    def searchMCTree(self, tree, avgUtil):
        for i in range(2000):
            self.searchMCBranch(tree, avgUtil, isTreeRoot=True)

        return self.pickBestChild(tree, final=True)

    def choose(self):
        # Generate Monte Carlo Tree.
        tree, avgUtil = self.generateMCTree()

        # Pick a goal.
        # goal = self.searchMCTree(tree, avgUtil).state
        goal = self.searchMCTree(tree, avgUtil)
        # TODO: this avgutil is not working because it is setting the AVERAGE case to be desirable.
        # this means that MC will explore every branch uniformly because the average case is spread uniformly throughout the tree.
        # This might be fixed if we add new heuristics like holes are bad, lines are good, etc.

        ### --- ###
        # currentVisits = tree.visits
        # C = 2 ** (0.5)
        # score = lambda x: ((float(x.reward) / x.visits) + C * (log(float(currentVisits)) / float(x.visits))**(0.5))

        # i = 0
        # for child in tree.children[0].children[0].children:
        # for child in tree.children:
            # if i > 15:
                # break
            # sys.stderr.write(str(child.state.field) + '\n')
            # sys.stderr.write(str(self.evaluate(child)) + '\n')
            # sys.stderr.write('visits: ' + str(child.visits) + '\n')
            # sys.stderr.write('reward: ' + str(child.reward) + '\n')
            # sys.stderr.write('chance:' + str(score(child)) + '\n')
            # i += 1

        sys.stderr.write('avgUtil: ' + str(avgUtil) + '\n')
        sys.stderr.write('root visits: ' + str(tree.visits) + '\n')
        sys.stderr.write('root reward: ' + str(tree.reward) + '\n')

        childVisits = [(child.visits, child.reward) for child in tree.children]
        sys.stderr.write('childVisitsAndRewards: \n' + str(childVisits) + '\n')

        childVisits = [(child.visits, child.reward) for child in tree.children[0].children]
        sys.stderr.write('childVisitsAndRewards2: \n' + str(childVisits) + '\n')

        sys.stderr.write('goal: \n' + str(goal.state.field))
        sys.stderr.write('goal util: ' + str(self.evaluate(goal)))
        ### --- ###

        goal = goal.state

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
