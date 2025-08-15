# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs

# Schritt 1: Alle Blockinstanzen explodieren und Layer der Inhalte anpassen
def explode_blocks_and_move_to_instance_layer():
    block_instances = [obj for obj in rs.AllObjects() if rs.ObjectType(obj) == rs.filter.instance]
    if not block_instances:
        return
    for instance in block_instances:
        instance_layer = rs.ObjectLayer(instance)
        exploded = rs.ExplodeBlockInstance(instance)
        if exploded:
            for obj in exploded:
                rs.ObjectLayer(obj, instance_layer)

# Schritt 2: Objekte anhand Dictionary verschieben und Quell-Layer löschen
def reassign_layers_and_cleanup(layer_map):
    # Objekte verschieben
    for source_layer, target_layer in layer_map.items():
        if not rs.IsLayer(source_layer):
            continue

        # Ziel-Layer erstellen falls nötig
        if not rs.IsLayer(target_layer):
            rs.AddLayer(target_layer)

        # Objekte auf dem Quell-Layer holen
        objs = rs.ObjectsByLayer(source_layer, True)
        if objs:
            for obj in objs:
                rs.ObjectLayer(obj, target_layer)

    # Leere Quell-Layer löschen
    for source_layer in layer_map.keys():
        if rs.IsLayer(source_layer):
            objs = rs.ObjectsByLayer(source_layer)
            if not objs:
                rs.DeleteLayer(source_layer)

# Dein Mapping-Dictionary (hier abgekürzt – ersetze ggf. durch das Original)
layer_map = {
    "01129": "000 Kataster Text",
    "01122": "000 Kataster Fixpunkte",
    "01139": "000 Kataster Fixpunkte",
    "01131": "000 Kataster Fixpunkte",
    "01132": "000 Kataster Fixpunkte",
    "01212": "000 Kataster Gebäude",
    "01211": "000 Kataster Gebäude",
    "01234": "000 Kataster Grünflächen",
    "01225": "000 Kataster Hartflächen",
    "01231": "000 Kataster Landwirtschaft",
    "01221": "000 Kataster Strassen",
    "01252": "000 Kataster Grünflächen",
    "01226": "000 Kataster Strassen",
    "01236": "000 Kataster Grünflächen",
    "01227": "000 Kataster Strassen",
    "01241": "000 Kataster Gewässer",
    "01242": "000 Kataster Grünflächen",
    "01251": "000 Kataster Wald",
    "01233": "000 Kataster Grünflächen",
    "01224": "000 Kataster Gewässer",
    "01264": "000 Kataster Hartflächen",
    "01222": "000 Kataster Eisenbahn",
    "01219": "000 Kataster Text",
    "01229": "000 Kataster Text",
    "01249": "000 Kataster Text",
    "01243": "000 Kataster Gewässer",
    "01313": "000 Kataster Objekte",
    "01321": "000 Kataster Unterirdisch",
    "01323": "000 Kataster Dächer",
    "01315": "000 Kataster Objekte",
    "01316": "000 Kataster Objekte",
    "01312": "000 Kataster Objekte",
    "01324": "000 Kataster Objekte",
    "01314": "000 Kataster Objekte",
    "01341": "000 Kataster Unterirdisch",
    "01351": "000 Kataster Objekte",
    "01322": "000 Kataster Unterirdisch",
    "01342": "000 Kataster Objekte",
    "01311": "000 Kataster Gebäudeteil",
    "01317": "000 Kataster Objekte",
    "01331": "000 Kataster Objekte",
    "01343": "000 Kataster Objekte",
    "01334": "000 Kataster Objekte",
    "01364": "000 Kataster Objekte",
    "01369": "000 Kataster Text",
    "01329": "000 Kataster Text",
    "01519": "000 Kataster Text",
    "01529": "000 Kataster Text",
    "01539": "000 Kataster Text",
    "01653": "000 Kataster Parzelle Punkte",
    "01651": "000 Kataster Parzelle Punkte",
    "01654": "000 Kataster Parzelle Punkte",
    "01657": "000 Kataster Parzelle Punkte",
    "01652": "000 Kataster Parzelle Punkte",
    "01656": "000 Kataster Parzelle Punkte",
    "01659": "000 Kataster Text Fixpunkte",
    "01629": "000 Kataster Text",
    "01621": "000 Kataster Parzelle",
    "01619": "000 Kataster Text",
    "01639": "000 Kataster Text",
    "01611": "000 Kataster Parzelle",
    "01631": "000 Kataster Parzelle",
    "01299": "000 Kataster Text"
}

# Ausführen
explode_blocks_and_move_to_instance_layer()
reassign_layers_and_cleanup(layer_map)
