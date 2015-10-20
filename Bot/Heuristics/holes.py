def holes(field):
    totalHoles = 0
    for i = 0 to field.shape[1]:
        for j = 0 to field.shape[0]:
            if field[j][i] == 0:
                totalHoles++
    return totalHoles
