def levelHeight(field):
    """Given a field, return the height of the highest block, normalized."""
    # this is probably wrong. There is no documentation in this thing. Ugh.
    for i in range(len(field)):
        empty = True
        for k in field[i]:
            if k > 1:
                empty = False
        if not empty:
            return i / len(field)
    return 1
