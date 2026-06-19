import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.optimize import milp, LinearConstraint, Bounds

# ======================
# CONFIG
# ======================

st.set_page_config(
    page_title="Consumo Energético",
    layout="wide"
)

st.title("⚡ Consumo Energético del Lugar")

# ======================
# CONFIG GENERAL
# ======================

c1, c2, c3 = st.columns(3)

with c1:
    energia = st.number_input(
        "Energía disponible (Wh)",
        value=12000
    )

with c2:
    cantidad = st.number_input(
        "Cantidad de aparatos",
        min_value=1,
        value=6
    )

with c3:
    st.metric(
        "Modo",
        "Automático"
    )

# ======================
# APARATOS
# ======================

ejemplos = [

["Heladera",150,24,10],
["Luces",80,8,8],
["Microondas",1200,1,6],
["Televisor",120,5,7],
["Aire acondicionado",1500,6,9],
["Notebook",90,8,7]

]

nombres=[]
consumos=[]
prioridades=[]

st.subheader("Equipamiento")

# 3 columnas visuales
columnas = st.columns(3)

for i in range(cantidad):

    col = columnas[i % 3]

    with col:

        st.markdown(
            f"**Aparato {i+1}**"
        )

        nombre = st.text_input(
            "Nombre",
            value=(
                ejemplos[i][0]
                if i < len(ejemplos)
                else f"Aparato {i+1}"
            ),
            key=f"n{i}"
        )

        cantidad_ap = st.number_input(
            "Cantidad",
            value=1,
            key=f"c{i}"
        )

        watts = st.number_input(
            "Consumo (W)",
            value=(
                ejemplos[i][1]
                if i < len(ejemplos)
                else 100
            ),
            key=f"w{i}"
        )

        horas = st.number_input(
            "Horas",
            value=(
                ejemplos[i][2]
                if i < len(ejemplos)
                else 8
            ),
            key=f"h{i}"
        )

        prioridad = st.slider(
            "Prioridad",
            1,
            10,
            (
                ejemplos[i][3]
                if i < len(ejemplos)
                else 5
            ),
            key=f"p{i}"
        )

        consumo = (
            cantidad_ap
            * watts
            * horas
        )

        nombres.append(nombre)
        consumos.append(consumo)
        prioridades.append(prioridad)

# ======================
# OPTIMIZACIÓN AUTOMÁTICA
# ======================

c = [-x for x in prioridades]

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

# ======================
# RESULTADOS
# ======================

st.divider()

if res.success:

    activos = np.round(res.x)

    energia_usada = sum(
        e*a
        for e,a
        in zip(
            consumos,
            activos
        )
    )

    r1, r2, r3 = st.columns(3)

    with r1:
        st.metric(
            "Energía usada",
            f"{energia_usada:.0f} Wh"
        )

    with r2:
        st.metric(
            "Disponible",
            f"{energia-energia_usada:.0f} Wh"
        )

    with r3:
        st.metric(
            "Uso",
            f"{energia_usada/energia:.0%}"
        )

    tabla = pd.DataFrame({

        "Aparato": nombres,

        "Consumo": consumos,

        "Estado": [

            "Encendido"
            if x
            else "Apagado"

            for x in activos
        ]

    })

    st.dataframe(
        tabla,
        hide_index=True,
        use_container_width=True
    )

    # gráfico punto a punto

    fig = px.line(

        tabla,

        x="Aparato",

        y="Consumo",

        markers=True

    )

    fig.update_layout(

        height=300,

        margin=dict(
            l=10,
            r=10,
            t=30,
            b=10
        ),

        transition_duration=400

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.error(
        "La energía disponible no alcanza."
    )
