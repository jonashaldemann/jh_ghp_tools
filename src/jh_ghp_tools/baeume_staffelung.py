import Rhino.Geometry as rg


def baeume_staffelung(curves, max_loops=50, tol=0.001):
    """
    Iterative Kurven-Überlappungsreduktion.
    Kleine Kurven zuerst, Überschneidungen werden abgezogen.
    Ergebnis: geschlossene Kurven.
    """

    # Hilfsfunktion: sichere Fläche einer Kurve
    def curve_area_safe(crv):
        amp = rg.AreaMassProperties.Compute(crv)
        return amp.Area if amp else 0.0

    # Sortiere Kurven nach Fläche aufsteigend
    curves_sorted = sorted(curves, key=curve_area_safe)
    result_curves = []
    loop_count = 0

    while curves_sorted and loop_count < max_loops:
        loop_count += 1
        # Nimm die kleinste Kurve als Sample
        sample = curves_sorted.pop(0)
        sample_copy = sample.DuplicateCurve()

        remaining_curves = []

        for c in curves_sorted:
            # Boolean Difference: sample_copy minus c
            if sample_copy.IsClosed and c.IsClosed:
                diff = rg.Curve.CreateBooleanDifference(sample_copy, c, tol)
                if diff:
                    # Nehme das größte verbleibende Segment
                    diff = [
                        crv
                        for crv in diff
                        if crv and crv.IsClosed and curve_area_safe(crv) > tol
                    ]
                    if diff:
                        diff = sorted(diff, key=curve_area_safe, reverse=True)
                        sample_copy = diff[0]

            remaining_curves.append(c)

        # Füge Sample hinzu, wenn gültig
        if sample_copy and sample_copy.IsClosed and curve_area_safe(sample_copy) > tol:
            result_curves.append(sample_copy)

        curves_sorted = remaining_curves

    if loop_count >= max_loops:
        print("Maximale Anzahl Loops erreicht!")

    return result_curves
