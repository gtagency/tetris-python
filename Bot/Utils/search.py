

def orderChildren(piecePositions):
    #need to ensure that the up state is returned first if applicable

def dfs (piecePositions, goalPositions):
    if piecePositions == goalPositions:
        return piecePositions
    horizon = []
    closed = []
    currentPosition = (piecePositions, [])
    while (currentPosition != goalPositions):
        if currentPosition[0] not in closed:
            children = orderChildren(currentPosition)
            for i in children:
                if i[0] == goalPositions:
                    return i
                if i[0] not in closed:
                    horizon.append(i)
            closed.append(currentPosition[0])
        if len(horizon) == 0:
            return False
        currentPosition = horizon.pop()
