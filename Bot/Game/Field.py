import numpy as np
import copy

class Field:
    def __init__(self):
        self.width = 10
        self.height = 20
        self.field = np.array([[0]*self.width]*self.height) #np.array([[0]*self.width, [0]*self.height], np.int32)

    def size(self):
        return self.width, self.height

    def updateField(self, field):
        self.field = np.array(field)

    def projectPieceDown(self, piece, offset):
        piecePositions = self._offsetPiece(piece.positions(), offset)

        field_s = None
        for height in range(0, self.height-1):
            tmp = self.fitPiece(piecePositions, [0, height])

            if not tmp:
                break
            field_s = tmp

        return field_s

    @staticmethod
    def _offsetPiece(piecePositions, offset):
        piece = copy.deepcopy(piecePositions)
        for pos in piece:
            pos[0] += offset[0]
            pos[1] += offset[1]

        return piece

    def _checkIfPieceFits(self, piecePositions):
        for x,y in piecePositions:
            if 0 <= x < self.width and 0 <= y < self.height:
                if self.field[y][x] > 1:
                    return False
            else:
                return False
        return True

    def fitPiece(self, piecePositions, offset=None):
        if offset:
            piece = self._offsetPiece(piecePositions, offset)
        else:
            piece = piecePositions

        field = copy.deepcopy(self.field)
        if self._checkIfPieceFits(piece):
            for x,y in piece:
                field[y][x] = 4

            return field
        else:
            return None

    def isDropPositionValid(self, rotation, position ):
        def pieceValid(piece, position):
            for rowIdx, row in enumerate(rotation):
                for colIdx, val in enumerate(row):
                    if val != 0:
                        yIdx = rowIdx + position[0]
                        xIdx = colIdx + position[1]
                        if not 0 <= yIdx < self.height or not 0 <= xIdx < self.width:
                            return False
                        if self.field[yIdx, xIdx] != 0:
                            return False
            return True

        # piecevalid = lambda piece, position: all(0<=coords[0]+position[0]<self.width and 0<=coords[1]+position[1]<self.height and self.field[(coords[0]+position[0], coords[1]+position[1])] == 0 for coords in rotation)
        # droppositionvalid = lambda piece, position: any( coords[1]+position[1]>self.height or self.field((coords[0]+position[0], coords[1]+position[1]+1)) != 0 for coords in rotation)

        return pieceValid(rotation, position) #and dropPosValid(rotation, position)

    def getChildren(self, piece):
        """Given a 5x5 piece matrix, return all possible goal states.

        A goal state is any position in which the piece is on top of another."""

        offset = len(piece.positions())- 1

        children = []

        for i in reversed(range(- offset, self.height + offset)):
            for j in range(- offset, self.width + offset):
                pos = (i, j)
                for rotation in piece._rotations:
                    if self.isDropPositionValid(rotation, pos):
                        children.append((rotation, pos))

        childrenFields = []
        for rotation, pos in children:
            childField = Field()
            piecePositions = []
            for tempY, row in enumerate(rotation):
                for tempX, val in enumerate(row):
                    if val != 0:
                        piecePositions.append((tempX + pos[0], tempY + pos[1]))
            childField.field = self.fitPiece(piecePositions)
            if childField.field != None:
                childrenFields.append(childField)

        return childrenFields

    def getAllChildren(self):
        findSpaces = lambda (x,y): [(p,q) for (p,q) in {(x-1,y),(x+1,y),(x,y-1),(x,y+1)} if (0<=p<self.width and 0<=q<self.height and self.field[q][p] == 0)]

        def findPieces(loc):
            domino = {(loc,y) for y in findSpaces(loc)}
            tromino = set()
            for x,y in domino:
                tromino.union({(x,y,z) for z in findSpaces(y)})
            tetromino = set()
            for x,y,z in tromino:
                tetromino.union({(x,y,z,w) for w in findSpaces(z)})
            return {set(x) for x in tetromino}

        children = set()
        for index, value in np.ndenumerate(self.field):
            x, y = index
            if value == 0 and (y == 0 or self.field[x,y-1] != 0):
                children.union(findPieces((x,y)))

        # Children is a bunch of sets, each of those with four coordinates that
        # need to be set to 1. And everything needs to be wrapped in a Field.
        childrenFields = []
        for child in children:
            childField = Field()
            childField.field = self.field
            for x, y in child:
                childField.field[y][x] = 1
            childrenFields.append(childField)

        return children
