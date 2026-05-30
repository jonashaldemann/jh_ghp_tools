# -*- coding: utf-8 -*-

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino

def delete_curve_duplicates_of_hatches(tolerance=0.01):
    """
    Löscht alle sichtbaren Kurven, die geometrisch identisch oder nahezu identisch
    zu den Kanten sichtbarer Hatches sind.
    """

    # 1. Sichtbare Kurven und Hatches
    visible_objs = rs.VisibleObjects()
    if not visible_objs:
        print("Keine sichtbaren Objekte gefunden.")
        return

    curves = [o for o in visible_objs if rs.IsCurve(o)]
    hatches = [o for o in visible_objs if rs.IsHatch(o)]

    if not curves or not hatches:
        print("Keine Kurven oder Hatches gefunden.")
        return

    # 2. Hatch-Kanten extrahieren
    hatch_edges = []
    for h_id in rs.VisibleObjects():
        if rs.IsHatch(h_id):
            obj = sc.doc.Objects.Find(h_id)
            hatch = obj.Geometry
            # Explode liefert Liste von Curves
            curves = hatch.Explode()
            for c in curves:
                if isinstance(c, Rhino.Geometry.Curve):  # nur echte Kurven behalten
                    cid = sc.doc.Objects.AddCurve(c)
                    if cid:
                        hatch_edges.append(cid)

    if not hatch_edges:
        print("Keine Kanten der Hatches gefunden.")
        return

    # 3. Vergleich und Duplikate sammeln
    duplicates = []
    for c in curves:
        c_len = rs.CurveLength(c)
        c_start = rs.CurveStartPoint(c)
        c_end = rs.CurveEndPoint(c)
        c_closed = rs.IsCurveClosed(c)

        for e in hatch_edges:
            e_len = rs.CurveLength(e)
            e_start = rs.CurveStartPoint(e)
            e_end = rs.CurveEndPoint(e)
            e_closed = rs.IsCurveClosed(e)

            if c_closed != e_closed:
                continue

            if c_closed:
                # geschlossene Kurve: Fläche vergleichen
                c_centroid = rs.CurveAreaCentroid(c)[0]
                e_centroid = rs.CurveAreaCentroid(e)[0]
                if c_centroid.DistanceTo(e_centroid) <= tolerance:
                    duplicates.append(c)
                    break
            else:
                # offene Kurve: Start + End + Länge prüfen
                start_match = c_start.DistanceTo(e_start) <= tolerance or c_start.DistanceTo(e_end) <= tolerance
                end_match = c_end.DistanceTo(e_end) <= tolerance or c_end.DistanceTo(e_start) <= tolerance
                
                # zusätzlich Mittelpunkt prüfen
                c_mid = rs.CurveMidPoint(c)
                e_mid = rs.CurveMidPoint(e)
                mid_match = c_mid.DistanceTo(e_mid) <= tolerance

                length_match = abs(c_len - e_len) <= tolerance and mid_match
                if start_match and end_match and length_match:
                    duplicates.append(c)
                    break

    # 4. Löschen
    if duplicates:
        rs.DeleteObjects(duplicates)
        print("{} Duplikat-Kurve(n) gelöscht.".format(len(duplicates)))
    else:
        print("Keine Duplikate gefunden.")


# Skript ausführen
delete_curve_duplicates_of_hatches()