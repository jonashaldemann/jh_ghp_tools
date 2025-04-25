import itertools


def wohnungsteilung(module_sizes, total_area, max_residual):
    """
    Optimiert die Anzahl der Module, um die Restfläche zu minimieren.

    :param module_sizes: Liste der Modulgrößen (in m²)
    :param total_area: Gesamtfläche (in m²)
    :param max_residual: Maximale erlaubte Restfläche (in m²)
    :return: Keine Rückgabe, gibt die Ergebnisse direkt aus
    """
    max_units_per_module = 10  # Maximale Anzahl an Modulen pro Größe
    ranges = [range(0, max_units_per_module + 1) for _ in module_sizes]

    results = []

    # Alle möglichen Kombinationen von Modulanordnungen berechnen
    for combo in itertools.product(*ranges):
        area = sum(n * size for n, size in zip(combo, module_sizes))
        residual = total_area - area
        if 0 <= residual <= max_residual:
            results.append((combo, residual))

    # Ergebnisse nach Restfläche sortieren
    results.sort(key=lambda x: x[1])

    # Ergebnisse ausgeben
    print(f"Modulkombinationen mit max. {max_residual} m² Restfläche:")
    for combo, residual in results:
        module_list = [
            f"{n} x {size} m²" for n, size in zip(combo, module_sizes) if n > 0
        ]
        print(f"{' + '.join(module_list)} -> Rest: {residual} m²")
