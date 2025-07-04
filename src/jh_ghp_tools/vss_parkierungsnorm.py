import ghpythonlib.components as gh
import math


def vss_parkierungsnorm(Gv, W, Pf, U, V):
    """
    Berechnet Parkierungsszenarien basierend auf der VSS-Norm.
    Args:
        Gv (bool): Gibt an, ob Gegenverkehr berücksichtigt werden soll.
                   Wenn True, wird die Mindestbreite der Fahrgasse auf 5.50 gesetzt, falls sie kleiner ist.
        W (float): Winkel der Parkplätze in Grad (z. B. 90, 75, 70, 60, 45, 30).
        Pf (float): Breite eines Parkfeldes in Metern (z. B. 2.50, 2.55, 2.60, etc.).
        U (int): Anzahl der Parkreihen in U-Richtung.
        V (int): Anzahl der Parkplätze in V-Richtung.
    Returns:
        tuple:
            - Geo (list): Liste von Rechtecken (geometrische Objekte), die die Parkplätze darstellen.
            - Info (str): Information über die berechnete Fahrgassenbreite.
    """

    # Fixe Werte
    parkfeldlaenge = 5.00
    winkel_rad = math.radians(90 - W)

    d_pf = {
        90: {
            2.50: 6.50,
            2.55: 6.25,
            2.60: 6.00,
            2.65: 5.75,
            2.70: 5.50,
            2.75: 5.25,
            2.80: 5.00,
        },
        75: {2.50: 5.00, 2.65: 4.50},
        70: {2.50: 4.50, 2.70: 4.00},
        60: {2.50: 3.50, 2.80: 3.20},
        45: {2.50: 3.20},
        30: {2.50: 3.20},
    }

    # Fahrgasse auslesen ohne Fallback-Wert ("")
    fahrgasse = d_pf.get(W, {}).get(Pf, "")

    # Mindestbreite bei Gegenverkehr
    if Gv and fahrgasse < 5.50:
        fahrgasse = 5.50

    # Versatzberechnungen
    reihenversatz = parkfeldlaenge * math.sin(winkel_rad)
    x_versatz = parkfeldlaenge * math.cos(winkel_rad)
    versatz_y = [(i // 2) * reihenversatz for i in range(U)]
    fahrgassenzuschlag = Pf * math.sin(winkel_rad)

    # U-Richtung
    series_u = []
    wert = 0
    for i in range(U):
        series_u.append(wert)
        wert += x_versatz + (fahrgasse + fahrgassenzuschlag if i % 2 == 0 else 0)

    # V-Richtung
    shift = Pf / math.cos(winkel_rad)
    series_v = [i * shift for i in range(V)]

    # Punktgitter
    points = []
    for i, u in enumerate(series_u):
        y_offset = versatz_y[i]
        for v in series_v:
            points.append(gh.ConstructPoint(u, v + y_offset, 0))

    # Rechtecke
    Geo = gh.Rectangle(points, parkfeldlaenge, Pf, 0.0)[0]

    Geo_rotated = []
    for curve, point in zip(Geo, points):
        rotated = gh.Rotate(curve, winkel_rad, point)[0]
        Geo_rotated.append(rotated)

    # Output
    Geo = Geo_rotated
    Info = f"Fahrgasse = {fahrgasse}"
    return Geo, Info
