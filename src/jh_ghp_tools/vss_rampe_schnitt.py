import ghpythonlib.components as gh


def rampe_im_schnitt(geschosshoehe, gefaelle):
    # Punkte definieren
    p1 = gh.ConstructPoint(-20, 0, 0)
    p2 = gh.ConstructPoint(0, 0, 0)

    # Rampe konstruieren
    v = gh.Rotate(gh.UnitX(1), -gh.Radians(gefaelle), gh.XYPlane(p2))[0]
    vx, vy, _ = gh.DeconstructVector(v)
    laenge_provisorisch = vx / -vy * geschosshoehe

    p3 = gh.ConstructPoint(laenge_provisorisch, -geschosshoehe, 0)
    p4 = gh.ConstructPoint(laenge_provisorisch + 20, -geschosshoehe, 0)

    # Eckige Rampe
    pline = gh.PolyLine([p1, p2, p3, p4], False)

    # Erste Rundung
    pline = gh.Fillet(pline, 1, 20)[0]

    # Zweite Rundung an Diskontinuität
    discont = gh.Discontinuity(pline, 1)[1][1]
    pline = gh.Fillet(pline, discont, 30)[0]

    # Start- und Endsegmente abschneiden
    segments = list(gh.Explode(pline, True)[0])
    middle_segments = segments[1:-1]

    # Rampe wieder zusammensetzen
    rampe = gh.JoinCurves(middle_segments, True)

    # Länge berechnen
    start, end = gh.EndPoints(rampe)
    sx, _, _ = gh.Deconstruct(start)
    ex, _, _ = gh.Deconstruct(end)
    laenge = ex - sx
    return rampe, laenge
