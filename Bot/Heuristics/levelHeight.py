def levelHeight(field):
    """Given a field, return the height of the highest block, normalized."""
    # this is probably wrong. There is no documentation in this thing. Ugh.
    for i in reversed(field):
        if not all(i):
            return i-1 / len(field)

