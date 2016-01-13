import datetime as dt

from sys import stderr
from math import log, exp
from operator import add
from random import randint, choice
from AbstractStrategy import AbstractStrategy
from Bot.Game import Piece
from Bot.Game.Field import Field
from collections import Counter
import copy
from Bot import util

class Node(object):

    def __init__(self, state, parent, rot_and_pos=None, this_piece=None, next_piece=None, instructions=None):
        self.state = state # Field
        self.rot_and_pos = rot_and_pos
        self.children = []  # A list of Nodes
        self.parent = parent
        self.visits = 1
        self.reward = 0
        self.util = [None] * 11
        self.stat = ''
        self.next_piece = next_piece
        self.this_piece = this_piece
        self.params = None
        self.possibleChildren = []
        self.instructions = instructions
        self.pieces = []

        if this_piece is not None:
            self.pieces = [this_piece]
        else:
            self.pieces = [Piece.create(pType) for pType in ['L', 'O', 'I', 'J', 'S', 'T', 'Z']]
        # print "Node start"
        # now = dt.datetime.utcnow()
        #self.initialChildren = []  # A list of tuples of rotations and pos's.
        for pieceNum in range(0,len(self.pieces)):
            for rotation in range(0,len(self.pieces[pieceNum]._rotations)):
                for position in range(-3, len(self.state.field[0])):
                    self.possibleChildren.append(((pieceNum,rotation), position, None))
            # self.initialChildren.extend([(copy.deepcopy(piece)rotation, position)
            #                               for rotation in len(piece._rotations)
            #                               for position in range(-3, len(self.state.field[0]) - 1)])
            # print self.initialChildren
        startValid = lambda (piece, position, complexChild): all(0<=coords[0]+position<10 for coords in self.pieces[piece[0]]._rotations[piece[1]])
        # print dt.datetime.utcnow() - now
        # now = dt.datetime.utcnow()
        self.possibleChildren = filter(startValid, self.possibleChildren)
        # print "filter"
        # print dt.datetime.utcnow() - now


    def calcParams(self):
        # print "param calc"
        # now = dt.datetime.utcnow()
        """One-pass param calculation.""" #actually it's now 2-pass :)
        field = self.state.field

        num_full_lines = 0
        height = 0
        col_heights = [0] * len(field[0])
        num_blocks = 0
        grow_hole = [False] * len(field[0])
        holes_per_col = [0] * len(field[0])
        filled_holes = 0
        filled_lines = [False] * len(field)
        for i in range(len(field)): #seperated so that grow_hole logic works correctly
            if all([0 if x==1 else x for x in field[i]]):
                filled_lines[i] = True

        for i in range(len(field)):
            num_blocks_line = 0
            num_unbreakable_blocks_line = 0

            for j in range(len(field[0])):
                block = field[i][j]

                if block > 1:
                    num_blocks_line += 1
                    if block == 3:
                        num_unbreakable_blocks_line += 1

                if block == 4:
                    if filled_lines[i] == False: #DO NOT CONDENSE INTO 1 IF STATEMENT!!! (breaks else logic)
                        grow_hole[j] = True
                    if col_heights[j] != 0:
                        filled_holes += 1
                elif block == 0 and grow_hole[j]:
                    holes_per_col[j] += 1
                else:
                    grow_hole[j] = False

                if col_heights[j] == 0 and block > 1:
                    col_heights[j] = len(field) - i

            if num_blocks_line == len(field[0]) and num_unbreakable_blocks_line != len(field[0]):
                num_full_lines += 1

            num_blocks += num_blocks_line

        height = max(col_heights)

        self.params = {
            'num_blocks': num_blocks,
            'num_full_lines': num_full_lines,
            'height': height,
            'col_heights': col_heights,
            'col_std_dev': self.get_std_dev(col_heights),
            'line_fillness': self.get_line_fillness(num_blocks, height),
            'holes': self.score_holes(holes_per_col),
            'filled_holes': filled_holes
        }
        # print dt.datetime.utcnow() - now

    def hasNextChild(self):
        return len(self.possibleChildren) != 0

    def getNextChild(self):
        if self.possibleChildren is None:
            return None
        """Returns a child Node with a randomly picked piece, rotation and position."""
        rotation, pos, complexChild = choice(self.possibleChildren)
        self.possibleChildren.remove((rotation, pos, complexChild))
        if type(pos) is int:
            #need to expand, aka find y val and check for complex children
            rotation,pos,complexChild = self.generateChildren(rotation, pos)

        while pos == None:
            if self.hasNextChild():
                return self.getNextChild()
            else:
                return None

        return self.getChild(self.pieces[rotation[0]]._rotations[rotation[1]], pos, complexChild)

    def generateChildren(self,piece,x):
        if self.params is None:
            self.calcParams()
        # print "genChildren"
        # now = dt.datetime.utcnow()
        newChildren = []
        piecePos = self.pieces[piece[0]]._rotations[piece[1]]
        complexChild = False
        position = (x, -2)

        newPosition = None
        while position[1] < self.state.height:
            position = (position[0], position[1]+1)

            offset = self.state._offsetPiece(piecePos, position)
            fitPiece = self.state.fitPiece(piecePos, position, softTop=True)
            if fitPiece != None:
                newPosition = position
                continue
            elif newPosition != None:
                if self.state._checkIfPieceFits(self.state._offsetPiece(piecePos, newPosition)) != False:
                    if complexChild == False:
                        # print "yes!!"
                        newChildren.append((piece,newPosition,None))
                        newPosition = None
                    else:
                        instructions = self.aStar(self.pieces[piece[0]], newPosition, piecePos)
                        # print instructions
                        if instructions != None:
                            # print "yes!!!"
                            newChildren.append((piece,newPosition,instructions))
            complexChild = True
        # print dt.datetime.utcnow() - now
        if len(newChildren) == 0:
            return None,None,None
        elif len(newChildren) == 1:
            return newChildren[0]
        else:
            ret = choice(newChildren)
            newChildren.remove(ret)
            for item in newChildren:
                self.possibleChildren.append(item)
            return ret

    def getChild(self, rotation, pos, complexInstructions):
        """Returns a child Node with the rotation dropped from pos."""

        new_field = self.state.fitPiece(rotation, pos)
        new_state = Field()
        new_state.field = new_field
        child = Node(new_state, self, rot_and_pos=(rotation, pos), this_piece=self.next_piece, instructions=complexInstructions)
        self.children.append(child)
        return child

    def calc_util(self, treeParams, relaxation):
        if self.params['num_full_lines'] > 1:
            self.stat = 'multi_full_line'
            return +1

        if relaxation <= 2 and self.params['holes'] != 1:
            self.stat = 'hole_found'
            return -1

        if relaxation > 2 and self.params['num_full_lines'] > 0:
            self.stat = 'full_line'
            return +1

        if self.params['filled_holes'] > 0 and self.params['holes'] == 1:
            self.stat = 'filled_holes'
            return +1

        if 2 < relaxation <= 6 and self.params['holes'] < 0.5: # this means 1 new holes necessary for True
            self.stat = 'holes<0.5'
            return -1

        if relaxation > 6 and self.params['holes'] < 0.3: # this means 2 new holes necessary for True
            self.stat = 'holes<0.3'
            return -1

        if relaxation > 5:
            if treeParams['height'] > 0 and self.params['col_std_dev'] > (1.4 *  (treeParams['col_std_dev'])):
                self.stat = 'colStdDev>1.4tree'
                return -1

            if self.params['line_fillness'] > (1.5 * treeParams['line_fillness']) and self.params['col_std_dev'] < treeParams['col_std_dev']:
                self.stat = 'goodfill_noholes'
                return +1

        if self.params['height'] > treeParams['height'] + 3:
            self.stat = 'height>tree+3'
            return -1

        self.stat = 'continue'

        return 0

    def evaluate(self, treeParams, relaxation=0):
        """Returns utility of a state.

        +1 if a full line is formed
        -1 if height goes over maxHeight
        0 if not a sink"""
        if self.params is None:
            self.calcParams()

        if self.util[relaxation] is None:
            self.util[relaxation] = self.calc_util(treeParams, relaxation)

        return self.util[relaxation]

    def get_std_dev(self, a_list):
        mean = self.get_mean(a_list)
        deviations = map(lambda x: (x - mean)**2, a_list)
        return (self.get_mean(deviations)) ** 0.5

    def get_mean(self, a_list):
        return reduce(lambda x, y: x + y, a_list) / float(len(a_list))

    def score_holes(self, holes_per_col):
        num_holes = sum(holes_per_col)
        return exp(-1 * num_holes)

    def get_line_fillness(self, num_blocks, height):
        if height == 0:
            return 0
        return num_blocks / (10.0 * height)

    def aStar(self, piece, position, piecePos):
        # used to see if complex block placement is valid. Instructions are kept
        # in reverse order to avoid having to call reverseDFS later
        GOAL_POS = (3,-1)
        currentField = self.state
        closed = set()
        openList = util.PriorityQueue()
        def getPriority(position, piece):
            dist = util.manhattanDistance(position, GOAL_POS)
            rotationDist = min(piece._rotateIndex, len(piece._rotations)-piece._rotateIndex)
            return dist + rotationDist
        openList.push((position, piece, []), getPriority(position, piece))

        while not openList.isEmpty():
            position, piece, intstructions = openList.pop()

            if position[0] == GOAL_POS[0] and position[1] == GOAL_POS[1] and piece._rotateIndex == 0:
                intstructions.reverse()
                return intstructions

            #rotations
            copyPiece = copy.deepcopy(piece)
            if copyPiece.turnLeft() and currentField._checkIfPieceFits(currentField._offsetPiece(copyPiece.positions(), position), softTop=True):
                newState = (copy.deepcopy(position), copy.deepcopy(copyPiece), copy.deepcopy(intstructions))
                newState[2].append("turnright")
                if (tuple(newState[0]), newState[1]._rotateIndex) not in closed:
                    openList.push(newState, getPriority(newState[0],newState[1]))
                    closed.add((tuple(newState[0]), newState[1]._rotateIndex))
            copyPiece = copy.deepcopy(piece)
            if copyPiece.turnRight() and currentField._checkIfPieceFits(currentField._offsetPiece(copyPiece.positions(), position), softTop=True):
                newState = (copy.deepcopy(position), copy.deepcopy(copyPiece), copy.deepcopy(intstructions))
                newState[2].append("turnleft")
                if (tuple(newState[0]), newState[1]._rotateIndex) not in closed:
                    openList.push(newState, getPriority(newState[0],newState[1]))
                    closed.add((tuple(newState[0]), newState[1]._rotateIndex))

            #normal moves
            for move in [[1,0],[-1,0],[0,-1]]:
                offset = currentField._offsetPiece(piece.positions(), map(add, position, move))
                if currentField._checkIfPieceFits(offset, softTop=True):
                    newState = (map(add, position, move), copy.deepcopy(piece), copy.deepcopy(intstructions))
                    newState[2].append("right" if move == [-1,0] else ("left" if move == [1,0] else "down"))
                    if (tuple(newState[0]), newState[1]._rotateIndex) not in closed:
                        openList.push(newState, getPriority(newState[0],newState[1]))
                        closed.add((tuple(newState[0]), newState[1]._rotateIndex))

        #print dt.datetime.utcnow() - begin
        return None


class PhantomNode(object):

    def __init__(self):
        self.visits = 1
        self.reward = 0


class MonteCarloStrategy(AbstractStrategy):
    def __init__(self, game):
        AbstractStrategy.__init__(self, game)
        self._actions = ['left', 'right', 'turnleft', 'turnright', 'down', 'drop']
        self.C = 2 ** (0.5)
        # self.C = 1.0
        self.score = lambda x, totalVisits: (
                (float(x.reward) / x.visits) +
                self.C * (log(totalVisits) / float(x.visits))**(0.5))

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

        # print len(root.children)
        # print score
        # print self.score(PhantomNode(), totalVisits)
        # print root.hasNextChild()
        # print score <= self.score(PhantomNode(), totalVisits)
        return best

    def searchMCBranch(self, root, treeParams, relaxation=0):
        root.visits += 1

        if root.util[relaxation] is None:
            root.util[relaxation] = root.evaluate(treeParams, relaxation)
        utility = root.util[relaxation]
        self.stats[root.stat] += 1

        if utility != 0:
            if utility == 1:
                root.reward += 1
            return utility

        child = self.pickBestChild(root)

        if child is None:
            utility = -1
        else:
            utility = self.searchMCBranch(child, treeParams, relaxation)

        if utility == 1:
            root.reward += 1
        return utility

    def pick_highest_reward(self, root):
        best_children = [child for child in root.children
                         if child.reward == max(x.reward for x in root.children)]
        # Break ties.
        best_children = [child for child in best_children
                         if child.params['line_fillness'] == max(x.params['line_fillness'] for x in best_children)]

        best_children = [child for child in best_children
                         if child.params['num_full_lines'] == max(x.params['num_full_lines'] for x in best_children)]

        best_children = [child for child in best_children
                         if child.params['holes'] == max(x.params['holes'] for x in best_children)]

        return choice(best_children)

    def searchMCTree(self, tree, timeLimit):
        oneTenth = dt.timedelta(milliseconds=(int(timeLimit) * 0.1))
        checkpoint = oneTenth

        timeLimit = dt.timedelta(milliseconds=int(timeLimit))
        if self._game.timebank < 1000 and timeLimit > 100: #prevents us from using up all of our time
            timeLimit = timeLimit - 25
        begin = dt.datetime.utcnow()

        relaxation = 0

        tree.calcParams()

        self.stats = Counter()

        while dt.datetime.utcnow() - begin < timeLimit:
            # now = dt.datetime.utcnow()
            if tree.reward == 0 and dt.datetime.utcnow() - begin > checkpoint:
                relaxation += 1
                stderr.write('relaxation level: ' + str(relaxation) + '\n')
                checkpoint = oneTenth * (relaxation + 1)

            self.searchMCBranch(tree, tree.params, relaxation)
            # print "search tree"
            # print dt.datetime.utcnow() - now

        # return self.pickBestChild(tree)
        #print tree.children
        return self.pick_highest_reward(tree)

    def choose(self):
        # Generate Monte Carlo Tree.
        tree = self.generateMCTree()

        # Pick a goal.
        goal = self.searchMCTree(tree, self._game.timePerMove)

        # Print statistics.
        self.print_stats(tree, goal)

        # Find actions to goal.
        if goal.instructions != None:
            return goal.instructions
        if goal.params["height"] >= len(goal.state.field) - 4: #if col heights too high, get_actions_to_goal is unreliable
            actions = self.reverseDFS(goal)
            while actions == None:
                tree.children.remove(goal)
                goal = self.pick_highest_reward(tree)
                actions = self.reverseDFS(goal)
            return actions
        else:
            return self.get_actions_to_goal(goal)

    def print_stats(self, tree, goal):
         # print str(goal.state.field)
        stderr.write(str(tree.visits) + 'vs ' + str(tree.reward) + 'rd' '\n')
        stderr.write(str([(x.visits, x.reward) for x in tree.children]) + '\n')

        for param in goal.params:
            stderr.write(param + ' ' + str(goal.params[param]) + '\n')

        stderr.write('STATS: ' + str(self.stats) + '\n')

    def get_actions_to_goal(self, goal):
        rotation, position = goal.rot_and_pos
        actions = []
        #begin = dt.datetime.utcnow()

        while rotation != self._game.piece.positions():
            actions.append('turnright')
            self._game.piece.turnRight()

        while rotation != self._game.piece.positions():
            actions.append('turnright')
            self._game.piece.turnRight()

        currentPos = list(self._game.piecePosition)
        while currentPos[0] != position[0]:
            if currentPos[0] > position[0]:
                actions.append('left')
                currentPos[0] -= 1
            else:
                actions.append('right')
                currentPos[0] += 1

        actions.append('drop')
        #print dt.datetime.utcnow() - begin
        return actions

    def reverseDFS(self, goal):
        #begin = dt.datetime.utcnow()
        piece = self._game.piece
        piecePos = self._game.piecePosition
        closed = set()
        currentField = self._game.me.field

        openList = [(piecePos, piece, [])]
        # print goal.field


        while len(openList) != 0:
            piecePos, piece, intstructions = openList.pop()

            test = goal.state.field == currentField.fitPiece(piece.positions(), piecePos)
            if type(test) is not bool and test.all():
                #(type(test) is bool and test == True) or
                # print currentField.fitPiece(piece.positions(), piecePos)
                # print piecePos
                # print piece.positions()
                # print piece._rotateIndex
                #print dt.datetime.utcnow() - begin
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

        #print dt.datetime.utcnow() - begin
        return None
