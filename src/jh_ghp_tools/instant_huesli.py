import ghpythonlib.components as gh
import math

def instant_huesli(curve, giebelhoehe, flip, giebelposition, dachwinkel, bake):

    if flip:
        angle = 0.5 * math.pi
    else:
        angle = 0.0

    # Solid
    extr_vec = gh.UnitZ(giebelhoehe)
    extrusion = gh.Extrude(curve, extr_vec)
    solid = gh.CapHoles(extrusion)

    # Vertikale Plane unter dem Giebel
    segments, _ = gh.Explode(curve, False)
    lengths = gh.Length(segments)
    longest_segment_index = lengths.index(max(lengths))
    longest_segment = segments[longest_segment_index]
    start, end = gh.EndPoints(longest_segment)
    vector, _ = gh.Vector2Pt(start, end, False)
    vector, _ =  gh.Rotate(vector, angle, gh.XYPlane(gh.ConstructPoint(0.0, 0.0, 0.0)))
    plane, _ = gh.AlignPlane(gh.XYPlane(gh.ConstructPoint(0.0, 0.0, 0.0)), vector)
    bbox, _ = gh.BoundingBox(solid, plane)
    start, end = gh.BoxCorners(bbox)[4], gh.BoxCorners(bbox)[6]
    diagonal = gh.Line(start, end)
    giebelpunkt, _, _ = gh.EvaluateLength(diagonal, giebelposition, True)
    giebelplane = gh.ConstructPlane(giebelpunkt, vector, plane.ZAxis)

    # Dachschräge
    dach_plane1, _ = gh.Rotate3D(giebelplane, math.radians(90 - dachwinkel), giebelpunkt, vector)
    dach_plane2, _ = gh.Mirror(dach_plane1, giebelplane)
    dach_planes = [dach_plane1, dach_plane2]

    # Schneiden
    for plane in dach_planes:
        crv, _ = gh.BrepXPlane(solid, plane)
        breps = gh.SplitBrep(solid, crv)
        breps = gh.CapHoles(breps)
        volumes, _ = gh.Volume(breps)
        solid = breps[volumes.index(max(volumes))]

    return solid