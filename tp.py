import streamlit as st
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

st.title("⚡ Optimización de Distribución de Energía")

st.write(
    "Modificá los parámetros y calculá la distribución óptima."
)

# ============================
# ENTRADAS DEL USUARIO
# ============================

energia_total = st.number_input(
    "Energía disponible",
    min_value=0,
    value=1200
)

st.subheader("Rendimiento por unidad")

rend_P = st.number_input(
    "Procesamiento (P)",
    value=10
)

rend_C = st.number_input(
    "Comunicaciones (C)",
    value=8
)

rend_A = st.number_input(
    "Almacenamiento (A)",
    value=6
)

st.subheader("Restricciones")

min_P = st.number_input(
    "Mínimo energía P",
    value=250
)

min_C = st.number_input(
    "Mínimo energía C",
    value=200
)

min_A = st.number_input(
    "Mínimo energía A",
    value=150
)

max_P = st.number_input(
    "Máximo energía P",
    value=600
)

relacion = st.slider(
    "C debe ser al menos (%) de P",
    min_value=0,
    max_value=100,
    value=40
)

factor = relacion / 100


# ============================
# BOTÓN CALCULAR
# ============================

if st.button("Calcular distribución"):

    c = [
        -rend_P,
        -rend_C,
        -rend_A
    ]

    A = [

        # Energía total
        [1, 1, 1],

        # C ≥ factor * P
        [factor, -1, 0]

    ]

    bl = [
        -np.inf,
        -np.inf
    ]

    bu = [
        energia_total,
        0
    ]

    constraints = LinearConstraint(A, bl, bu)

    bounds = Bounds(
        [min_P, min_C, min_A],
        [max_P, np.inf, np.inf]
    )

    res = milp(
        c=c,
        constraints=constraints,
        bounds=bounds,
        integrality=[0, 0, 0]
    )

    st.subheader("Resultados")

    if res.success:

        P = res.x[0]
        C = res.x[1]
        A = res.x[2]

        st.success("Optimización completada")

        st.metric(
            "Rendimiento máximo",
            round(-res.fun, 2)
        )

        st.write("### Distribución óptima")

        st.write(f"Procesamiento (P): {P:.2f}")
        st.write(f"Comunicaciones (C): {C:.2f}")
        st.write(f"Almacenamiento (A): {A:.2f}")

        st.bar_chart({
            "Energía": [P, C, A]
        })

    else:
        st.error(
            "No existe solución con esos parámetros."
        )
