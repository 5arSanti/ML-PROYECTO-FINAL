import plotly.graph_objects as go
import streamlit as st

import carga
import marca

marca.encabezado("Operación", "Señales: qué variables pesan en cada modelo",
                 "Tres preguntas distintas, tres rankings distintos. La importancia es la caída del "
                 "desempeño al desordenar cada variable.")

PANELES = (
    ("importancia_variables.csv", "Ventas de hoy", "caída de R²", marca.GRIS_OSCURO,
     "El tráfico explica casi todo lo que vende una tienda hoy. No dice dónde una nevera añade más."),
    ("importancia_heterogeneidad.csv", "Dónde rinde más una nevera", "importancia en el efecto", marca.ROJO,
     "Ciudad, tráfico y temperatura deciden cuánto añade el equipo: por eso la lista se concentra en la costa."),
    ("importancia_riesgo.csv", "Quién se puede ir", "caída de PR-AUC", marca.AMBAR,
     "El riesgo se lee en la relación comercial: participación, nevera operativa, precio, visitas y quiebre."),
)

for archivo, titulo, eje, color, texto in PANELES:
    t = carga.tabla(archivo).head(12).iloc[::-1]
    st.subheader(titulo)
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = go.Figure(go.Bar(x=t["importancia"], y=[marca.etiqueta(v) for v in t["variable"]],
                               orientation="h", marker_color=color))
        fig.update_layout(xaxis_title=eje)
        marca.grafico(fig, 360)
    with col2:
        st.write("")
        marca.lectura(texto)
marca.pie()
