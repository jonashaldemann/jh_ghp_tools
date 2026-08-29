"""
random_lines_from_points.py

Erzeugt aus einer Liste von Punkten kurze Linien, die in zufaellige
Richtungen (in der XY-Ebene) zeigen.

Verwendung in GhPython:

    import sys
    path = r"C:\Pfad\zu\deinem\scripts-ordner"
    if path not in sys.path:
        sys.path.append(path)

    import random_linien
    from importlib import reload
    reload(random_linien_aus_punkten)

    C = random_linien_aus_punkten.random_linien_aus_punkten(P, L)

Inputs:
    P : List[Rhino.Geometry.Point3d]
    L : float - Linienlaenge
Output:
    List[Rhino.Geometry.Line]
"""

import math
import random

import Rhino



def random_lines_from_points(points, length):
    """Erzeugt fuer jeden Punkt eine Linie mit zufaelliger Richtung in der XY-Ebene."""
    if not points:
        raise ValueError("points ist leer - mindestens einen Punkt uebergeben.")

    length = length or 0.01

    lines = []
    for p in points:
        angle = random.uniform(0.0, 2.0 * math.pi)
        direction = Rhino.Geometry.Vector3d(1.0, 0.0, 0.0)
        direction.Rotate(angle, Rhino.Geometry.Vector3d.ZAxis)
        lines.append(Rhino.Geometry.Line(p, direction, length))

    return lines