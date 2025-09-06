# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs

def create_hatches_from_curves():
    # 1. Kurven vom Benutzer auswählen
    curves = rs.GetObjects("Wähle geschlossene Kurven aus für Hatches", rs.filter.curve, preselect=True)
    if not curves:
        print("Keine Kurven ausgewählt.")
        return
    
    # 2. Für jede Kurve prüfen, ob sie geschlossen ist und Hatch erstellen
    for curve in curves:
        if rs.IsCurveClosed(curve):
            try:
                # Solid Hatch erstellen
                rs.AddHatch(curve, "Solid")
            except Exception as e:
                print("Fehler beim Erstellen von Hatch für Kurve {}: {}".format(curve, e))
        else:
            print("Kurve {} ist nicht geschlossen, wird übersprungen.".format(curve))

# 3. Skript ausführen
create_hatches_from_curves()
