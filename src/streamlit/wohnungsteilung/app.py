import streamlit as st
import itertools


def wohnungsteilung(module_sizes, total_area, max_residual):
    """
    Gibt eine sortierte Liste möglicher Wohnungsaufteilungen mit Restfläche zurück.
    """
    max_units_per_module = 10
    ranges = [range(0, max_units_per_module + 1) for _ in module_sizes]

    results = []

    for combo in itertools.product(*ranges):
        area = sum(n * size for n, size in zip(combo, module_sizes))
        residual = total_area - area
        if 0 <= residual <= max_residual:
            results.append((combo, residual))

    results.sort(key=lambda x: x[1])
    return results


# --- Streamlit Interface ---

st.title("🏠 Automatische Wohnungsaufteilung")

modul_text = st.text_input(
    "Modulgrößen (z. B. 30, 50, 70)", value="30, 50, 70"
)

total_area = st.number_input(
    "Gesamtfläche des Geschosses (m²)", min_value=10.0, value=250.0, step=10.0
)

max_residual = st.number_input(
    "Maximal erlaubte Restfläche (m²)", min_value=0.0, value=5.0, step=1.0
)

if st.button("Berechnen"):
    try:
        module_sizes = [float(x.strip()) for x in modul_text.split(",")]
    except ValueError:
        st.error("Bitte gültige Zahlen für Modulgrößen eingeben (z. B. 30, 50, 70)")
    else:
        results = wohnungsteilung(module_sizes, total_area, max_residual)

        if not results:
            st.warning("Keine passende Kombination gefunden.")
        else:
            st.success(f"{len(results)} Kombination(en) gefunden:")
            for combo, residual in results[:10]:  # Nur die ersten 10 anzeigen
                module_list = [
                    f"{n} × {int(size)} m²"
                    for n, size in zip(combo, module_sizes)
                    if n > 0
                ]
                st.markdown(f"- {' + '.join(module_list)} → **Rest: {int(residual)} m²**")
