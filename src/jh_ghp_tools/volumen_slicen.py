import ghpythonlib.components as gh
import Rhino.Geometry as rg


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
    storey_base_heights = [schnitthoehe] + [h_eg + schnitthoehe + h_og * i for i in range(storeys)]
    planes = [rg.Plane(rg.Point3d(0, 0, height), rg.Vector3d.ZAxis) for height in storey_base_heights]

    # Schnittkurven berechnen
    x_curves = []
    for brep in breps:
        for plane in planes:
            curves = rg.Brep.CreateContourCurves(brep, plane)
            if curves:
                x_curves.extend(curves)

    # Flächen
    areas = []
    curve_data = []
    for crv in x_curves:
        if crv.IsClosed and crv.IsPlanar():
            area_props = rg.AreaMassProperties.Compute(crv)
            if area_props:
                area = area_props.Area
                endpoint = crv.PointAtEnd
                areas.append(area)
                curve_data.append((crv, endpoint))

    total_area = sum(areas)
    total_area_str = f"{round(total_area)} m²"

    # Extrusionen
    breps_new = []
    for crv, pt in curve_data:

        height = h_eg if pt.Z < schnitthoehe + 0.1 else h_og
        extrusion = rg.Extrusion.Create(crv, height, True)
        print(extrusion)
        if extrusion:
            brep_capped = extrusion.ToBrep()
            breps_new.append(brep_capped)

    return breps_new, total_area_str
