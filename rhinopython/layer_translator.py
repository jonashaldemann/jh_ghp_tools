# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs
import json
import unicodedata
import io


# -------------------------------
# Hilfsfunktion: Unicode Normalisierung
# -------------------------------
def norm(s):
    if not s:
        return s
    return unicodedata.normalize("NFC", s)


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

    with io.open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Keys und Values normalisieren
    return {
        norm(k): norm(v)
        for k, v in data.items()
    }


layer_map = load_layer_map()


# -------------------------------
# Schritt 1: Alle Blockinstanzen explodieren
# -------------------------------
def explode_blocks():
    block_instances = [
        obj for obj in rs.AllObjects()
        if rs.ObjectType(obj) == rs.filter.instance
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

        source_layer = norm(source_layer)
        target_layer = norm(target_layer)

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
    layer = norm(layer)

    if not rs.IsLayer(layer):
        return

    sublayers = rs.LayerChildren(layer) or []

    for sub in sublayers:
        delete_layer_recursive(sub)

    objs = rs.ObjectsByLayer(layer, True)

    if objs:
        print("Layer", layer, "hat noch", len(objs), "Objekte")
        return

    try:
        rs.DeleteLayer(layer)
    except Exception as e:
        print("Fehler beim Löschen von", layer, ":", e)


def cleanup_layers(layer_map):
    for source_layer in layer_map.keys():
        delete_layer_recursive(source_layer)


# -------------------------------
# Optional: Alle leeren Layer löschen
# -------------------------------
def cleanup_all_empty_layers():
    for layer in rs.LayerNames():
        layer = norm(layer)

        objs = rs.ObjectsByLayer(layer, True)

        if not objs:
            delete_layer_recursive(layer)


# -------------------------------
# Optional: Blockdefinitionen löschen
# -------------------------------
def delete_all_block_definitions():
    for block in rs.BlockNames():
        try:
            rs.DeleteBlock(block)
        except Exception as e:
            print("Block konnte nicht gelöscht werden:", block, e)


# -------------------------------
# Hauptskript
# -------------------------------
explode_blocks()
reassign_layers(layer_map)
cleanup_layers(layer_map)
cleanup_all_empty_layers()
# delete_all_block_definitions()