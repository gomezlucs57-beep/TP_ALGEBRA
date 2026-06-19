import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.optimize import milp, LinearConstraint, Bounds

from io import BytesIO

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib import colors
from reportlab.lib.styles import (
    getSampleStyleSheet
)

# ======================
# CONFIG
# ======================

st.set_page_config(
    page_title="Consumo Energético",
    layout="wide"
)

st.title("⚡ Informe de Consumo Energético")

st.caption(
    "Ingresá los equipos y el sistema calcula automáticamente."
)

# ======================
# CONFIG GENERAL
# ======================

c1, c2, c3 = st.columns(3)

with c1:

    energia = st.number_input(
        "Energía disponible (Wh)",
        value=12000,
        min_value=100
    )

with c2:

    cantidad = st.number_input(
        "Cantidad de equipos",
        value=6,
        min_value=1
    )

with c3:

    st.metric(
        "Actualización",
        "Automática"
    )

# ======================
# EQUIPOS
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

st.subheader(
    "Equipamiento"
)

cols = st.columns(3)

for i in range(int(cantidad)):

    with cols[i % 3]:

        nombre_base = (

            equipos[i][0]

            if i < len(equipos)

            else f"Equipo {i+1}"

        )

        with st.expander(
            f"⚙️ {nombre_base}"
        ):

            nombre = st.text_input(

                "Nombre",

                value=nombre_base,

                key=f"n{i}"

            )

            cantidad_ap = st.number_input(

                "Cantidad",

                value=1,

                min_value=1,

                key=f"cant{i}"

            )

            watts = st.number_input(

                "Consumo por hora (W)",

                value=(
                    equipos[i][1]

                    if i < len(equipos)

                    else 100
                ),

                min_value=1,

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

            st.metric(
                "Consumo diario",
                f"{consumo:.0f} Wh"
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

if consumos:

    try:

        c = [

            -x

            for x

            in prioridades

        ]

        constraints = LinearConstraint(

            [consumos],

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

            usados = [

                c*a

                for c,a

                in zip(
                    consumos,
                    activos
                )

            ]

            energia_usada = sum(
                usados
            )

            tabla = pd.DataFrame({

                "Equipo":
                nombres,

                "Consumo Diario (Wh)":
                consumos,

                "Estado":[

                    "Encendido"

                    if x

                    else "Apagado"

                    for x

                    in activos

                ]

            })

            tabla = tabla[
                tabla["Equipo"]
                != ""
            ]

            tabla = tabla.reset_index(
                drop=True
            )

            tabla[
                "Consumo Mensual (Wh)"
            ] = (
                tabla[
                    "Consumo Diario (Wh)"
                ] * 30
            )

            m1,m2,m3=st.columns(3)

            with m1:

                st.metric(
                    "Diario",
                    f"{energia_usada:.0f} Wh"
                )

            with m2:

                st.metric(
                    "Mensual",
                    f"{tabla['Consumo Mensual (Wh)'].sum():.0f} Wh"
                )

            with m3:

                st.metric(
                    "Uso",
                    f"{energia_usada/energia:.0%}"
                )

            st.subheader(
                "Informe"
            )

            st.dataframe(

                tabla,

                use_container_width=True,

                hide_index=True

            )

            # gráfico

            fig = px.line(

                tabla,

                x="Equipo",

                y="Consumo Diario (Wh)",

                markers=True

            )

            fig.update_layout(
                height=300
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # ======================
            # PDF
            # ======================

            def crear_pdf(df):

                buffer = BytesIO()

                doc = SimpleDocTemplate(
                    buffer
                )

                estilos = (
                    getSampleStyleSheet()
                )

                contenido=[]

                contenido.append(

                    Paragraph(

                        "Informe Mensual",

                        estilos["Title"]

                    )

                )

                contenido.append(
                    Spacer(
                        1,
                        20
                    )
                )

                datos = [

                    list(
                        df.columns
                    )

                ]

                datos.extend(
                    df.values.tolist()
                )

                tabla_pdf = Table(
                    datos
                )

                tabla_pdf.setStyle(

                    TableStyle([

                        (
                            "GRID",

                            (0,0),

                            (-1,-1),

                            1,

                            colors.black

                        )

                    ])

                )

                contenido.append(
                    tabla_pdf
                )

                doc.build(
                    contenido
                )

                buffer.seek(0)

                return buffer

            pdf = crear_pdf(
                tabla
            )

            st.download_button(

                "📄 Descargar PDF",

                pdf,

                file_name="reporte_consumo.pdf",

                mime="application/pdf"

            )

        else:

            st.warning(
                "No existe combinación válida."
            )

    except Exception as e:

        st.error(
            str(e)
        )
