import Rhino
import ghpythonlib.components as gh
import random
import math
from compas.geometry import Point, Box, Polyline
from compas.geometry import (
    closest_point_on_polyline,
    distance_point_point,
    is_point_in_polygon_xy,
    distance_point_point,
)
from compas_rhino.conversions import point_to_rhino, point_to_compas


def verlaufsschraffur(x_domain, y_domain, N, CB, C1, C0, cell_size):
    """
    Eingangsfunktion, die Punkte innerhalb eines Polygons generiert und filtert.
    """
    # Konvertiere Polylines
    cb = curve_to_polyline_smart(CB)
    c1 = curve_to_polyline_smart(C1)
    c0 = curve_to_polyline_smart(C0)

    # Bereich aus den Domains extrahieren
    x0, x1, y0, y1 = deconstruct_domains(x_domain, y_domain)

    # Punkte generieren
    points = generate_points(cb, c1, c0, x0, x1, y0, y1, N, cell_size)

    # Zusätzliche Filterung am Ende
    points = filter_points(points, c0, c1)

    return points


def deconstruct_domains(x_domain, y_domain):
    """
    Extrahiert die Grenzen aus den x- und y-Domains.
    """
    x0, x1 = x_domain.T0, x_domain.T1
    y0, y1 = y_domain.T0, y_domain.T1
    return x0, x1, y0, y1


def is_cell_in_polygon(cell, polygon):
    """
    Prüft, ob eine Zelle vollständig, teilweise oder gar nicht innerhalb eines Polygons liegt.
    """
    cell_corners = [cell.corner(i) for i in range(4)]
    inside_status = [is_point_in_polygon_xy(corner, polygon) for corner in cell_corners]

    if all(inside_status):
        return "inside"
    elif any(inside_status):
        return "partial"
    else:
        return "outside"


def generate_points(cb, c1, c0, x0, x1, y0, y1, N, cell_size):
    """
    Generiert Punkte innerhalb der gegebenen Bereiche basierend auf den Polygonbedingungen.
    """
    cols = int(
        (x1 - x0) // cell_size + (1 if (x1 - x0) % cell_size else 0)
    )  # aufrunden
    rows = int(
        (y1 - y0) // cell_size + (1 if (y1 - y0) % cell_size else 0)
    )  # aufrunden
    points = []
    num_points_per_cell = N // (cols * rows)

    for col in range(cols):
        for row in range(rows):
            # Zelle definieren
            x_min = x0 + col * cell_size
            x_max = x_min + cell_size
            y_min = y0 + row * cell_size
            y_max = y_min + cell_size

            # Box mit Eckpunkten erstellen
            corner_1 = [x_min, y_min, 0.0]
            corner_2 = [x_max, y_max, 0.0]
            cell = Box.from_points([corner_1, corner_2])

            # Zelle testen
            cell_status = is_cell_in_polygon(cell, cb)

            if cell_status == "inside":
                points.extend(
                    generate_points_in_inside_cell(
                        x_min, x_max, y_min, y_max, num_points_per_cell, c0, c1
                    )
                )
            elif cell_status == "partial":
                points.extend(
                    generate_points_in_partial_cell(
                        x_min, x_max, y_min, y_max, num_points_per_cell, cb, c0, c1
                    )
                )

    return points


def generate_points_in_inside_cell(x_min, x_max, y_min, y_max, num_points, c0, c1):

    points = []

    for _ in range(num_points):
        pt = generate_point_in_cell(x_min, x_max, y_min, y_max, c0, c1)
        if pt:
            points.append(point_to_rhino(pt))
    return points


def generate_points_in_partial_cell(x_min, x_max, y_min, y_max, num_points, cb, c0, c1):
    """
    Generiert Punkte innerhalb einer vollständig im Polygon liegenden Zelle.
    """
    points = []
    for _ in range(num_points):
        pt = generate_point_in_cell(x_min, x_max, y_min, y_max, c0, c1)
        if not pt:
            continue
        if not is_point_in_polygon_xy(pt, cb):
            continue
        points.append(point_to_rhino(pt))
    return points


def filter_points(points, c0, c1):
    """
    Filtert die generierten Punkte basierend auf einem Schwellenwert.
    """
    return [
        pt
        for pt in points
        if calculate_threshold(Point(pt.X, pt.Y, pt.Z), c0, c1) >= random.random()
    ]


def calculate_threshold(pt, c0, c1):
    pt0 = closest_point_on_polyline(pt, c0)
    pt1 = closest_point_on_polyline(pt, c1)
    dmax = distance_point_point(pt0, pt1)
    d0 = distance_point_point(pt, pt0)
    return d0 / dmax


def generate_point_in_cell(x_min, x_max, y_min, y_max, c0, c1):
    x = random.uniform(x_min, x_max)
    y = random.uniform(y_min, y_max)
    pt = Point(x, y, 0.0)
    return pt


def curve_to_polyline_smart(curve, rebuild_points=5):
    """
    Konvertiert eine Rhino Curve in eine COMPAS Polyline.
    Explodiert die Kurve in Teilsegmente:
    - lineare Segmente werden direkt übernommen
    - nicht-lineare Segmente werden in 'rebuild_points' Punkten approximiert

    Parameters
    ----------
    curve : Rhino.Geometry.Curve
        Eingabekurve
    rebuild_points : int
        Anzahl Stützpunkte für die Approximation nicht-linearer Segmente

    Returns
    -------
    Polyline
        COMPAS Polyline
    """
    polypoints = []

    # Explodieren
    segments = curve.DuplicateSegments()
    if not segments:
        segments = [curve]  # falls nicht segmentierbar (z.B. einfache Linie)

    for seg in segments:
        if seg.IsLinear():
            # Linie = nur Endpunkte
            pts = [seg.PointAtStart, seg.PointAtEnd]
        else:
            # Nicht-linear = rebuild
            t0, t1 = seg.Domain.T0, seg.Domain.T1
            ts = [
                t0 + (t1 - t0) * i / (rebuild_points - 1) for i in range(rebuild_points)
            ]
            pts = [seg.PointAt(t) for t in ts]

        # COMPAS Punkte
        compas_pts = [point_to_compas(pt) for pt in pts]

        # Vermeide doppelte Punkte beim Zusammenfügen
        if polypoints:
            if distance_point_point(compas_pts[0], polypoints[-1]) < 1e-6:
                compas_pts = compas_pts[1:]

        polypoints.extend(compas_pts)

    return Polyline(polypoints)


# Ausfhren in GhPython
# points = verlaufsschraffur(x_domain, y_domain, N, CB, C1, C0, cell_size)
