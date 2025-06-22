import streamlit as st
import math
import plotly.graph_objects as go
from shapely.geometry import LineString
import ezdxf
from io import BytesIO

def vss_rampe_im_schnitt(geschosshoehe, gefaelle):
    """
    Berechnet Rampe im 2D-Schnitt gemäss VSS mit einfacher Rundung.
    Rückgabe als LineString und Länge.
    """
    gefaelle_rad = math.atan(gefaelle / 100)

    # Punkte definieren
    p1 = (-20, 0)
    p2 = (0, 0)

    # Rampe (P2 -> P3)
    dx = geschosshoehe / math.tan(gefaelle_rad)
    p3 = (dx, -geschosshoehe)
    p4 = (dx + 20, -geschosshoehe)

    # Eckige Linie
    pts = [p1, p2, p3, p4]

    # Rundungen nur skizziert – hier: keine echte Fillet, sondern einfache Näherung
    # Für echte Rundungen → Bezier o.ä. oder CAD-Tools
    rampe = LineString(pts)
    laenge = p4[0] - p1[0]
    return rampe, laenge

def export_dxf(linestring):
    doc = ezdxf.new()
    msp = doc.modelspace()
    points = list(linestring.coords)
    for start, end in zip(points[:-1], points[1:]):
        msp.add_line(start, end)

    buffer = BytesIO()
    doc.write(buffer)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.set_page_config(page_title="VSS Rampe", layout="centered")
st.title("🛣️ VSS-Rampe im Schnitt")

st.sidebar.header("Parameter")
h = st.sidebar.number_input("Geschosshöhe [m]", min_value=0.1, max_value=6.0, value=3.2, step=0.1)
g = st.sidebar.number_input("Gefälle [%]", min_value=1.0, max_value=18.0, value=12.0, step=0.5)

rampe, laenge = vss_rampe_im_schnitt(h, g)

# Plotly Zeichnung
fig = go.Figure()
x, y = rampe.xy
fig.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", name="Rampe"))
fig.update_layout(
    title="Rampe im Schnitt (2D)",
    xaxis_title="X [m]",
    yaxis_title="Y [m]",
    width=800,
    height=400,
    yaxis_scaleanchor="x",
    template="simple_white"
)
st.plotly_chart(fig)

st.markdown(f"**Horizontale Rampenlänge:** {laenge:.2f} m")

# DXF Export
dxf_data = export_dxf(rampe)
st.download_button("📥 DXF herunterladen", dxf_data, file_name="rampe.dxf", mime="application/dxf")
