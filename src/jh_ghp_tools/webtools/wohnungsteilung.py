import itertools
import streamlit as st

def wohnungsteilung(module_sizes, total_area, max_residual):
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

# Streamlit UI
st.title("Wohnungsteilung Optimierer")

sizes_input = st.text_input("Modulgrößen (z. B. 12, 20, 25)", "12, 20, 25")
area = st.number_input("Gesamtfläche (m²)", min_value=1, value=120)
residual = st.number_input("Maximale Restfläche (m²)", min_value=0, value=5)

if st.button("Berechnen"):
    try:
        sizes = [float(s.strip()) for s in sizes_input.split(",")]
        result = wohnungsteilung(sizes, area, residual)
        st.write(f"### Kombinationen mit max. {residual} m² Rest:")
        for combo, rest in result:
            parts = [f"{n} × {int(s)} m²" for n, s in zip(combo, sizes) if n > 0]
            st.write(f"{' + '.join(parts)} → **Rest: {int(rest)} m²**")
    except Exception as e:
        st.error(f"Fehler: {e}")
