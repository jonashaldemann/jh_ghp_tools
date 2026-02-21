import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs


def get_guid_layer_name(guids):
    """
    Verwendet in:
        attributes_excel_to_rhino.py
        storeyizer.py
    """

    # Temporär auf das aktive Rhino-Dokument umstellen
    # Muss in R8 nicht mehr zurückgesetzt werden
    sc.doc = Rhino.RhinoDoc.ActiveDoc

    if guids:
        layer_names = []
        for guid in guids:
            obj = sc.doc.Objects.Find(guid)
            if obj:
                layer_name = sc.doc.Layers[obj.Attributes.LayerIndex].Name
                layer_names.append(layer_name)

    return layer_names