# ======================
# EQUIPAMIENTO
# ======================

st.subheader("Equipamiento")

equipos_default = [

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

for i in range(cantidad):

    nombre_default = (
        equipos_default[i][0]
        if i < len(equipos_default)
        else f"Aparato {i+1}"
    )

    with st.expander(
        f"⚙️ {nombre_default}",
        expanded=False
    ):

        c1, c2, c3 = st.columns(3)

        with c1:

            nombre = st.text_input(
                "Nombre",
                value=nombre_default,
                key=f"n{i}"
            )

            cantidad_ap = st.number_input(
                "Cantidad",
                value=1,
                min_value=1,
                key=f"c{i}"
            )

        with c2:

            watts = st.number_input(
                "Consumo (W)",
                value=(
                    equipos_default[i][1]
                    if i < len(equipos_default)
                    else 100
                ),
                key=f"w{i}"
            )

            horas = st.number_input(
                "Horas uso",
                value=(
                    equipos_default[i][2]
                    if i < len(equipos_default)
                    else 8
                ),
                min_value=1,
                max_value=24,
                key=f"h{i}"
            )

        with c3:

            prioridad = st.slider(
                "Prioridad",
                1,
                10,
                (
                    equipos_default[i][3]
                    if i < len(equipos_default)
                    else 5
                ),
                key=f"p{i}"
            )

            consumo_total = (
                cantidad_ap
                * watts
                * horas
            )

            st.metric(
                "Consumo",
                f"{consumo_total:.0f} Wh"
            )

        nombres.append(nombre)

        consumos.append(
            consumo_total
        )

        prioridades.append(
            prioridad
        )
