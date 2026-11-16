import plotly.graph_objects as go
import streamlit as st

import carga
import marca

m = carga.tabla("metricas_modelos_ventas.csv")
imp = carga.tabla("importancia_variables.csv").head(10).iloc[::-1]
mejor = m.iloc[0]
lineal = m[m["modelo"].str.startswith("Lineal")].iloc[0]

marca.encabezado(
    "Recorrido · 3 de 6",
    "Predecir cuánto vende una tienda no dice cuánto añade una nevera",
    "El modelo de ventas describe la realidad tal como está. Sirve para verificar que hay señal "
    "y para saber qué mueve las ventas, no para decidir dónde instalar.",
)
marca.fila_kpis([
    ("Mejor modelo", mejor["modelo"], "de cuatro algoritmos comparados", False),
    ("R² en prueba", marca.dec(mejor["R2_test"]), f"frente a {marca.dec(lineal['R2_test'])} del lineal", True),
    ("Error absoluto medio", marca.cop(mejor["MAE_COP_test"]), "por tienda al mes, en prueba", False),
    ("Variable dominante", marca.etiqueta(imp.iloc[-1]["variable"]), "por amplio margen", False),
])

col1, col2 = st.columns(2)
with col1:
    fig = go.Figure()
    fig.add_bar(name="Validación cruzada", x=m["modelo"], y=m["R2_cv"], marker_color=marca.GRIS_CLARO)
    fig.add_bar(name="Prueba", x=m["modelo"], y=m["R2_test"],
                marker_color=[marca.ROJO if i == 0 else marca.GRIS for i in range(len(m))],
                text=[marca.dec(v) for v in m["R2_test"]], textposition="outside")
    fig.update_layout(title="R² por modelo (logaritmo de ventas)", barmode="group", yaxis_range=[0.6, 0.75])
    marca.grafico(fig, 380)
with col2:
    fig = go.Figure(go.Bar(x=imp["importancia"], y=[marca.etiqueta(v) for v in imp["variable"]],
                           orientation="h", marker_color=marca.ROJO))
    fig.update_layout(title="Qué mueve las ventas de hoy", xaxis_title="caída de R² al permutar")
    marca.grafico(fig, 380)

st.dataframe(
    m[["modelo", "R2_cv", "R2_test", "MAE_COP_test"]].rename(columns={
        "modelo": "Modelo", "R2_cv": "R² validación cruzada", "R2_test": "R² prueba",
        "MAE_COP_test": "MAE en prueba (COP)"}),
    hide_index=True, width="stretch",
    column_config={"R² validación cruzada": st.column_config.NumberColumn(format="%.3f"),
                   "R² prueba": st.column_config.NumberColumn(format="%.3f"),
                   "MAE en prueba (COP)": st.column_config.NumberColumn(format="$ %,.0f")},
)

marca.lectura(
    f"<b>{mejor['modelo']}</b> mejora al lineal en {marca.dec(mejor['R2_test'] - lineal['R2_test'])} "
    "de R² y se equivoca en torno a "
    f"{marca.cop(mejor['MAE_COP_test'])} por tienda. El tráfico de clientes manda. Saber cuánto vende "
    "una tienda hoy es como leer el termómetro de un paciente: informa el estado actual y no dice qué "
    "cambiaría con un tratamiento nuevo.")

marca.siguiente("paginas/r4_efecto.py", "Siguiente: efecto de la nevera")
marca.pie()
