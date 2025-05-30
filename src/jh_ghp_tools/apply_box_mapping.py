import Rhino
import Rhino.Geometry as rg
import System
from Rhino.Render import TextureMapping
from typing import List, Any


def _extract_guid(guid: Any) -> System.Guid:
    if isinstance(guid, System.Guid):
        return guid
    if hasattr(guid, "Id") and isinstance(guid.Id, System.Guid):
        return guid.Id
    if hasattr(guid, "Value") and isinstance(guid.Value, System.Guid):
        return guid.Value
    return None


def apply_box_mapping(
    geometries: List[Any],
    guids: List[Any],
    x_dim: float,
    y_dim: float,
    z_dim: float,
    update: bool = False,
) -> List[rg.Box]:
    x_interval = rg.Interval(-x_dim / 2, x_dim / 2)
    y_interval = rg.Interval(-y_dim / 2, y_dim / 2)
    z_interval = rg.Interval(-z_dim / 2, z_dim / 2)

    boxes = []

    for geom, guid in zip(geometries, guids):
        rhino_guid = _extract_guid(guid)
        if not rhino_guid:
            continue

        plane = None

        # Für Breps
        print(geom)
        if isinstance(geom, rg.Brep) or isinstance(geom, rg.Extrusion):
            # Falls es eine Extrusion ist, in Brep umwandeln
            if isinstance(geom, rg.Extrusion):
                geom = geom.ToBrep()
                if geom is None:
                    continue
            print("is brep")
            face_areas = [
                rg.AreaMassProperties.Compute(face).Area for face in geom.Faces
            ]
            max_area_index, _ = max(enumerate(face_areas), key=lambda x: x[1])
            face = geom.Faces[max_area_index]
            face_brep = face.DuplicateFace(False)
            edge_curves = [edge.EdgeCurve for edge in face_brep.Edges]
            if not edge_curves:
                continue
            longest = max(edge_curves, key=lambda crv: crv.GetLength())
            start, end = longest.PointAtStart, longest.PointAtEnd
            y_vector = end - start
            face_normal = face_brep.Faces[0].NormalAt(0.5, 0.5)
            x_vector = rg.Vector3d.CrossProduct(y_vector, face_normal)
            plane = rg.Plane(start, x_vector, y_vector)

        # Für Meshes
        elif isinstance(geom, rg.Mesh):
            max_area = 0
            max_face_index = -1

            for i in range(geom.Faces.Count):
                face = geom.Faces[i]
                pts = []
                for idx in (face.A, face.B, face.C):
                    v = geom.Vertices[idx]
                    # Falls v kein Point3d ist, explizit erzeugen
                    pt = rg.Point3d(v.X, v.Y, v.Z)
                    pts.append(pt)

                polyline = rg.Polyline()
                for pt in pts:
                    polyline.Add(pt)
                polyline.Add(pts[0])
                area_props = rg.AreaMassProperties.Compute(polyline.ToNurbsCurve())
                area = area_props.Area if area_props else 0

                if area > max_area:
                    max_area = area
                    max_face_index = i

            if max_face_index < 0:
                continue

            face = geom.Faces[max_face_index]

            pts = [
                rg.Point3d(
                    geom.Vertices[face.A].X,
                    geom.Vertices[face.A].Y,
                    geom.Vertices[face.A].Z,
                ),
                rg.Point3d(
                    geom.Vertices[face.B].X,
                    geom.Vertices[face.B].Y,
                    geom.Vertices[face.B].Z,
                ),
                rg.Point3d(
                    geom.Vertices[face.C].X,
                    geom.Vertices[face.C].Y,
                    geom.Vertices[face.C].Z,
                ),
            ]

            edges = [
                (pts[0], pts[1]),
                (pts[1], pts[2]),
                (pts[2], pts[0]),
            ]

            longest_edge = max(edges, key=lambda e: e[0].DistanceTo(e[1]))
            start, end = longest_edge
            y_vector = end - start

            v1 = pts[1] - pts[0]
            v2 = pts[2] - pts[0]
            face_normal = rg.Vector3d.CrossProduct(v1, v2)
            face_normal.Unitize()

            x_vector = rg.Vector3d.CrossProduct(y_vector, face_normal)
            x_vector.Unitize()
            y_vector.Unitize()

            plane = rg.Plane(start, x_vector, y_vector)

        else:
            print("is none")
            continue

        box = rg.Box(plane, x_interval, y_interval, z_interval)
        boxes.append(box)

        if update:
            obj_ref = Rhino.RhinoDoc.ActiveDoc.Objects.Find(rhino_guid)
            print(obj_ref)
            if obj_ref:
                mapping = TextureMapping.CreateBoxMapping(
                    plane, x_interval, y_interval, z_interval, True
                )
                mapping_channel = 1
                Rhino.RhinoDoc.ActiveDoc.Objects.ModifyTextureMapping(
                    obj_ref.Id, mapping_channel, mapping
                )
                attr = obj_ref.Attributes
                attr.MaterialSource = (
                    Rhino.DocObjects.ObjectMaterialSource.MaterialFromObject
                )
                attr.MappingChannel = mapping_channel
                Rhino.RhinoDoc.ActiveDoc.Objects.ModifyAttributes(obj_ref, attr, True)

    return boxes
