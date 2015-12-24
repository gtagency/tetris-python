import numpy as np
import copy

class Field:
    def __init__(self):
        self.width = 10
        self.height = 20
        self.field = np.array([[0]*self.width]*self.height)

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

    def projectRotationDown(self, piecePositions, offset):
        piecePositions = self._offsetPiece(piecePositions, offset)

        field_s = None
        for height in range(0, self.height-1):
            tmp = self.fitPiece(piecePositions, [0, height])

            if tmp is None or len(tmp) == 0:
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
        for x, y in piecePositions:
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

    def isDropPositionValid(self, rotation, position):
        pieceValid = lambda piece, position: all(coords[1]+position[1]<self.height and 0<=coords[0]+position[0]<self.width and self.field[coords[1]+position[1]][coords[0]+position[0]] <= 1 for coords in rotation)
        # dropPosValid = lambda piece, position: any( coords[1]+position[1] + 1>=self.height or self.field[coords[1]+position[1]+1][coords[0]+position[0]] > 1 for coords in rotation)

        return pieceValid(rotation, position) # and dropPosValid(rotation, position)

