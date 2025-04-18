import ghpythonlib.components as gh

def volumen_slicen(breps, h_eg, h_og, h_tot):
    schnitthoehe = 0.1
    storeys = int(h_tot / 2.5)
    
    # Planes for each Storey
    storey_base_heights = [schnitthoehe] + [h_eg + schnitthoehe + h_og * i for i in range(storeys)]
    pts = gh.ConstructPoint(0, 0, storey_base_heights)
    plns = gh.XYPlane(pts)

    # Intersection Curves
    x_curves = []
    for brep in breps:
        try:
            x_curve, _ = gh.BrepXPlane(brep, plns)
            for crv in x_curve:
                x_curves.append(crv)
        except:
            pass

    # Area Calculation
    areas, centroids = gh.Area(x_curves)
    area, _ = gh.MassAddition(areas)
    area = f"{round(area)} m²"

    # Extrude Curves
    extrusion_heights = []
    for pt in centroids:
        if pt.Z < schnitthoehe + 0.1:
            extrusion_heights.append(h_eg)
        else:
            extrusion_heights.append(h_og)
    vectors = gh.UnitZ(extrusion_heights)
    open_breps = gh.Extrude(x_curves, vectors)
    breps_new = gh.CapHoles(open_breps)

    return breps_new, area