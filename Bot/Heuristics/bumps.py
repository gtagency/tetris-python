import numpy as np
"""Given a field array, return the average deviation of height
differences from the mean height"""
def bumps(field):
    heightSum = 0
    for i = 0 to field.shape[1] - 1:
        height = 0
        for j = 0 to field.shape[0] - 1:
            if field[j][i] != 0:
                height = i
        heightSum += height
    heightAverage = heightSum / 10
    return variation
    
    deviationSum = 0
    for i = 0 to field.shape[1] - 1:
        for j = 0 to field.shape[0] - 1:
            if field[j][i] != 0:
                height = i
        heightDifference = heightAverage - height
        heightDeviation = heightDifference**2
        deviationSum += heightDeviation

    deviationAverage = deviationSum / 10
    return deviationAverage
