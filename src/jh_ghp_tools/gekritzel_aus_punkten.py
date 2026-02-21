import Rhino.Geometry as rg

def gekritzel_aus_punkten(P):
    if not P or len(P) < 2:
        return None

    # Ersten Punkt entnehmen
    P_null = P.pop(0)
    P_sorted = [P_null]

    # Solange Punkte übrig sind
    while P:
        # Distanzen zum aktuellen Punkt berechnen
        distances = [P_null.DistanceTo(p) for p in P]
        # Index des nächsten Punkts finden
        index = distances.index(min(distances))
        # Nächsten Punkt holen
        P_next = P.pop(index)
        P_sorted.append(P_next)
        # Referenzpunkt aktualisieren
        P_null = P_next

    # Polyline aus sortierten Punkten erzeugen
    C = rg.Polyline(P_sorted)
    return C
