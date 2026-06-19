import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
import matplotlib.pyplot as plt

# ======================
# CONFIG PÁGINA
# ======================

st.set_page_config(
    page_title="Distribución Energía",
    layout="centered"
)

st.title("⚡ Distribución de Energía")

# ======================
# ENTRADAS COMPACTAS
# ======================

col1, col2 = st.columns(2)

with col1:
    energia_total = st.number_input(
        "Energía total",
        value=1200,
        step=50
    )

with col2:
    relacion = st.slider(
        "C mínimo respecto a P (%)",
        0,
        100,
        40
    )

factor = relacion / 100


st.markdown("### Rendimiento")

c1, c2, c3 = st.columns(3)

with c1:
    rend_P = st.number_input(
        "P",
        value=10
    )

with c2:
    rend_C = st.number_input(
        "C",
        value=8
    )

with c3:
    rend_A = st.number_input(
        "A",
        value=6
    )

# ======================
# RESTRICCIONES OCULTAS
# ======================

with st.expander("Restricciones"):

    c1, c2 = st.columns(2)

    with c1:
        min_P = st.number_input(
            "Mín P",
            value=250
        )

        min_C = st.number_input(
            "Mín C",
            value=200
        )

    with c2:
        min_A = st.number_input(
            "Mín A",
            value=150
        )

        max_P = st.number_input(
            "Máx P",
            value=600
        )

# ======================
# BOTÓN
# ======================

if st.button(
    "Optimizar",
    use_container_width=True
):

    c = [
        -rend_P,
        -rend_C,
        -rend_A
    ]

    A = [

        [1, 1, 1],
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

    constraints = LinearConstraint(
        A,
        bl,
        bu
    )

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

    if res.success:

        P, C, A = res.x

        st.success("Optimización completada")

        st.metric(
            "Rendimiento Máximo",
            f"{-res.fun:.0f}"
        )

        st.markdown("### Distribución")

        r1, r2, r3 = st.columns(3)

        r1.metric("P", f"{P:.0f}")
        r2.metric("C", f"{C:.0f}")
        r3.metric("A", f"{A:.0f}")

        # ======================
        # GRÁFICO CORREGIDO
        # ======================

        fig, ax = plt.subplots(
            figsize=(6, 3)
        )

        categorias = [
            "Procesamiento",
            "Comunicación",
            "Almacenamiento"
        ]

        valores = [P, C, A]

        ax.bar(
            categorias,
            valores
        )

        # enderezar números
        plt.xticks(
            rotation=0
        )

        ax.set_ylabel(
            "Unidades"
        )

        plt.tight_layout()

        st.pyplot(fig)

    else:

        st.error(
            "No existe solución."
        )
