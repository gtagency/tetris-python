import numpy as np
import copy

class Field:
    def __init__(self):
        self.width = 10
        self.height = 20
        self.field = np.array([[0]*self.width, [0]*self.height], np.int32) #[[0]*self.width]*self.height

    def size(self):
        return self.width, self.height

    def updateField(self, field):
        self.field = field

    def projectPieceDown(self, piece, offset):
        piecePositions = self.__offsetPiece(piece.positions(), offset)

        field = None
        for height in range(0, self.height-1):
            tmp = self.fitPiece(piecePositions, [0, height])

            if not tmp:
                break
            field = tmp

        return field

    @staticmethod
    def __offsetPiece(piecePositions, offset):
        piece = copy.deepcopy(piecePositions)
        for pos in piece:
            pos[0] += offset[0]
            pos[1] += offset[1]

        return piece

    def __checkIfPieceFits(self, piecePositions):
        for x,y in piecePositions:
            if 0 <= x < self.width and 0 <= y < self.height:
                if self.field[y][x] > 1:
                    return False
            else:
                return False
        return True

    def fitPiece(self, piecePositions, offset=None):
        if offset:
            piece = self.__offsetPiece(piecePositions, offset)
        else:
            piece = piecePositions

        field = copy.deepcopy(self.field)
        if self.__checkIfPieceFits(piece):
            for x,y in piece:
                field[y][x] = 4

            return field
        else:
            return None

    def getChildren(self, piece):
        findSpaces = lambda (x,y): [(p,q) for (p,q) in {(x-1,y),(x+1,y),(x,y-1),(x,y+1)} if (0<=p<self.width and 0<=q<self.height and self.field[p,q] == 0)]

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
        for (x,y), value in np.ndenumerate(self.field):
            if value == 0 and (y == 0 or self.field[x,y-1] != 0):
                children.union(findPieces((x,y)))
        paths = {}


        # compose = lambda x,f: {(x,y) for (x,y) in (x,f(x))} no, I want {(x,y) for y in f(x)}
        # composeElementWise = lambda x,f: frozenset.union(*{compose(x,f) for x in x})
        # findPieces = lambda x: (x,findSpaces(x))
        # composeSelf = lambda f, n: lambda x: x if n == 0 else composeSelf(f, n-1)(f(x))


