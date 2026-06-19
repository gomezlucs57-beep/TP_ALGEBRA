import streamlit as st
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

st.set_page_config(
    page_title="Optimización Lineal",
    page_icon="📈",
    layout="centered"
)

st.title("📈 Optimizador de Programación Lineal")

st.markdown("""
### Problema

Maximizar:

**F = 25x + 50y**

Sujeto a:

- x + y ≤ 90
- 4x + 6y ≥ 390
- 15x + 40y ≤ 2000
- x, y ≥ 0
""")

tipo_variables = st.radio(
    "Tipo de variables",
    ["Continuas", "Enteras"]
)

if st.button("Resolver problema"):

    # Función objetivo (negativa porque milp minimiza)
    c = [-25, -50]

    # Matriz de restricciones
    A = [
        [1, 1],
        [4, 6],
        [15, 40]
    ]

    # Límites inferior y superior
    bl = [-np.inf, 390, -np.inf]
    bu = [90, np.inf, 2000]

    constraints = LinearConstraint(A, bl, bu)

    bounds = Bounds(
        [0, 0],
        [np.inf, np.inf]
    )

    # 0 = continua, 1 = entera
    integrality = [0, 0]

    if tipo_variables == "Enteras":
        integrality = [1, 1]

    resultado = milp(
        c=c,
        constraints=constraints,
        bounds=bounds,
        integrality=integrality
    )

    if resultado.success:

        st.success("Solución encontrada")

        x = resultado.x[0]
        y = resultado.x[1]
        f = -resultado.fun

        col1, col2, col3 = st.columns(3)

        col1.metric("x", f"{x:.2f}")
        col2.metric("y", f"{y:.2f}")
        col3.metric("F(x,y)", f"{f:.2f}")

        st.subheader("Vector solución")
        st.write(resultado.x)

        st.subheader("Estado")
        st.info(resultado.message)

    else:
        st.error("No se encontró una solución factible.")
        st.write(resultado.message)
