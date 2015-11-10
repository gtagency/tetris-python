import numpy as np
"""Given a field array, return the number of holes."""
def holes(field):
    totalHoles = 0
    for i = 0 to field.shape[1] - 1:
        for j = 0 to field.shape[0] - 1:
            if field[j][i] != 0:
                for k = j to field.shape[0] - 1:
                    if field[k][j] == 0:
                        totalHoles++
                i++

    return totalHoles
