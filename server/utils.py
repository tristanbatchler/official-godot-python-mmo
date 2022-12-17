import math

def direction_to(current: list, target: list) -> list:
    "Return the vector with unit length pointing in the direction from current to target"
    if target == current:
        return [0, 0]
    
    n_x = target[0] - current[0]
    n_y = target[1] - current[1]

    length = math.dist(current, target)
    return [n_x / length, n_y / length]