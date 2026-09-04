import Rhino
import Rhino.Geometry as rg
import scriptcontext as sc
import System
import System.Drawing


def _get_or_create_layer(layer_path):
    """
    Gibt den Layer-Index zurueck. Erstellt den Layer (und noetige
    Eltern-Layer bei verschachtelten Pfaden wie "Terrain::Schraffur"),
    falls er noch nicht existiert.
    """
    # GH-Wrapper (z.B. GH_String, GH_Number) entpacken, falls vorhanden
    if hasattr(layer_path, "Value"):
        layer_path = layer_path.Value
    layer_path = str(layer_path)

    layer_table = sc.doc.Layers
    parts = layer_path.split("::")

    parent_index = -1
    full_path = ""

    for part in parts:
        full_path = part if not full_path else full_path + "::" + part
        index = layer_table.FindByFullPath(full_path, -1)

        if index < 0:
            new_layer = Rhino.DocObjects.Layer()
            new_layer.Name = part
            if parent_index >= 0:
                new_layer.ParentLayerId = layer_table[parent_index].Id
            new_layer.Color = System.Drawing.Color.Black
            index = layer_table.Add(new_layer)

        parent_index = index

    return parent_index


def _find_owner_doc(sample_guids):
    """
    Ermittelt das RhinoDoc, das die referenzierten Objekte tatsaechlich
    enthaelt. Notwendig, weil Rhino 8 mehrere Dokumente gleichzeitig
    offen haben kann und Rhino.RhinoDoc.ActiveDoc (das Dokument des
    fokussierten Tabs) nicht zwingend das Dokument ist, das die
    Grasshopper-Datei enthaelt.
    """
    active = Rhino.RhinoDoc.ActiveDoc

    candidates = []
    if active is not None:
        candidates.append(active)
    try:
        for d in Rhino.RhinoDoc.OpenDocuments():
            candidates.append(d)
    except Exception:
        pass

    seen = set()
    unique_docs = []
    for d in candidates:
        if d is None or d.RuntimeSerialNumber in seen:
            continue
        seen.add(d.RuntimeSerialNumber)
        unique_docs.append(d)

    for guid in sample_guids:
        for d in unique_docs:
            if d.Objects.Find(guid) is not None:
                return d

    return active


def bake_objects_to_layers(objects, layers, bake):
    """
    Bakt eine Liste von Grasshopper-Geometrien (Brep, Curve, Surface, Mesh)
    auf eine Liste von Rhino-Layern. Fehlende Layer werden automatisch
    erstellt.

    Parameter
    ---------
    objects : list
        Liste von GH-Geometrien.
    layers : str oder list
        Ein einzelner Layername (gilt dann fuer alle Objekte) oder eine
        Liste gleicher Laenge wie objects. Verschachtelte Layer mit
        "::" trennen, z.B. "Terrain::Schraffur".
    bake : bool
        Nur wenn True wird tatsaechlich gebakt.

    Rueckgabe
    ---------
    list of System.Guid der gebakten Objekte.
    """
    guids = []

    if not bake or not objects:
        return guids

    if isinstance(layers, str):
        layers = [layers] * len(objects)
    elif len(layers) == 1 and len(objects) > 1:
        layers = list(layers) * len(objects)

    if len(layers) != len(objects):
        raise ValueError(
            "objects und layers muessen gleich lang sein (oder layers "
            "enthaelt nur einen Eintrag)."
        )

    # GH-Wrapper (z.B. GH_Brep, GH_Curve) entpacken, falls vorhanden
    unwrapped = []
    for obj in objects:
        geo = obj
        if geo is not None and hasattr(geo, "Value"):
            geo = geo.Value
        unwrapped.append(geo)

    sample_guids = [g for g in unwrapped if isinstance(g, System.Guid)][:5]

    # Innerhalb von GHPython zeigt sc.doc auf das GH-Proxy-Dokument, das
    # kein Baken unterstuetzt. Fuer die Dauer des Bakens auf das Rhino-
    # Dokument umschalten, das die Grasshopper-Datei tatsaechlich
    # hostet (nicht zwingend Rhino.RhinoDoc.ActiveDoc, falls mehrere
    # Dokumente gleichzeitig offen sind), und danach zurueckstellen.
    ghdoc = sc.doc
    doc = _find_owner_doc(sample_guids) if sample_guids else Rhino.RhinoDoc.ActiveDoc
    sc.doc = doc

    try:
        for geo, layer_name in zip(unwrapped, layers):
            if geo is None:
                guids.append(None)
                continue

            layer_index = _get_or_create_layer(layer_name)

            attributes = doc.CreateDefaultAttributes()
            attributes.LayerIndex = layer_index

            # Referenzierte Rhino-Objekte kommen als Guid statt als
            # Geometrie an (z.B. bei einem auf "referenced" gesetzten
            # Geometrie-Parameter). Dafuer die eigentliche Geometrie
            # aus dem Dokument holen.
            if isinstance(geo, System.Guid):
                rhino_obj = doc.Objects.Find(geo)
                if rhino_obj is None:
                    guids.append(None)
                    continue
                geo = rhino_obj.Geometry

            if isinstance(geo, rg.Brep):
                guid = doc.Objects.AddBrep(geo, attributes)
            elif isinstance(geo, rg.Curve):
                guid = doc.Objects.AddCurve(geo, attributes)
            elif isinstance(geo, rg.Surface):
                guid = doc.Objects.AddSurface(geo, attributes)
            elif isinstance(geo, rg.Mesh):
                guid = doc.Objects.AddMesh(geo, attributes)
            else:
                guid = doc.Objects.Add(geo, attributes)

            guids.append(guid)

        doc.Views.Redraw()
    finally:
        sc.doc = ghdoc

    return guids