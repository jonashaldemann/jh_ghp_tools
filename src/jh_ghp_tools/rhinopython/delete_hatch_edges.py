# -*- coding: utf-8 -*-

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino

def sample_curve_points(curve, num=20):
    if not isinstance(curve, Rhino.Geometry.NurbsCurve):
        curve = curve.ToNurbsCurve()
    if not curve: return []
    t_vals = [curve.Domain.ParameterAt(i / float(num - 1)) for i in range(num)]
    return [curve.PointAt(t) for t in t_vals]

def move_curves_if_fully_on_hatch_edge(tol=0.01, num_points=20):
    deleted_layer = "_deleted_"
    if not rs.IsLayer(deleted_layer):
        rs.AddLayer(deleted_layer)

    C = rs.GetObjects("Waehle Kurven (C)", rs.filter.curve)
    H = rs.GetObjects("Waehle Hatches (H)", rs.filter.hatch)
    if not C or not H: return

    hatch_edges = []
    for hid in H:
        h_obj = sc.doc.Objects.Find(hid)
        hatch = h_obj.Geometry
        if isinstance(hatch, Rhino.Geometry.Hatch):
            loops = hatch.Get3dCurves(True) + hatch.Get3dCurves(False)
            for loop in loops:
                nurbs = loop.ToNurbsCurve()
                if nurbs:
                    hatch_edges.append(nurbs)

    moved_ids = []
    for cid in C:
        c_obj = sc.doc.Objects.Find(cid)
        if not c_obj: continue
        c_geom = c_obj.Geometry
        points = sample_curve_points(c_geom, num_points)

        for edge in hatch_edges:
            edge_domain = edge.Domain
            all_on_edge = True
            for pt in points:
                # ClosestPoint gibt (found, t)
                found, t = edge.ClosestPoint(pt)
                if not found:
                    all_on_edge = False
                    break
                closest_pt = edge.PointAt(t)
                if closest_pt.DistanceTo(pt) > tol:
                    all_on_edge = False
                    break
                if t < edge_domain.T0 - tol or t > edge_domain.T1 + tol:
                    all_on_edge = False
                    break

            if all_on_edge:
                rs.ObjectLayer(cid, deleted_layer)
                moved_ids.append(cid)
                break

    print("Verschoben:", len(moved_ids), "Kurven auf Layer", deleted_layer)

move_curves_if_fully_on_hatch_edge()
