# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs
import json
import os


# -------------------------------
# Schritt 0: Layer Mapping laden
# -------------------------------
def load_layer_map():
    file_path = rs.OpenFileName(
        "Layer-Mapping-Datei auswählen",
        "JSON files (*.json)|*.json|All files (*.*)|*.*||",
    )
    if not file_path:
        raise FileNotFoundError("Keine Datei ausgewählt.")
    with open(file_path, "r") as f:
        return json.load(f)


layer_map = load_layer_map()


# -------------------------------
# Schritt 1: Alle Blockinstanzen explodieren
# -------------------------------
def explode_blocks():
    block_instances = [
        obj for obj in rs.AllObjects() if rs.ObjectType(obj) == rs.filter.instance
    ]
    if not block_instances:
        return
    for instance in block_instances:
        rs.ExplodeBlockInstance(instance)


# -------------------------------
# Schritt 2: Objekte anhand Mapping verschieben
# -------------------------------
def reassign_layers(layer_map):
    for source_layer, target_layer in layer_map.items():
        if not rs.IsLayer(source_layer):
            continue
        if not rs.IsLayer(target_layer):
            rs.AddLayer(target_layer)
        objs = rs.ObjectsByLayer(source_layer, True)
        if objs:
            for obj in objs:
                rs.ObjectLayer(obj, target_layer)


# -------------------------------
# Schritt 3: Leere Layer rekursiv löschen
# -------------------------------
def delete_layer_recursive(layer):
    if not rs.IsLayer(layer):
        return
    sublayers = rs.LayerChildren(layer) or []
    for sub in sublayers:
        delete_layer_recursive(sub)
    objs = rs.ObjectsByLayer(layer, True)
    if objs:
        print(
            "Layer", layer, "hat noch", len(objs), "Objekte, kann nicht gelöscht werden"
        )
        return
    try:
        rs.DeleteLayer(layer)
        print("Layer gelöscht:", layer)
    except Exception as e:
        print("Fehler beim Löschen von", layer, ":", e)


def cleanup_layers(layer_map):
    for source_layer in layer_map.keys():
        delete_layer_recursive(source_layer)


# -------------------------------
# Optional: Blockdefinitionen löschen
# -------------------------------
def delete_all_block_definitions():
    for block in rs.BlockNames():
        try:
            rs.DeleteBlock(block)
        except Exception as e:
            print("Konnte Blockdefinition nicht löschen:", block, e)


# -------------------------------
# Optional: Alle leeren Layer löschen
# -------------------------------
def cleanup_all_empty_layers():
    for layer in rs.LayerNames():
        objs = rs.ObjectsByLayer(layer, True)
        if not objs:
            delete_layer_recursive(layer)


# -------------------------------
# Hauptskript ausführen
# -------------------------------
explode_blocks()
reassign_layers(layer_map)
cleanup_layers(layer_map)
cleanup_all_empty_layers()
# delete_all_block_definitions()  # optional aktivieren
