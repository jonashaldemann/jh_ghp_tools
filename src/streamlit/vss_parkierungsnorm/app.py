import math
import streamlit as st
import plotly.graph_objects as go
import ezdxf


def vss_parkierungsnorm(Gv, W, Pf, U, V):
    parkfeldlaenge = 5.00
    winkel_rad = math.radians(90 - W)

    d_pf = {
        90: {
            2.50: 6.50,
            2.55: 6.25,
            2.60: 6.00,
            2.65: 5.75,
            2.70: 5.50,
            2.75: 5.25,
            2.80: 5.00,
        },
        75: {2.50: 5.00, 2.65: 4.50},
        70: {2.50: 4.50, 2.70: 4.00},
        60: {2.50: 3.50, 2.80: 3.20},
        45: {2.50: 3.20},
        30: {2.50: 3.20},
    }

    fahrgasse = d_pf.get(W, {}).get(Pf, 0)
    if not fahrgasse:
        raise ValueError(
            f"Für Winkel {W}° und Parkfeldbreite {Pf} m ist kein Fahrgassenwert definiert."
        )
    if Gv and fahrgasse < 5.50:
        fahrgasse = 5.50

    reihenversatz = parkfeldlaenge * math.sin(winkel_rad)
    x_versatz = parkfeldlaenge * math.cos(winkel_rad)
    versatz_y = [(i // 2) * reihenversatz for i in range(U)]
    fahrgassenzuschlag = Pf * math.sin(winkel_rad)

    series_u = []
    wert = 0
    for i in range(U):
        series_u.append(wert)
        wert += x_versatz + (fahrgasse + fahrgassenzuschlag if i % 2 == 0 else 0)

    shift = Pf / math.cos(winkel_rad)
    series_v = [i * shift for i in range(V)]

    points = []
    for i, u in enumerate(series_u):
        y_offset = versatz_y[i]
        for v in series_v:
            points.append((u, v + y_offset))

    def rectangle_points(x, y, length, width, angle_rad):
        pts = [
            (0, 0),
            (length, 0),
            (length, width),
            (0, width),
        ]
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        rotated = []
        for px, py in pts:
            rx = cos_a * px - sin_a * py + x
            ry = sin_a * px + cos_a * py + y
            rotated.append((rx, ry))
        return rotated

    Geo = [rectangle_points(x, y, parkfeldlaenge, Pf, winkel_rad) for x, y in points]

    Info = f"Fahrgasse = {fahrgasse:.2f} m"
    return Geo, Info


def plot_parking(Geo):
    fig = go.Figure()
    for poly in Geo:
        x, y = zip(*poly)
        x = list(x) + [x[0]]
        y = list(y) + [y[0]]
        fig.add_trace(
            go.Scatter(x=x, y=y, fill="toself", mode="lines", line_color="blue")
        )
    fig.update_layout(
        width=700,
        height=500,
        title="Parkierung nach VSS-Norm",
        xaxis_title="Meter",
        yaxis_title="Meter",
        yaxis=dict(scaleanchor="x", scaleratio=1),
        showlegend=False,
    )
    return fig


def export_dxf(Geo, filename="parkierung.dxf"):
    import ezdxf

    doc = ezdxf.new()
    msp = doc.modelspace()
    for poly in Geo:
        points = [(x, y) for x, y in poly]
        points.append(points[0])
        msp.add_lwpolyline(points, close=True)
    doc.saveas(filename)


st.title("Parkierung nach VSS-Norm")

with st.form("params"):
    Gv = st.checkbox("Gegenverkehr berücksichtigen", value=True)
    W = st.selectbox(
        "Winkel der Parkplätze (Grad)", options=[90, 75, 70, 60, 45, 30], index=0
    )
    Pf = st.selectbox(
        "Breite eines Parkfeldes (m)",
        options=[2.50, 2.55, 2.60, 2.65, 2.70, 2.75, 2.80],
        index=0,
    )
    U = st.number_input("Anzahl Parkreihen (U)", min_value=1, max_value=20, value=5)
    V = st.number_input(
        "Anzahl Parkplätze pro Reihe (V)", min_value=1, max_value=20, value=10
    )
    submit = st.form_submit_button("Berechnen")

if submit:
    try:
        Geo, info = vss_parkierungsnorm(Gv, W, Pf, U, V)
        fig = plot_parking(Geo)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"**{info}**")

        export_dxf(Geo, "parkierung.dxf")
        with open("parkierung.dxf", "rb") as f:
            st.download_button("Download DXF", f, file_name="parkierung.dxf")
    except ValueError as e:
        st.error(str(e))
        d_pf = {
            90: [2.50, 2.55, 2.60, 2.65, 2.70, 2.75, 2.80],
            75: [2.50, 2.65],
            70: [2.50, 2.70],
            60: [2.50, 2.80],
            45: [2.50],
            30: [2.50],
        }
        mögliche_breiten = d_pf.get(W, [])
        if mögliche_breiten:
            st.markdown(
                f"Mögliche Parkfeldbreiten für Winkel **{W}°**: {', '.join(f'{w:.2f} m' for w in mögliche_breiten)}"
            )
        else:
            st.warning("Keine definierten Werte für diesen Winkel.")
