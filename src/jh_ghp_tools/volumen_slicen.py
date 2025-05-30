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
    schnitthoehe = 0.01
    storeys = int(h_tot / 2.5)

    # Ebenen für jede Etage erstellen
    storey_base_heights = [schnitthoehe] + [
        h_eg + schnitthoehe + h_og * i for i in range(storeys)
    ]
    planes = [
        rg.Plane(rg.Point3d(0, 0, height), rg.Vector3d.ZAxis)
        for height in storey_base_heights
    ]
    storeys = ["EG0"] + [f"OG{i}" for i in range(1, len(storey_base_heights) + 1)]

    # Schnittkurven berechnen
    x_curves = []
    areas = []
    tabelle = []
    for plane, storey in zip(planes, storeys):
        storey_curves = []
        for brep in breps:
            curves = rg.Brep.CreateContourCurves(brep, plane)
            if curves:
                storey_curves.extend(curves)

        storey_area = []
        for storey_curve in storey_curves:
            area_props = rg.AreaMassProperties.Compute(storey_curve)
            if area_props:
                storey_area.append(area_props.Area)

        storey_area = sum(storey_area)
        areas.append(storey_area)

        if storey_area > 0:
            tabelle.append(f"{storey} {int(storey_area)} m²")

        if storey_curves:
            x_curves.extend(storey_curves)

    total_area = sum(areas)
    total_area_str = f"ist {round(total_area)} m²"

    return x_curves, total_area_str, tabelle
