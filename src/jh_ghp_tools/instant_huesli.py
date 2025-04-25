import math
import scriptcontext as sc
import Rhino
import ghpythonlib.components as gh


def instant_huesli(curve, giebelhoehe, flip, giebelposition, dachwinkel, bake):
    angle = 0.5 * math.pi if flip else 0.0

    # Solid
    extr_vec = gh.UnitZ(giebelhoehe)
    solid = gh.CapHoles(gh.Extrude(curve, extr_vec))

    # Vertikale Plane unter dem Giebel
    segments, _ = gh.Explode(curve, False)
    longest_segment = max(segments, key=lambda seg: gh.Length(seg))
    start, end = gh.EndPoints(longest_segment)
    vector, _ = gh.Rotate(
        gh.Vector2Pt(start, end, False), angle, gh.XYPlane(gh.ConstructPoint(0.0, 0.0, 0.0))
    )
    plane, _ = gh.AlignPlane(gh.XYPlane(gh.ConstructPoint(0.0, 0.0, 0.0)), vector)
    bbox, _ = gh.BoundingBox(solid, plane)
    diagonal = gh.Line(gh.BoxCorners(bbox)[4], gh.BoxCorners(bbox)[6])
    giebelpunkt, _, _ = gh.EvaluateLength(diagonal, giebelposition, True)
    giebelplane = gh.ConstructPlane(giebelpunkt, vector, plane.ZAxis)

    # Dachschräge
    dach_planes = [
        gh.Rotate3D(giebelplane, math.radians(90 - dachwinkel), giebelpunkt, vector)[0],
        gh.Mirror(
            gh.Rotate3D(giebelplane, math.radians(90 - dachwinkel), giebelpunkt, vector)[0],
            giebelplane,
        )[0],
    ]

    # Schneiden
    for plane in dach_planes:
        crv, _ = gh.BrepXPlane(solid, plane)
        breps = gh.CapHoles(gh.SplitBrep(solid, crv))
        solid = max(breps, key=lambda brep: gh.Volume(brep)[0])

    # Baken
    if bake:
        sc.doc = Rhino.RhinoDoc.ActiveDoc
        attributes = Rhino.DocObjects.ObjectAttributes()
        sc.doc.Objects.AddBrep(solid, attributes)
        sc.doc = sc.sticky.get("ghdoc", None)  # Retrieve ghdoc from scriptcontext's sticky dictionary

    return solid
