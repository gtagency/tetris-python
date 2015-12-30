from random import randint, choice
from AbstractStrategy import AbstractStrategy
from math import log
import math
from operator import add
import copy
import sys
import datetime
from Bot.Game import Piece
from Bot.Game.Field import Field


class Node(object):

    def __init__(self, state, parent, rot_and_pos=None, this_piece=None, next_piece=None):
        self.state = state
        self.rot_and_pos = rot_and_pos
        self.children = []  # A list of Nodes
        self.parent = parent
        self.visits = 1
        self.reward = 0
        self.next_piece = next_piece
        self.this_piece = this_piece

        if this_piece is not None:
            pieces = [this_piece]
        else:
            pieces = [Piece.create(pType) for pType in ['L', 'O', 'I', 'J', 'S', 'T', 'Z']]

        self.possibleChildren = []  # A list of tuples of rotations and pos's.
        for piece in pieces:
            self.possibleChildren.extend([(rotation, position)
                                          for rotation in piece._rotations
                                          for position in range(-3, len(self.state.field[0]) - 1)])

    def hasNextChild(self):
        return len(self.possibleChildren) != 0

    def getNextChild(self):
        """Returns a child Node with a randomly picked piece, rotation and position."""
        rotation, pos = choice(self.possibleChildren)
        self.possibleChildren.remove((rotation, pos))

        while not self.state.isDropPositionValid(rotation, (pos, 0)):
            if self.hasNextChild():
                return self.getNextChild()
            else:
                return None

        return self.getChild(rotation, pos)

    def getChild(self, rotation, pos):
        """Returns a child Node with the rotation dropped from pos."""
        new_field = self.state.projectRotationDown(rotation, (pos, 0))
        new_state = Field()
        new_state.field = new_field
        child = Node(new_state, self, rot_and_pos=(rotation, pos), this_piece=self.next_piece)
        self.children.append(child)
        return child


class PhantomNode(object):

    def __init__(self):
        self.visits = 1
        self.reward = 0


class MonteCarloStrategy(AbstractStrategy):
    def __init__(self, game):
        AbstractStrategy.__init__(self, game)
        self._actions = ['left', 'right', 'turnleft', 'turnright', 'down', 'drop']
        # self.C = 2 ** (0.5)
        self.C = 1.0
        self.score = lambda x, totalVisits: (
                (float(x.reward) / x.visits) +
                self.C * (log(totalVisits) / float(x.visits))**(0.5))

    def has_full_line(self, field):
        for row in field:
            if all(row):
                return True
        return False

    def get_std_dev(self, a_list):
        mean = self.get_mean(a_list)
        deviations = map(lambda x: (x - mean)**2, a_list)
        return (self.get_mean(deviations)) ** 0.5

    def get_mean(self, a_list):
        return reduce(lambda x, y: x + y, a_list) / float(len(a_list))

    def get_column_distribution(self, field):
        num_block_in_col = [0] * len(field)
        for col in range(len(field)):
            for row in range(len(field[col])):
                if field[col][row] > 1:
                    num_block_in_col[col] += 1
        return self.get_std_dev(num_block_in_col)

    def get_col_heights(self, field):
        col_height = [0] * len(field)
        for col in range(len(field)):
            for row in range(len(field[col])):
                if col_height[col] == 0 and field[col][row] > 1:
                    col_height[col] = len(field) - col
        return col_height

    def get_col_height_std_dev(self, field, treeHeightsMean):
        col_height = self.get_col_heights(field)
        deviations = map(lambda x: (x - treeHeightsMean)**2, col_height)
        return (self.get_mean(deviations)) ** 0.5

    def newHolesRBad(self, field):
        #only counts holes under the newly placed block
        height = len(field)
        width = len(field[0])
        holes = 0
        for i in range(width):
            empty = True
            for j in range(height):
                k = field[j][i]
                if k == 4:
                    if empty:
                        empty = False
                elif k == 0:
                    if not empty:
                        holes += 1
                else:
                    empty = True
        return math.e ** (-1 * holes)

    def get_height(self, field):
        for i, row in enumerate(field):
            if any([x > 1 for x in row]):
                return (len(field) - i)
        return 0

    def get_line_fillness(self, field, height=None):
        if height is None:
            height = self.get_height(field)

        if height == 0:
            return 0

        num_blocks = 0
        for row in field:
            num_blocks += len(filter(lambda x: x > 1, row))

        return num_blocks / (10.0 * height)

    def generateMCTree(self):
        currentState = self._game.me.field
        root = Node(currentState, None,
                this_piece=self._game.piece,
                next_piece=self._game.nextPiece)
        return root

    def pickBestChild(self, root):
        totalVisits = root.visits

        if len(root.children) > 0:
            score, best = max([(self.score(child, totalVisits), child) for child in root.children])
        else:
            score = float('-inf')

        if root.hasNextChild() and score <= self.score(PhantomNode(), totalVisits):
            best = root.getNextChild()
            if best is None:
                return self.pickBestChild(root)

        return best

    def evaluate(self, root, treeHeight, treeHeightsMean):
        """Returns utility of a state.

        +1 if a full line is formed
        -1 if height goes over maxHeight
        0 if not a sink"""
        field = root.state.field
        if root.parent == None:
            return 0

        if self.has_full_line(field):
            return +1

        field_height = self.get_height(field)
        holes = self.newHolesRBad(field)

        if self.get_line_fillness(field, field_height) >= 0.8 and holes >= 0.9:
            # print field
            # print self.get_line_fillness(field, field_height)
            return +1

        if holes == 1 and field_height != 0 and (field_height <= treeHeight+1 or field_height <= 4):
            #print field
            return +1

        if self.get_col_height_std_dev(field, treeHeightsMean) > 2.4:
            return -1

        if treeHeight <= 4:
            if field_height > 4 and not isinstance(root.this_piece, Piece.IPiece):
                return -1
        else:
            if field_height > treeHeight + 1 and not isinstance(root.this_piece, Piece.IPiece):
                return -1

        return 0

    def searchMCBranch(self, root, treeHeight, treeHeightsMean):
        root.visits += 1

        utility = self.evaluate(root, treeHeight, treeHeightsMean)
        if utility != 0:
            if utility == 1:
                root.reward += 1
            return utility

        child = self.pickBestChild(root)

        if child is None:
            utility = -1
        else:
            utility = self.searchMCBranch(child, treeHeight, treeHeightsMean)

        if utility == 1:
            root.reward += 1
        return utility

    def pick_highest_reward(self, root):
        _, best = max((x.reward, x) for x in root.children)
        return best

    def searchMCTree(self, tree, timeLimit):
        timeLimit = datetime.timedelta(milliseconds=int(timeLimit))
        begin = datetime.datetime.utcnow()

        treeHeight = self.get_height(tree.state.field)
        treeHeightsMean = self.get_mean(self.get_col_heights(tree.state.field))

        while datetime.datetime.utcnow() - begin < timeLimit:
            self.searchMCBranch(tree, treeHeight, treeHeightsMean)
            # print str(datetime.datetime.utcnow() - begin)
            # print [(x.visits, x.reward) for x in tree.children]

        # return self.pickBestChild(tree)
        return self.pick_highest_reward(tree)

    def choose(self):
        # Generate Monte Carlo Tree.
        tree = self.generateMCTree()

        # Pick a goal.
        goal = self.searchMCTree(tree, self._game.timePerMove)

        # print str(goal.state.field)
        sys.stderr.write(str([(x.visits, x.reward) for x in tree.children]) + '\n')
        sys.stderr.write('holes ' + str(self.newHolesRBad(goal.state.field)) + '\n')
        treeHeightsMean = self.get_mean(self.get_col_heights(tree.state.field))
        sys.stderr.write('colhstddev' + str(self.get_col_height_std_dev(goal.state.field, treeHeightsMean)) + '\n')

        # Find actions to goal.
        return self.get_actions_to_goal(goal)

    def get_actions_to_goal(self, goal):
        rotation, position = goal.rot_and_pos
        actions = []

        while rotation != self._game.piece.positions():
            actions.append('turnright')
            self._game.piece.turnRight()

        currentPos = list(self._game.piecePosition)
        while currentPos[0] != position:
            if currentPos[0] > position:
                actions.append('left')
                currentPos[0] -= 1
            else:
                actions.append('right')
                currentPos[0] += 1

        actions.append('drop')

        return actions
