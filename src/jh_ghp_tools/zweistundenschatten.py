import Rhino
import System
import ghpythonlib.components as gh


def zweistundenschatten(B, start, end):
    """
    Berechnet den Schatten eines Objektes B in einem Zeitraum von 2 Stunden.

    Args:
        B: Das Objekt, dessen Schatten berechnet werden soll.
        start: Startzeit in Stunden (z.B. 8.0 für 08:00 Uhr).
        end: Endzeit in Stunden (z.B. 18.0 für 18:00 Uhr).

    Returns:
        schatten: Die berechneten Schattenflächen.
    """

    # Main Settings
    step = 1
    stunden = 2

    # Rothrist, MEZ UTC+1
    sun = Rhino.RhinoDoc.ActiveDoc.RenderSettings.Sun
    sun.Longitude = 7.8798
    sun.Latitude = 47.3063
    sun.Timezone = 1.0

    # Generate hourly series
    stundenserie = [start + i * step for i in range(int((end - start) / step) + 1)]
    pl = gh.XYPlane(gh.ConstructPoint(0, 0, 0))
    regions = []

    # Calculate shadow regions
    for t in stundenserie:
        h, m = divmod(int(t * 60), 60)
        datetime = System.DateTime(2025, 10, 29, h, m, 0, System.DateTimeKind.Unspecified)
        sun.SetDateTime(datetime, datetime.Kind)
        vec = sun.Vector
        brep = gh.ProjectAlong(B, pl, vec)[0]
        region = gh.DeconstructBrep(brep)[0]
        regions.append(gh.RegionUnion(region))

    # Find intersection points of shadows
    match_points = [pt for i in range(len(regions) - stunden) if regions[i] and regions[i + stunden] for pt in gh.MultipleCurves([regions[i], regions[i + stunden]])[0]]

    # Filter points outside the footprint
    distances = gh.BrepClosestPoint(match_points, B)[2]
    match_points_outer = [point for point, dist in zip(match_points, distances) if dist > 0.1]

    # Cut shadow polygons and calculate X-hour shadow
    split_crv = gh.PolyLine(match_points_outer, False)
    brep_centroid = gh.Volume(B)[1]
    surfaces = []
    for srf in regions[stunden:-stunden]:
        split = gh.SurfaceSplit(srf, split_crv)
        split_centroids = gh.Area(split)[1]
        distances = gh.Distance(split_centroids, brep_centroid)
        split_s = sorted(zip(split, distances), key=lambda x: x[1])
        surfaces.append(split_s[0][0])

    schatten = gh.BoundarySurfaces(gh.RegionUnion(surfaces))

    return regions, match_points_outer, schatten
