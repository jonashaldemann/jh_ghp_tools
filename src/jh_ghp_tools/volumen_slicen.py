import ghpythonlib.components as gh
import Rhino.Geometry as rg


import Rhino.Geometry as rg


import Rhino.Geometry as rg


def volumen_slicen(breps, h_eg, h_og, top_on=True):
    schnitthoehe = 0.01

    all_curves = []
    all_areas = []
    tabelle = []

    for idx, brep in enumerate(breps):

        bbox = brep.GetBoundingBox(True)
        z0 = bbox.Min.Z
        z_max = bbox.Max.Z

        # Geschosse innerhalb der Bounding Box erzeugen
        storey_heights = [z0 + schnitthoehe]

        current_height = z0 + h_eg + schnitthoehe

        while current_height < z_max:
            storey_heights.append(current_height)
            current_height += h_og

        # Oberstes Geschoss optional entfernen
        if not top_on and len(storey_heights) > 1:
            storey_heights = storey_heights[:-1]

        planes = [
            rg.Plane(rg.Point3d(0, 0, height), rg.Vector3d.ZAxis)
            for height in storey_heights
        ]

        storey_names = ["EG"] + [
            f"OG{i}" for i in range(1, len(storey_heights))
        ]

        brep_areas = []

        for plane, storey_name in zip(planes, storey_names):

            curves = rg.Brep.CreateContourCurves(brep, plane)

            if not curves:
                brep_areas.append(0.0)
                continue

            area_sum = 0.0

            for curve in curves:
                props = rg.AreaMassProperties.Compute(curve)
                if props:
                    area_sum += props.Area

            brep_areas.append(area_sum)

            if area_sum > 0:
                tabelle.append(
                    f"Brep{idx} {storey_name} {int(area_sum)} m²"
                )

            all_curves.extend(curves)

        all_areas.append(sum(brep_areas))

    total_area = sum(all_areas)
    total_area_str = f"ist {round(total_area)} m²"

    return all_curves, total_area_str, tabelle