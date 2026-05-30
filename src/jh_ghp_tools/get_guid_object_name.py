import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs


def get_guid_object_name(guids):
    """
    Nicht mehr verwendet
    """

    # Temporär auf das aktive Rhino-Dokument umstellen
    sc.doc = Rhino.RhinoDoc.ActiveDoc

    if guids:
        object_names = []
        for guid in guids:
            obj = sc.doc.Objects.Find(guid)
            if obj:
                object_name = obj.Name
                object_names.append(object_name)

    return object_names