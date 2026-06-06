import streamlit as st
import itertools


def wohnungsteilung(module_sizes, total_area, max_residual):
    """
    Gibt eine Liste möglicher Wohnungsaufteilungen mit Restfläche zurück.
    """
    max_units_per_module = 10
    ranges = [range(0, max_units_per_module + 1) for _ in module_sizes]

    results = []

    for combo in itertools.product(*ranges):
        area = sum(n * size for n, size in zip(combo, module_sizes))
        residual = total_area - area

        if 0 <= residual <= max_residual:
            results.append((combo, residual))

    return results


def mix_distance(combo, target_mix):
    total_units = sum(combo)

    if total_units == 0:
        return float("inf")

    actual_mix = [n / total_units for n in combo]

    return sum(
        abs(a - t)
        for a, t in zip(actual_mix, target_mix)
    )


# --- Streamlit Interface ---

st.title("🏠 Automatische Wohnungsaufteilung")

st.text(
    "Tool zur Variantenfindung für Wohnungszuschnitte auf Basis von Modulgrößen."
)

modul_text = st.text_input(
    "Erlaubte Modulgrößen (z. B. 62, 85, 108, 136)",
    value="62, 85, 108, 136"
)

mix_text = st.text_input(
    "Ziel-Wohnungsmix in % (z. B. 25, 25, 25, 25)",
    value="20, 20, 30, 30"
)

total_area = st.number_input(
    "Gesamtfläche des Geschosses (m²)",
    min_value=10.0,
    value=288.0,
    step=10.0
)

max_residual = st.number_input(
    "Maximal erlaubte Restfläche (m²)",
    min_value=0.0,
    value=10.0,
    step=1.0
)

if st.button("Berechnen"):
    try:
        module_sizes = [float(x.strip()) for x in modul_text.split(",")]
        mix_target = [float(x.strip()) for x in mix_text.split(",")]
    except ValueError:
        st.error("Ungültige Eingaben bei Modulgrößen oder Mix.")
    else:
        results = wohnungsteilung(module_sizes, total_area, max_residual)

        if not results:
            st.warning("Keine passende Kombination gefunden.")
        else:
            # Sortierung: zuerst Mix-Abweichung, dann Restfläche
            results.sort(
                key=lambda x: (
                    mix_distance(x[0], mix_target),
                    x[1]
                )
            )

            st.success(f"{len(results)} Kombination(en) gefunden:")

            for combo, residual in results[:10]:
                total_units = sum(combo)

                module_list = [
                    f"{n} × {int(size)} m²"
                    for n, size in zip(combo, module_sizes)
                    if n > 0
                ]

                st.markdown(
                    f"- {' + '.join(module_list)} "
                    f"→ Rest: {int(residual)} m²"
                )