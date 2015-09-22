

#TODO: need to account for t-spin points
def scoreCalc(field, player):
    _lineVals = {1:1, 2:3, 3:6, 4:12}
    scoreArray = [1]*field.height
    perfectClear = 1
    for index, arr in enumerate(field.field):
        for val in arr:
            if val != 0:
                perfectClear = 0
            if val in [0,3]:
                scoreArray[index] = 0
                if perfectClear == 0:
                    continue
    score = 0
    if perfectClear != 0:
        for s in scoreArray:
            if s == 1:
                score += 1
        score = _lineVals[score]
    else:
        score = 24
    score += player.combo
    return score
