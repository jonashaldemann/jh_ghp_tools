import Rhino
from Rhino import Render
import Rhino.Geometry as rg
import rhinoscriptsyntax as rs


def bake_box_map(brep, box, bake_toggle):
    box_plane = box.Plane
    dx = box.X
    dy = box.Y
    dz = box.Z

    if bake_toggle:
        rs.EnableRedraw(False)
        guid = Rhino.RhinoDoc.ActiveDoc.Objects.Add(brep)
        boxmap = Render.TextureMapping.CreateBoxMapping(box_plane, dx, dy, dz, False)
        Rhino.RhinoDoc.ActiveDoc.Objects.ModifyTextureMapping(guid, 1, boxmap)
        rs.EnableRedraw(True)
