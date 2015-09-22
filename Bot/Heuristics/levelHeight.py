def levelHeight(field):
    """Given a field, return the height of the highest block, normalized."""
    # this is probably wrong. There is no documentation in this thing. Ugh.
    height = 0
    for i in reversed(range(len(field))):
        for j in range(len(field[0])):
            if field[i][j] == 1:
                height = i
                break
    normalizedHeight = float(height) / len(field)
    return normalizedHeight

