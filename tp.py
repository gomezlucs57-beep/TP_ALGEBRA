import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
import matplotlib.pyplot as plt

# ==========================
# CONFIGURACIÓN
# ==========================

st.set_page_config(
    page_title="Distribución de Energía",
    layout="centered"
)

st.title("⚡ Optimización de Distribución de Energía")

st.caption(
    "Ingresá los parámetros y el sistema calculará automáticamente la mejor distribución."
)

# ==========================
# ENERGÍA TOTAL
# ==========================

energia_total = st.number_input(
    "Energía disponible",
    min_value=0,
    value=1200,
    help="Cantidad total de energía para repartir."
)

# ==========================
# RENDIMIENTO
# ==========================

st.subheader("Rendimiento por unidad de energía")

c1, c2, c3 = st.columns(3)

with c1:
    rendimiento_procesamiento = st.number_input(
        "Procesamiento de Datos",
        value=10
    )

with c2:
    rendimiento_comunicaciones = st.number_input(
        "Comunicaciones",
        value=8
    )

with c3:
    rendimiento_almacenamiento = st.number_input(
        "Almacenamiento",
        value=6
    )

# ==========================
# RESTRICCIONES
# ==========================

with st.expander("Configuración avanzada"):

    st.markdown("### Energía mínima requerida")

    c1, c2, c3 = st.columns(3)

    with c1:
        min_procesamiento = st.number_input(
            "Procesamiento",
            value=250
        )

    with c2:
        min_comunicaciones = st.number_input(
            "Comunicaciones",
            value=200
        )

    with c3:
        min_almacenamiento = st.number_input(
            "Almacenamiento",
            value=150
        )

    max_procesamiento = st.number_input(
        "Máximo permitido para Procesamiento",
        value=600
    )

    porcentaje = st.slider(
        "Comunicaciones debe recibir al menos este porcentaje respecto a Procesamiento",
        0,
        100,
        40
    )

factor = porcentaje / 100


# ==========================
# CÁLCULO
# ==========================

if st.button("Calcular distribución óptima", use_container_width=True):

    c = [
        -rendimiento_procesamiento,
        -rendimiento_comunicaciones,
        -rendimiento_almacenamiento
    ]

    matriz = [

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
        matriz,
        bl,
        bu
    )

    bounds = Bounds(
        [
            min_procesamiento,
            min_comunicaciones,
            min_almacenamiento
        ],
        [
            max_procesamiento,
            np.inf,
            np.inf
        ]
    )

    resultado = milp(
        c=c,
        constraints=constraints,
        bounds=bounds,
        integrality=[0, 0, 0]
    )

    if resultado.success:

        procesamiento = resultado.x[0]
        comunicaciones = resultado.x[1]
        almacenamiento = resultado.x[2]

        st.success("Distribución calculada")

        st.metric(
            "Rendimiento máximo obtenido",
            f"{-resultado.fun:.0f}"
        )

        st.subheader("Asignación recomendada")

        tabla = pd.DataFrame({
            "Subsistema": [
                "Procesamiento de Datos",
                "Comunicaciones",
                "Almacenamiento"
            ],
            "Energía Asignada": [
                round(procesamiento),
                round(comunicaciones),
                round(almacenamiento)
            ]
        })

        st.dataframe(
            tabla,
            hide_index=True,
            use_container_width=True
        )

        # GRÁFICO MÁS SIMPLE

        fig, ax = plt.subplots(
            figsize=(8, 3)
        )

        nombres = [
            "Procesamiento",
            "Comunicaciones",
            "Almacenamiento"
        ]

        valores = [
            procesamiento,
            comunicaciones,
            almacenamiento
        ]

        ax.barh(
            nombres,
            valores
        )

        ax.set_xlabel(
            "Unidades de energía"
        )

        plt.tight_layout()

        st.pyplot(fig)

    else:

        st.error(
            "No existe una solución válida con esos parámetros."
        )
