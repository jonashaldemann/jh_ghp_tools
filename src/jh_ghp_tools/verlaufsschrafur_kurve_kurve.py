"""
verlaufsschraffur.py

Erzeugt eine Verlaufs-Punktschraffur entlang einer Schnittkante (Terrain-Schnitt).
Alle Funktionen liegen auf Modulebene (keine verschachtelten Definitionen).

Verwendung in GhPython:

    import sys
    path = r"C:\Pfad\zu\deinem\scripts-ordner"
    if path not in sys.path:
        sys.path.append(path)

    import verlaufsschraffur
    from importlib import reload
    reload(verlaufsschraffur)   # nur waehrend der Entwicklung noetig

    points = verlaufsschraffur.verlaufsschraffur(
        x_domain, y_domain, N, CB, C1, C0, cell_size, gamma, min_dist
    )

Inputs (GH-Component):
    x_domain, y_domain : Domain
    N                   : int   - grobe Ziel-Punktanzahl vor Filterung/Cull
    CB, C1, C0          : Curve - Begrenzung, aeussere/innere Referenzkurve
    cell_size           : float - Rastergroesse fuer Kandidaten-Generierung
    gamma               : float - Formfaktor der Abnahme (t**gamma). <1 = zuerst
                          schnellerer, dann langsamerer Abfall. 1.0 = linear (Original).
    min_dist            : float - Mindestabstand zwischen Punkten (ersetzt CullDuplicates)
"""

import random
import numpy as np

from compas.geometry import Point, Polyline
from compas_rhino.conversions import curve_to_compas_polyline, point_to_rhino


def curve_to_polyline_safe(curve, segments=50):
    """Wandelt beliebige Rhino-Kurve in COMPAS-Polyline um."""
    try:
        return curve_to_compas_polyline(curve)
    except Exception:
        domain = curve.Domain
        t_values = [domain[0] + (domain[1] - domain[0]) * i / segments for i in range(segments + 1)]
        pts = [curve.PointAt(t) for t in t_values]
        return Polyline([[p.X, p.Y, p.Z] for p in pts])


def deconstruct_domain_pair(x_domain, y_domain):
    """Zerlegt zwei GH-Domains in x0, x1, y0, y1."""
    import ghpythonlib.components as gh
    x0, x1 = gh.DeconstructDomain(x_domain)
    y0, y1 = gh.DeconstructDomain(y_domain)
    return x0, x1, y0, y1


def polyline_to_xy_array(polyline):
    """COMPAS-Polyline -> (M,2) numpy-Array (nur XY, Z wird ignoriert)."""
    return np.array([[p[0], p[1]] for p in polyline.points], dtype=float)


def points_in_polygon_xy(points_xy, poly_xy):
    """Vektorisierter Punkt-in-Polygon-Test (ray casting). points_xy: (N,2), poly_xy: (M,2)."""
    x = points_xy[:, 0]
    y = points_xy[:, 1]
    n = len(poly_xy)
    inside = np.zeros(len(points_xy), dtype=bool)
    j = n - 1
    for i in range(n):
        xi, yi = poly_xy[i]
        xj, yj = poly_xy[j]
        denom = (yj - yi) if (yj - yi) != 0 else 1e-12
        cond = ((yi > y) != (yj > y)) & (x < (xj - xi) * (y - yi) / denom + xi)
        inside = np.where(cond, ~inside, inside)
        j = i
    return inside


def min_dist_to_polyline(points_xy, poly_xy):
    """Vektorisierter minimaler Abstand jedes Punkts zu einer Polyline (Segment-Projektion)."""
    a = poly_xy[:-1]
    b = poly_xy[1:]
    ab = b - a
    ab_len2 = np.maximum(np.sum(ab ** 2, axis=1), 1e-12)
    ap = points_xy[:, None, :] - a[None, :, :]
    t = np.clip(np.sum(ap * ab[None, :, :], axis=2) / ab_len2[None, :], 0.0, 1.0)
    proj = a[None, :, :] + t[:, :, None] * ab[None, :, :]
    d = np.linalg.norm(points_xy[:, None, :] - proj, axis=2)
    return d.min(axis=1)


def generate_candidate_grid(x0, x1, y0, y1, cell_size, n_per_cell):
    """Erzeugt zufaellige Kandidatenpunkte, gleichmaessig auf ein Zellenraster verteilt."""
    cols = max(int((x1 - x0) // cell_size + (1 if (x1 - x0) % cell_size else 0)), 1)
    rows = max(int((y1 - y0) // cell_size + (1 if (y1 - y0) % cell_size else 0)), 1)

    col_idx = np.repeat(np.arange(cols), rows * n_per_cell)
    row_idx = np.tile(np.repeat(np.arange(rows), n_per_cell), cols)

    x_min = x0 + col_idx * cell_size
    y_min = y0 + row_idx * cell_size

    rand_x = np.random.uniform(0.0, cell_size, size=col_idx.shape[0])
    rand_y = np.random.uniform(0.0, cell_size, size=col_idx.shape[0])

    return np.column_stack([x_min + rand_x, y_min + rand_y])


def calculate_thresholds(points_xy, c0_xy, c1_xy):
    """t = 0 an c0 (dichte Kante), t = 1 an c1 (verlaufsende), vektorisiert."""
    d0 = min_dist_to_polyline(points_xy, c0_xy)
    d1 = min_dist_to_polyline(points_xy, c1_xy)
    dmax = d0 + d1
    dmax = np.where(dmax == 0, 1e-12, dmax)
    return d0 / dmax


def cull_duplicates(points_xy, min_dist):
    """Entfernt Punkte, die naeher als min_dist beieinander liegen.
       Spatial-Hash-Grid -> O(N) statt O(N^2) wie CullDuplicates."""
    if min_dist <= 0 or len(points_xy) == 0:
        return points_xy

    cell_size = min_dist
    min_dist2 = min_dist * min_dist
    grid = {}
    keep_mask = np.zeros(len(points_xy), dtype=bool)

    order = np.arange(len(points_xy))
    np.random.shuffle(order)  # verhindert Bias durch Zeilen/Spalten-Reihenfolge

    for idx in order:
        x, y = points_xy[idx]
        cx = int(x // cell_size)
        cy = int(y // cell_size)
        too_close = False
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for oidx in grid.get((cx + dx, cy + dy), ()):
                    ox, oy = points_xy[oidx]
                    ddx = x - ox
                    ddy = y - oy
                    if ddx * ddx + ddy * ddy < min_dist2:
                        too_close = True
                        break
                if too_close:
                    break
            if too_close:
                break
        if not too_close:
            keep_mask[idx] = True
            grid.setdefault((cx, cy), []).append(idx)

    return points_xy[keep_mask]


def verlaufsschraffur_kurve_kurve(x_domain, y_domain, N, CB, C1, C0, cell_size, gamma, min_dist):
    """Hauptfunktion: von GhPython aus aufrufen."""
    cb = curve_to_polyline_safe(CB)
    c1 = curve_to_polyline_safe(C1)
    c0 = curve_to_polyline_safe(C0)

    cb_xy = polyline_to_xy_array(cb)
    c1_xy = polyline_to_xy_array(c1)
    c0_xy = polyline_to_xy_array(c0)

    x0, x1, y0, y1 = deconstruct_domain_pair(x_domain, y_domain)

    cols = max(int((x1 - x0) // cell_size + (1 if (x1 - x0) % cell_size else 0)), 1)
    rows = max(int((y1 - y0) // cell_size + (1 if (y1 - y0) % cell_size else 0)), 1)
    n_per_cell = max(1, int(N // max(cols * rows, 1)))

    candidates = generate_candidate_grid(x0, x1, y0, y1, cell_size, n_per_cell)

    inside_cb = points_in_polygon_xy(candidates, cb_xy)
    candidates = candidates[inside_cb]
    if len(candidates) == 0:
        return []

    t = calculate_thresholds(candidates, c0_xy, c1_xy)
    t_shaped = t ** gamma
    rnd = np.random.random(size=t_shaped.shape[0])
    candidates = candidates[t_shaped >= rnd]

    candidates = cull_duplicates(candidates, min_dist)

    return [point_to_rhino(Point(float(x), float(y), 0.0)) for x, y in candidates]