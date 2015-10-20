def levelheight(field):
    for i in reversed(field):
        if not all(i):
            return (i-1) / len(field)
