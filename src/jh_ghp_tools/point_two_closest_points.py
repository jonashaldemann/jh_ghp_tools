import Rhino.Geometry as rg

def point_two_closest_points(points):
  
    lines = []
    for i, pt in enumerate(points):
        # Calculate distances to all other points
        dists = [(j, pt.DistanceTo(points[j])) for j in range(len(points)) if j != i]
        # Sort by distance and get indices of two closest
        closest = sorted(dists, key=lambda x: x[1])[:2]
        for idx, _ in closest:
            line = rg.Line(pt, points[idx])
            lines.append(line)
    
    
    # Join lines that are contiguous
    joined_curves = rg.Curve.JoinCurves([rg.LineCurve(line) for line in lines])

    return joined_curves