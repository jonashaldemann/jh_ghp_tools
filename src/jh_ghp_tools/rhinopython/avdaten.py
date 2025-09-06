# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs
import json
import os
import codecs

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

def load_layer_map(filename="avdatenlayer.json"):
    script_dir = os.path.dirname(__file__)
    filepath = os.path.join(script_dir, filename)

    with codecs.open(filepath, "r", "utf-8") as f:
        return json.load(f)

# Dein Mapping-Dictionary (hier abgekürzt – ersetze ggf. durch das Original)
layer_map = load_layer_map()

# Ausführen
explode_blocks_and_move_to_instance_layer()
reassign_layers_and_cleanup(layer_map)
