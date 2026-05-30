from collections import defaultdict

def gruppieren_nach_string(geometries, names):

    groups = defaultdict(list)
    order = []

    for geo, name in zip(geometries, names):
        if name not in groups:
            order.append(name)
        groups[name].append(geo)

    geometrie_gruppen = [groups[name] for name in order]
    name_gruppen = order

    return geometrie_gruppen, name_gruppen