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

st.title("⚡ Calculadora de Consumo Energético")

st.caption(
    "Ingresá los equipos del lugar y el sistema calcula automáticamente."
)

# ======================
# CONFIG GENERAL
# ======================

col1, col2, col3 = st.columns(3)

with col1:

    energia = st.number_input(
        "Energía disponible (Wh)",
        min_value=100,
        value=12000
    )

with col2:

    cantidad = st.number_input(
        "Cantidad de equipos",
        min_value=1,
        value=6,
        step=1
    )

with col3:

    st.metric(
        "Cálculo",
        "Automático"
    )

# ======================
# DATOS BASE
# ======================

equipos = [

("Heladera",150,24,10),
("Luces",80,8,8),
("Microondas",1200,1,6),
("Televisor",120,5,7),
("Aire acondicionado",1500,6,9),
("Notebook",90,8,7)

]

nombres=[]
consumos=[]
prioridades=[]

# ======================
# EQUIPAMIENTO
# ======================

st.subheader("Equipamiento")

columnas = st.columns(3)

for i in range(int(cantidad)):

    with columnas[i % 3]:

        nombre_default = (
            equipos[i][0]
            if i < len(equipos)
            else f"Equipo {i+1}"
        )

        with st.expander(
            f"⚙️ {nombre_default}",
            expanded=False
        ):

            nombre = st.text_input(
                "Nombre",
                value=nombre_default,
                key=f"n{i}"
            )

            cantidad_ap = st.number_input(
                "Cantidad",
                min_value=1,
                value=1,
                key=f"cant{i}"
            )

            watts = st.number_input(
                "Consumo por hora (W)",
                min_value=1,
                value=(
                    equipos[i][1]
                    if i < len(equipos)
                    else 100
                ),
                key=f"w{i}"
            )

            horas = st.slider(
                "Horas de uso",
                1,
                24,
                (
                    equipos[i][2]
                    if i < len(equipos)
                    else 8
                ),
                key=f"h{i}"
            )

            prioridad = st.slider(
                "Prioridad",
                1,
                10,
                (
                    equipos[i][3]
                    if i < len(equipos)
                    else 5
                ),
                key=f"p{i}"
            )

            consumo = (
                cantidad_ap
                * watts
                * horas
            )

            st.caption(
                f"Consumo estimado: {consumo:.0f} Wh"
            )

            nombres.append(
                nombre.strip()
            )

            consumos.append(
                consumo
            )

            prioridades.append(
                prioridad
            )

# ======================
# OPTIMIZACIÓN
# ======================

if len(consumos):

    try:

        c = [
            -x
            for x
            in prioridades
        ]

        A = [
            consumos
        ]

        constraints = LinearConstraint(
            A,
            [-np.inf],
            [energia]
        )

        bounds = Bounds(
            [0]*len(consumos),
            [1]*len(consumos)
        )

        res = milp(

            c=c,

            constraints=constraints,

            bounds=bounds,

            integrality=[1]*len(consumos)

        )

        st.divider()

        if res.success:

            activos = np.round(
                res.x
            )

            energia_usada = sum(

                c*a

                for c,a

                in zip(
                    consumos,
                    activos
                )

            )

            m1, m2, m3 = st.columns(3)

            with m1:

                st.metric(
                    "Usada",
                    f"{energia_usada:.0f} Wh"
                )

            with m2:

                st.metric(
                    "Disponible",
                    f"{energia-energia_usada:.0f} Wh"
                )

            with m3:

                st.metric(
                    "Uso",
                    f"{energia_usada/energia:.0%}"
                )

            tabla = pd.DataFrame({

                "Equipo":
                nombres,

                "Consumo (Wh)":
                consumos,

                "Estado":[

                    "Encendido"

                    if x

                    else "Apagado"

                    for x

                    in activos

                ]

            })

            # eliminar filas vacías
            tabla = tabla[
                tabla["Equipo"]
                .astype(str)
                .str.strip()
                != ""
            ]

            tabla = tabla.reset_index(
                drop=True
            )

            st.subheader(
                "Resultado"
            )

            st.dataframe(

                tabla,

                hide_index=True,

                use_container_width=True

            )

            # ======================
            # GRÁFICO
            # ======================

            fig = px.line(

                tabla,

                x="Equipo",

                y="Consumo (Wh)",

                markers=True

            )

            fig.update_layout(

                height=320,

                margin=dict(
                    l=10,
                    r=10,
                    t=20,
                    b=10
                ),

                xaxis=dict(
                    categoryorder="array"
                )

            )

            st.plotly_chart(

                fig,

                use_container_width=True

            )

        else:

            st.warning(
                "No existe una combinación válida."
            )

    except Exception as e:

        st.error(
            f"Error: {e}"
        )
