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
