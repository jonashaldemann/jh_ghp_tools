import ghpythonlib.components as gh


def volumen_slicen(breps, h_eg, h_og, h_tot):
    """
    Berechnet Volumen-Schnitte und extrudiert diese basierend auf Eingabe-Breps.

    Args:
        breps (list): Eingabe-Breps.
        h_eg (float): Höhe des Erdgeschosses.
        h_og (float): Höhe eines Obergeschosses.
        h_tot (float): Gesamthöhe.

    Returns:
        tuple: (Liste der neuen Breps, Gesamtfläche als String)
    """
    schnitthoehe = 0.1
    storeys = int(h_tot / 2.5)

    # Ebenen für jede Etage erstellen
    storey_base_heights = [schnitthoehe] + [
        h_eg + schnitthoehe + h_og * i for i in range(storeys)
    ]
    planes = gh.XYPlane(gh.ConstructPoint(0, 0, storey_base_heights))

    # Schnittkurven berechnen
    x_curves = []
    for brep in breps:
        try:
            x_curve, _ = gh.BrepXPlane(brep, planes)
            x_curves.extend(x_curve)
        except Exception:
            pass

    # Flächen und Zentroiden berechnen
    areas, centroids = gh.Area(x_curves)
    total_area, _ = gh.MassAddition(areas)
    total_area_str = f"{round(total_area)} m²"

    # Extrusionshöhen bestimmen
    extrusion_heights = [
        h_eg if pt.Z < schnitthoehe + 0.1 else h_og for pt in centroids
    ]

    # Korrektur der Schnittkurven basierend auf Brep-Containment
    corrected_x_curves = []
    new_extrusion_heights = []
    for crv, centroid, height in zip(x_curves, centroids, extrusion_heights):
        moved_pt, _ = gh.Move(centroid, gh.UnitZ(height - schnitthoehe - 0.01))
        containment, _ = gh.PointInBreps(breps, moved_pt, True)
        if containment:
            corrected_x_curves.append(crv)
            new_extrusion_heights.append(height)

    # Extrudieren und Breps erstellen
    vectors = gh.UnitZ(new_extrusion_heights)
    open_breps = gh.Extrude(corrected_x_curves, vectors)
    breps_new = gh.CapHoles(open_breps)

    return breps_new, total_area_str