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
