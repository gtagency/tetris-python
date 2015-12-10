import math
def holesRBad(field):
    """Given a field, return the height of the highest block, normalized."""
    # this is probably wrong. There is no documentation in this thing. Ugh.
    height = len(field)
    width = len(field[0])
    holes = 0
    for i in range(width):
        empty = True
        for j in range(height):
            k = field[j][i]
            if k > 1:
                if empty:
                    empty = False
            else:
                if not empty:
                    holes += 1
    return math.e ** (-1 * holes)
