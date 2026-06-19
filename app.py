```python
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.optimize import milp, LinearConstraint, Bounds

from analytics import (
    calcular_costos,
    generar_historial
)

from recommendations import (
    generar_recomendaciones
)

from pdf_report import (
    generar_pdf
)

st.set_page_config(
    page_title="Gestión Energética",
    layout="wide"
)

st.title("⚡ Gestión Energética Inteligente")

# --------------------
# CONFIG
# --------------------

c1, c2, c3 = st.columns(3)

with c1:

    energia = st.number_input(
        "Energía disponible (Wh)",
        value=12000
    )

with c2:

    precio = st.number_input(
        "Precio kWh",
        value=150.0
    )

with c3:

    cantidad = st.number_input(
        "Cantidad equipos",
        value=6,
        min_value=1
    )

# --------------------
# EQUIPOS
# --------------------

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

st.subheader("Equipamiento")

cols = st.columns(3)

for i in range(int(cantidad)):

    with cols[i % 3]:

        base = (
            equipos[i]
            if i < len(equipos)
            else (
                f"Equipo {i+1}",
                100,
                8,
                5
            )
        )

        with st.expander(
            f"⚙️ {base[0]}"
        ):

            nombre = st.text_input(
                "Equipo",
                value=base[0],
                key=f"n{i}"
            )

            cantidad_ap = st.number_input(
                "Cantidad",
                1,
                key=f"c{i}"
            )

            watts = st.number_input(
                "W",
                value=base[1],
                key=f"w{i}"
            )

            horas = st.slider(
                "Horas",
                1,
                24,
                base[2],
                key=f"h{i}"
            )

            prioridad = st.slider(
                "Prioridad",
                1,
                10,
                base[3],
                key=f"p{i}"
            )

            consumo = (
                cantidad_ap
                *
                watts
                *
                horas
            )

            st.metric(
                "Wh diarios",
                f"{consumo}"
            )

            nombres.append(
                nombre
            )

            consumos.append(
                consumo
            )

            prioridades.append(
                prioridad
            )

# --------------------
# OPTIMIZACIÓN
# --------------------

c = [-x for x in prioridades]

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

if res.success:

    activos = np.round(
        res.x
    )

    usados = [

        e*a

        for e,a

        in zip(
            consumos,
            activos
        )

    ]

    total = sum(
        usados
    )

    tabla = pd.DataFrame({

        "Equipo":
        nombres,

        "Consumo Diario":
        consumos,

        "Estado":[

            "Activo"

            if x

            else "Apagado"

            for x

            in activos

        ]

    })

    tabla = tabla[
        tabla["Equipo"]
        .str.strip()
        != ""
    ]

    costo = calcular_costos(
        total,
        precio
    )

    st.divider()

    a,b,c = st.columns(3)

    a.metric(
        "Diario",
        costo["dia"]
    )

    b.metric(
        "Mensual",
        costo["mes"]
    )

    c.metric(
        "Anual",
        costo["anio"]
    )

    st.subheader(
        "Resumen"
    )

    st.dataframe(
        tabla,
        use_container_width=True
    )

    fig = px.line(

        tabla,

        x="Equipo",

        y="Consumo Diario",

        markers=True

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "Historial"
    )

    hist = generar_historial(
        total
    )

    st.line_chart(
        hist
    )

    st.subheader(
        "Recomendaciones"
    )

    for r in generar_recomendaciones(
        tabla
    ):

        st.info(
            r
        )

    pdf = generar_pdf(
        tabla,
        costo
    )

    st.download_button(

        "📄 Descargar PDF",

        pdf,

        "reporte.pdf"

    )
```
