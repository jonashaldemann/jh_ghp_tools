import Rhino
import System
import ghpythonlib.components as gh


def schatten(brep, time):
    """
    Berechnet den Schatten eines Objektes B zu einer bestimmten Zeit t.

    Args:
        brep: Das Objekt, dessen Schatten berechnet werden soll.
        time: Zeit in Stunden (z.B. 8.0 für 08:00 Uhr).

    Returns:
        tuple: Ein Tupel bestehend aus dem Schattenvektor und den berechneten Schattenflächen.
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
    stundenserie = [time + i * step for i in range(int(stunden / step) + 1)]

    # Plane and point for projection
    pt = gh.ConstructPoint(0, 0, 0)
    pl = gh.XYPlane(pt)

    h = int(time)
    m = int((time - h) * 60)

    # Bern, MEZ UTC+1
    latitude = 46.9481
    longitude = 7.4474
    timezone = 1.0
    datetime = System.DateTime(2025, 10, 29, h, m, 0, System.DateTimeKind.Unspecified)

    sun.Longitude = longitude
    sun.Latitude = latitude
    sun.Timezone = timezone
    sun.SetDateTime(datetime, datetime.Kind)

    vec = sun.Vector
    projected_brep = gh.ProjectAlong(brep, pl, vec)[0]
    regions = gh.DeconstructBrep(projected_brep)[0]
    surface = gh.RegionUnion(regions)

    return vec, surface
