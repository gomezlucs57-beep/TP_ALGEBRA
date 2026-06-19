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
import pandas as pd
import numpy as np


# =========================
# COSTOS
# =========================

def calcular_costos(
    consumo_wh,
    precio_kwh
):

    kwh = consumo_wh / 1000

    diario = kwh * precio_kwh

    mensual = diario * 30

    anual = mensual * 12

    return {

        "dia":
        f"${diario:,.0f}",

        "mes":
        f"${mensual:,.0f}",

        "anio":
        f"${anual:,.0f}"

    }


# =========================
# HISTORIAL
# =========================

def generar_historial(
    consumo_actual
):

    meses = [

        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",

        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre"

    ]

    np.random.seed(42)

    variacion = np.random.uniform(
        0.85,
        1.15,
        12
    )

    valores = [

        consumo_actual
        *
        v

        for v

        in variacion

    ]

    historial = pd.DataFrame({

        "Mes":
        meses,

        "Consumo":
        valores

    })

    return historial


# =========================
# RESUMEN
# =========================

def obtener_resumen(
    historial
):

    mayor = historial[
        "Consumo"
    ].max()

    menor = historial[
        "Consumo"
    ].min()

    promedio = historial[
        "Consumo"
    ].mean()

    return {

        "maximo":
        round(
            mayor
        ),

        "minimo":
        round(
            menor
        ),

        "promedio":
        round(
            promedio
        )

    }


# =========================
# COMPARACIÓN
# =========================

def variacion_mensual(
    historial
):

    hist = historial.copy()

    hist[
        "Variación %"
    ] = (

        hist[
            "Consumo"
        ]

        .pct_change()

        *100

    )

    hist = hist.fillna(
        0
    )

    return hist
    import pandas as pd


# ==========================
# RECOMENDACIONES
# ==========================

def generar_recomendaciones(
    tabla
):

    recomendaciones = []

    if len(tabla) == 0:

        return [
            "No hay datos suficientes."
        ]

    consumo_col = "Consumo Diario"

    # --------------------------
    # Mayor consumidor
    # --------------------------

    mayor = tabla.loc[
        tabla[
            consumo_col
        ].idxmax()
    ]

    recomendaciones.append(

        (
            f"Mayor consumo: "
            f"{mayor['Equipo']} "
            f"({mayor[consumo_col]:.0f} Wh/día)"
        )

    )

    # --------------------------
    # Uso elevado
    # --------------------------

    promedio = tabla[
        consumo_col
    ].mean()

    altos = tabla[
        tabla[
            consumo_col
        ]
        >
        promedio * 1.5
    ]

    if len(altos):

        recomendaciones.append(

            "Hay equipos con consumo elevado. "
            "Evaluá reducir horas de uso."

        )

    # --------------------------
    # Aire acondicionado
    # --------------------------

    aire = tabla[

        tabla[
            "Equipo"
        ]

        .str.contains(
            "aire",
            case=False,
            na=False
        )

    ]

    if len(aire):

        recomendaciones.append(

            "Reducir 1–2 horas del aire "
            "puede disminuir el consumo."

        )

    # --------------------------
    # Heladera
    # --------------------------

    heladera = tabla[

        tabla[
            "Equipo"
        ]

        .str.contains(
            "heladera",
            case=False,
            na=False
        )

    ]

    if len(heladera):

        recomendaciones.append(

            "Verificá temperatura y burletes "
            "de la heladera."

        )

    # --------------------------
    # Luces
    # --------------------------

    luces = tabla[

        tabla[
            "Equipo"
        ]

        .str.contains(
            "luz",
            case=False,
            na=False
        )

    ]

    if len(luces):

        recomendaciones.append(

            "Migrar a LED suele reducir "
            "el consumo de iluminación."

        )

    # --------------------------
    # Estado
    # --------------------------

    apagados = tabla[
        tabla[
            "Estado"
        ]
        ==
        "Apagado"
    ]

    if len(apagados):

        recomendaciones.append(

            f"{len(apagados)} equipo(s) "
            f"quedaron fuera del límite energético."

        )

    # --------------------------
    # Aprovechamiento
    # --------------------------

    total = tabla[
        consumo_col
    ].sum()

    if total < 3000:

        recomendaciones.append(

            "El consumo total es bajo. "
            "Existe margen disponible."

        )

    elif total > 10000:

        recomendaciones.append(

            "Consumo alto. "
            "Conviene revisar hábitos."

        )

    return recomendaciones


# ==========================
# SCORE EFICIENCIA
# ==========================

def score_eficiencia(
    tabla
):

    total = tabla[
        "Consumo Diario"
    ].sum()

    if total < 3000:

        return (
            90,
            "Excelente"
        )

    elif total < 6000:

        return (
            75,
            "Buena"
        )

    elif total < 10000:

        return (
            55,
            "Media"
        )

    else:

        return (
            35,
            "Mejorable"
        )
        from io import BytesIO
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)

from reportlab.lib import colors


# ==========================
# PDF
# ==========================

def generar_pdf(
    tabla,
    costos
):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer
    )

    estilos = (
        getSampleStyleSheet()
    )

    contenido = []

    # ------------------
    # TITULO
    # ------------------

    contenido.append(

        Paragraph(

            "Informe Energético",

            estilos[
                "Title"
            ]

        )

    )

    contenido.append(

        Spacer(
            1,
            20
        )

    )

    contenido.append(

        Paragraph(

            (
                "Fecha: "
                +
                datetime
                .now()
                .strftime(
                    "%d/%m/%Y"
                )
            ),

            estilos[
                "Normal"
            ]

        )

    )

    contenido.append(

        Spacer(
            1,
            20
        )

    )

    # ------------------
    # COSTOS
    # ------------------

    contenido.append(

        Paragraph(

            "Resumen Económico",

            estilos[
                "Heading1"
            ]

        )

    )

    contenido.append(

        Paragraph(

            (
                f"Costo diario: {costos['dia']}<br/>"
                f"Costo mensual: {costos['mes']}<br/>"
                f"Costo anual: {costos['anio']}"
            ),

            estilos[
                "Normal"
            ]

        )

    )

    contenido.append(

        Spacer(
            1,
            25
        )

    )

    # ------------------
    # TABLA
    # ------------------

    contenido.append(

        Paragraph(

            "Detalle por Equipo",

            estilos[
                "Heading1"
            ]

        )

    )

    datos = [

        list(
            tabla.columns
        )

    ]

    datos.extend(

        tabla
        .values
        .tolist()

    )

    tabla_pdf = Table(
        datos
    )

    tabla_pdf.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0,0),
                (-1,0),
                colors.darkblue
            ),

            (
                "TEXTCOLOR",
                (0,0),
                (-1,0),
                colors.white
            ),

            (
                "GRID",
                (0,0),
                (-1,-1),
                1,
                colors.black
            ),

            (
                "PADDING",
                (0,0),
                (-1,-1),
                8
            ),

            (
                "VALIGN",
                (0,0),
                (-1,-1),
                "TOP"
            )

        ])

    )

    contenido.append(
        tabla_pdf
    )

    contenido.append(

        Spacer(
            1,
            30
        )

    )

    # ------------------
    # PIE
    # ------------------

    contenido.append(

        Paragraph(

            (
                "Este reporte fue generado "
                "automáticamente."
            ),

            estilos[
                "Italic"
            ]

        )

    )

    # construir

    doc.build(
        contenido
    )

    buffer.seek(
        0
    )

    return buffer
    
