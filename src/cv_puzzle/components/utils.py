def get_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculates the squared euclidian distance between two points.

    d(x,y)^2 = (x1-y1)^2 + (x2-y2)^2
    """
    euclidian_distance = (x1 - x2) ** 2 + (y1 - y2) ** 2

    return euclidian_distance
