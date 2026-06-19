import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.optimize import milp, LinearConstraint, Bounds

# ==================
# CONFIG
# ==================

st.set_page_config(
    page_title="Consumo Energético",
    layout="centered"
)

# ==================
# FONDO DINÁMICO
# ==================

def fondo(consumo):

    rojo = int(255 * consumo)
    verde = int(255 * (1 - consumo))

    st.markdown(f"""
    <style>

    .stApp {{
        background:
        rgb(
            {255-rojo},
            {verde},
            220
        );

        transition:1s;
    }}

    </style>
    """, unsafe_allow_html=True)


# ==================
# TÍTULO
# ==================

st.title("⚡ Consumo de Energía por Aparatos")

st.caption(
    "Ingresá los aparatos del lugar y el sistema calcula automáticamente."
)

energia = st.number_input(
    "Energía disponible (Wh)",
    value=12000
)

cantidad = st.number_input(
    "Cantidad de aparatos",
    min_value=1,
    value=5
)

# ==================
# APARATOS
# ==================

ejemplos = [

    ["Heladera",150,24,10],
    ["Luces",80,8,8],
    ["Microondas",1200,1,6],
    ["Televisor",120,5,7],
    ["Aire acondicionado",1500,6,9]

]

nombres=[]
consumos=[]
prioridades=[]

st.subheader("Equipamiento")

for i in range(cantidad):

    with st.expander(
        f"Aparato {i+1}",
        expanded=i < 3
    ):

        nombre = st.text_input(
            "Nombre",
            value=ejemplos[i][0]
            if i < len(ejemplos)
            else f"Aparato {i+1}"
        )

        cantidad_ap = st.number_input(
            "Cantidad",
            value=1,
            key=f"cant{i}"
        )

        watts = st.number_input(
            "Consumo (W)",
            value=ejemplos[i][1]
            if i < len(ejemplos)
            else 100,
            key=f"w{i}"
        )

        horas = st.slider(
            "Horas de uso",
            1,
            24,
            ejemplos[i][2]
            if i < len(ejemplos)
            else 8,
            key=f"h{i}"
        )

        prioridad = st.slider(
            "Importancia",
            1,
            10,
            ejemplos[i][3]
            if i < len(ejemplos)
            else 5,
            key=f"p{i}"
        )

        energia_ap = cantidad_ap * watts * horas

        nombres.append(nombre)
        consumos.append(energia_ap)

        prioridades.append(prioridad)

# ==================
# OPTIMIZACIÓN
# ==================

c = [-p for p in prioridades]

A = [consumos]

constraints = LinearConstraint(
    A,
    [-np.inf],
    [energia]
)

bounds = Bounds(
    [0]*cantidad,
    [1]*cantidad
)

res = milp(
    c=c,
    constraints=constraints,
    bounds=bounds,
    integrality=[1]*cantidad
)

# ==================
# RESULTADO
# ==================

if res.success:

    activos = np.round(res.x)

    usado = sum(
        c*v
        for c,v
        in zip(consumos,activos)
    )

    fondo(
        usado/energia
    )

    tabla = pd.DataFrame({

        "Aparato": nombres,

        "Consumo": consumos,

        "Activo": [
            "Sí"
            if x
            else "No"
            for x in activos
        ]

    })

    st.metric(
        "Energía utilizada",
        f"{usado:.0f} Wh"
    )

    st.metric(
        "Disponibilidad",
        f"{100*(1-usado/energia):.0f}%"
    )

    st.dataframe(
        tabla,
        hide_index=True,
        use_container_width=True
    )

    # GRÁFICO PUNTO A PUNTO

    graf = tabla.copy()

    graf["Consumo"] = graf["Consumo"].astype(float)

    fig = px.line(

        graf,

        x="Aparato",

        y="Consumo",

        markers=True

    )

    fig.update_layout(

        height=350,

        transition_duration=600

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.error(
        "La energía disponible no alcanza."
    )
