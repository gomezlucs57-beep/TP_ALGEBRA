import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from scipy.optimize import milp, LinearConstraint, Bounds

# ======================
# CONFIG
# ======================

st.set_page_config(
    page_title="Distribución de Energía",
    layout="centered"
)

# ======================
# COLOR DINÁMICO
# ======================

def color_consumo(porcentaje):

    rojo = int(255 * porcentaje)
    verde = int(255 * (1 - porcentaje))

    return f"""
    <style>

    .stApp {{
        background:
        rgb(
            {255-rojo},
            {verde},
            230
        );

        transition:
        background 1s ease;
    }}

    div[data-testid="stMetric"] {{
        transition:
        all 0.5s;
    }}

    </style>
    """

# ======================
# DATOS
# ======================

energia_total = st.number_input(
    "⚡ Energía disponible",
    value=1200
)

st.subheader("Subsistemas")

cantidad = st.number_input(
    "Cantidad de subsistemas",
    min_value=3,
    value=3
)

nombres = []
rendimientos = []
minimos = []
maximos = []

default = [
    "Procesamiento de Datos",
    "Comunicaciones",
    "Almacenamiento"
]

default_r = [10, 8, 6]
default_min = [250, 200, 150]
default_max = [600, 99999, 99999]

for i in range(cantidad):

    with st.expander(
        f"Subsistema {i+1}",
        expanded=i < 3
    ):

        nombre = st.text_input(
            "Nombre",
            value=default[i]
            if i < 3
            else f"Sistema {i+1}"
        )

        rendimiento = st.number_input(
            "Rendimiento",
            value=default_r[i]
            if i < 3
            else 5,
            key=f"r{i}"
        )

        minimo = st.number_input(
            "Mínimo",
            value=default_min[i]
            if i < 3
            else 0,
            key=f"m{i}"
        )

        maximo = st.number_input(
            "Máximo",
            value=default_max[i]
            if i < 3
            else energia_total,
            key=f"x{i}"
        )

        nombres.append(nombre)
        rendimientos.append(rendimiento)
        minimos.append(minimo)
        maximos.append(maximo)

# ======================
# CÁLCULO AUTOMÁTICO
# ======================

c = [-x for x in rendimientos]

A = [np.ones(cantidad)]

bl = [-np.inf]
bu = [energia_total]

constraints = LinearConstraint(
    A,
    bl,
    bu
)

bounds = Bounds(
    minimos,
    maximos
)

res = milp(
    c=c,
    constraints=constraints,
    bounds=bounds,
    integrality=[0]*cantidad
)

# ======================
# RESULTADO
# ======================

if res.success:

    consumo = np.sum(res.x)

    porcentaje = min(
        consumo / energia_total,
        1
    )

    st.markdown(
        color_consumo(
            porcentaje
        ),
        unsafe_allow_html=True
    )

    st.success(
        "Resultado actualizado automáticamente"
    )

    st.metric(
        "Rendimiento Máximo",
        f"{-res.fun:.0f}"
    )

    tabla = pd.DataFrame({

        "Subsistema":
        nombres,

        "Energía":
        np.round(
            res.x,
            1
        )

    })

    st.dataframe(
        tabla,
        hide_index=True,
        use_container_width=True
    )

    # ======================
    # GRÁFICO PUNTO A PUNTO
    # ======================

    fig = px.line(

        tabla,

        x="Subsistema",

        y="Energía",

        markers=True,

        title="Distribución Energética"

    )

    fig.update_layout(

        transition_duration=800,

        height=350,

        margin=dict(
            l=20,
            r=20,
            t=40,
            b=20
        )
    )

    fig.update_traces(
        line_shape="linear"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.error(
        "No existe una distribución válida."
    )
