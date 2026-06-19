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
