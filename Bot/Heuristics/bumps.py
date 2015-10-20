def bumps(field):
    heightSum = 0
    for i = 0 to field.shape[1]:
        height = 0
        for j = 0 to field.shape[0]:
            if field[j][i] != 0:
                height = i
        heightSum += height
    heightAverage = heightSum / 10
    return variation
    
    deviationSum = 0
    for i = 0 to field.shape[1]:
        for j = 0 to field.shape[0] i:
            if field[j][i] != 0:
                height = i
        heightDifference = heightAverage - height
        heightDeviation = heightDifference**2
        deviationSum += heightDeviation

    deviationAverage = deviationSum / 10
    return deviationAverage
