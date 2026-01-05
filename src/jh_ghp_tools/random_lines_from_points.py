import math
import random
import Rhino

def random_lines_from_points(P: list, L: float):
    """
    Generate random lines from a list of points with a given length.

    Args:
        P (list[Rhino.Geometry.Point3d]): List of points.
        L (float): Length of each line.

    Returns:
        list[Rhino.Geometry.LineCurve]: List of lines as curves.
    """

    if not P:
        raise ValueError("Add Point Input")

    L = L or 0.01
    domain_min, domain_max = 0.0, 2 * math.pi

    curves = []
    for p in P:
        angle = random.uniform(domain_min, domain_max)

        # Startvektor
        vec = Rhino.Geometry.Vector3d(L, 0, 0)
        vec.Rotate(angle, Rhino.Geometry.Vector3d.ZAxis)

        # Linie erzeugen
        line = Rhino.Geometry.Line(p, p + vec)
        curves.append(Rhino.Geometry.LineCurve(line))

    return curves
