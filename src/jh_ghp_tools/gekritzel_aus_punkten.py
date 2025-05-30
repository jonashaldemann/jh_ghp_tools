import ghpythonlib.components as gh
import Grasshopper.Kernel as gk
from ghpythonlib.componentbase import executingcomponent as component


def gekritzel_aus_punkten(P):
    # do the work here
    C = None
    
    # Initialisierung
    P_null = P.pop(0)  # Erster Punkt und gleichzeitig aus der Liste entfernen
    P_sorted = [P_null]  # Liste mit sortierten Punkten

    # Punkte nach Nähe sortieren
    while P:  # Solange P nicht leer ist
        cp, index, _ = gh.ClosestPoint(P_null, P)
        P_sorted.append(cp)
        P_null = P.pop(index)  # Nächsten Punkt entfernen und als neuen Referenzpunkt setzen

    C = gh.PolyLine(P_sorted, False)
    return C

