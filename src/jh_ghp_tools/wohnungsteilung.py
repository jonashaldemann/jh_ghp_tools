from pulp import LpProblem, LpVariable, LpInteger, lpSum, LpMinimize
import itertools


def wohnungsteilung(module_sizes, total_area, max_residual):
    """
    Optimiert die Anzahl der Module, um die Restfläche zu minimieren.

    :param module_sizes: Liste der Modulgrößen
    :param total_area: Gesamtfläche
    :return: Optimale Modulanzahl und Restfläche
    """

    max_units_per_module = 10

    ranges = [range(0, max_units_per_module + 1) for _ in module_sizes]

    results = []

    for combo in itertools.product(*ranges):
        area = sum(n * size for n, size in zip(combo, module_sizes))
        residual = total_area - area
        if 0 <= residual <= max_residual:
            results.append((combo, residual))
    
    results.sort(key=lambda x: x[1])

    print(f"Modulkombinationen mit max. {max_residual} m² Restfläche:")
    for combo, residual in results:
        module_list = [f"{n} x {size} m²" for n, size in zip(combo, module_sizes) if n > 0]
        print(f"{' + '.join(module_list)} -> Rest: {residual} m²")

