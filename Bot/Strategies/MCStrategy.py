from random import randint, choice
from AbstractStrategy import AbstractStrategy
from math import log
from operator import add
import copy
import sys
from Bot.Game import Piece


class Node(object):

    def __init__(self, state, parent, rot_and_pos=None, this_piece=None, next_piece=None):
        self.state = state
        self.rot_and_pos = rot_and_pos
        self.children = []  # A list of Nodes
        self.parent = parent
        self.visits = 1
        self.reward = 0
        self.next_piece = next_piece

        pieces = [this_piece] or [Piece.create(pType)
                for pType in ['L', 'O', 'I', 'J', 'S', 'T', 'Z']]
        self.possibleChildren = []  # A list of tuples of rotations and pos's.
        for piece in pieces:
            self.possibleChildren.extend([(rotation, position)
                                          for rotation in piece._rotations
                                          for position in range(len(self.state[0])]))

    def getNextChild(self):
        """Returns a child Node with a randomly picked piece, rotation and position."""
        rotation, pos = choice(self.possibleChildren)
        self.possibleChildren.remove((rotation, pos))
        while not self.state.isDropPositionValid(rotation, pos):
            rotation, pos = choice(self.possibleChildren)
            self.possibleChildren.remove((rotation, pos))

        return self.getChild(rotation, pos)

    def getChild(self, rotation, pos):
        """Returns a child Node with the rotation dropped from pos."""
        new_state = self.state.projectRotationDown(rotation, pos)
        child = Node(new_state, self, rot_and_pos=(rotation, pos), this_piece=self.next_piece)
        self.children.append(child)
        return child


class MonteCarloStrategy(AbstractStrategy):
    def __init__(self, game):
        AbstractStrategy.__init__(self, game)
        self._actions = ['left', 'right', 'turnleft', 'turnright', 'down', 'drop']
        self.C = 2 ** (0.5)
        self.score = lambda x, totalVisits: (
                (float(x.reward) / x.visits) +
                self.C * (log(totalVisits) / float(x.visits))**(0.5))

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

    def generateMCTree(self):
        currentState = self._game.me.field
        root = Node(currentState, None,
                this_piece=self._game.piece,
                next_piece=self._game.nextPiece)
        return root

    def pickBestChild(self, root):
        C = 2**(0.5)
        totalVisits = root.visits

        _, best = max([(self.score(child, totalVisits), child) for child in root.children] +
                      [(self.score({ visits: 1, reward: 0 }, totalVisits), 'phantom')])
        if best === 'phantom':
            best = root.getNextChild()
        return best

    def evaluate(self, root):
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

    def searchMCBranch(self, root):
        root.visits += 1

        utility = self.evaluate(root)
        if utility != 0:
            if utility == 1:
                root.reward += 1
            return utility

        child = self.pickBestChild(root)

        utility = self.searchMCBranch(child)
        if utility == 1:
            root.reward += 1
        return utility

    def searchMCTree(self, tree, timeLimit):
        for i in range(2000):
            self.searchMCBranch(tree)

        return self.pickBestChild(tree)

    def choose(self):
        # Generate Monte Carlo Tree.
        tree = self.generateMCTree()

        # Pick a goal.
        goal = self.searchMCTree(tree, self._game.timebank)

        # Find actions to goal.
        return self.get_actions_to_goal(goal)

    def get_actions_to_goal(self, goal):
        rotation, position = goal.rot_and_pos
        actions = []

        while rotation != self._game.piece.positions():
            actions.append('turnright')
            self._game.piece.turnRight()

        currentPos = self._game.piecePosition
        while currentPos[1] != position[1]:
            if currentPos[1] > position[1]:
                actions.append('left')
                curentPos[1] -= 1
            else:
                actions.append('right')
                currentPos[1] += 1

        actions.append('drop')

        return actions

