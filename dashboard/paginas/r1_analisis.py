import numpy as np
import plotly.graph_objects as go
import streamlit as st

import carga
import datos
import marca

k = carga.kpis()
df = carga.tiendas()

marca.encabezado(
    "Recorrido · 1 de 6",
    "Dónde instalar 1.000 neveras nuevas, y cuánto deja",
    "Gerencia pidió una lista de tiendas, una estimación de la ganancia y un tablero para "
    "explorar la decisión. Esta es la respuesta y el camino para llegar a ella.",
)
marca.fila_kpis([
    ("Recomendación", "1.000 tiendas", f"de {marca.num(k['Tiendas elegibles'])} elegibles", False),
    ("Ganancia mensual", marca.mm(k["Ganancia mensual total estimada"]),
     f"{marca.mm(k['Ganancia anual estimada'])} al año", True),
    ("Retorno", f"{marca.dec(k['Retorno sobre el costo'], 1)} veces", "sobre el costo de las neveras", False),
    ("Efecto de la nevera", f"+{marca.pct(k['Efecto promedio de la nevera'])}",
     f"IC 95 %: {marca.pct(datos.IC_EFECTO_PCT[0])} a {marca.pct(datos.IC_EFECTO_PCT[1])}", False),
    ("Riesgo alto", marca.num(k["Tiendas de riesgo Alto en la lista"]), "tiendas de la lista", False),
])

st.subheader("Análisis exploratorio: las neveras no se pusieron al azar")
col1, col2 = st.columns(2)
with col1:
    etiquetas = [e for e, _ in datos.EMBUDO][::-1]
    valores = [v for _, v in datos.EMBUDO][::-1]
    colores = [marca.ROJO if e in ("Elegibles", "Neveras a instalar") else marca.GRIS_CLARO
               for e in etiquetas]
    fig = go.Figure(go.Bar(x=valores, y=etiquetas, orientation="h", marker_color=colores,
                           text=[marca.num(v) for v in valores], textposition="outside"))
    fig.update_layout(title="Embudo de elegibilidad", xaxis_title="tiendas",
                      xaxis_range=[0, max(valores) * 1.18])
    marca.grafico(fig, 360)
with col2:
    b = carga.tabla("balance_covariables.csv").assign(
        abs_crudo=lambda d: d["SMD_crudo"].abs()).nlargest(12, "abs_crudo").iloc[::-1]
    fig = go.Figure(go.Bar(
        x=b["abs_crudo"], y=[marca.etiqueta(v) for v in b["variable"]], orientation="h",
        marker_color=[marca.ROJO if v > 0.1 else marca.GRIS_CLARO for v in b["abs_crudo"]]))
    fig.add_vline(x=0.1, line_dash="dash", line_color=marca.NEGRO)
    fig.update_layout(title="Desbalance entre tiendas con y sin nevera (|SMD|)", xaxis_title="|SMD|")
    marca.grafico(fig, 360)

marca.lectura(
    f"Las tiendas que ya tienen nevera FEMSA reciben un <b>{datos.TRAFICO_EXTRA_PCT} % más de clientes</b> "
    f"y venden <b>{marca.cop(datos.DIFERENCIA_SIMPLE_COP)} más al mes</b>. Pero eran mejores tiendas "
    "desde antes: las barras rojas superan el umbral de 0,1 de desbalance. Comparar promedios mezcla "
    "el efecto de la nevera con el lugar donde se decidió ponerla.")

st.subheader("Las ventas se leen en porcentaje, no en pesos")
col1, col2 = st.columns(2)
with col1:
    fig = go.Figure(go.Histogram(x=df["ventas_femsa_cop_mes"] / 1e6, nbinsx=60, marker_color=marca.GRIS))
    fig.update_layout(title="Ventas FEMSA de las elegibles (millones de COP)", bargap=0.02)
    marca.grafico(fig, 300)
with col2:
    fig = go.Figure(go.Histogram(x=np.log(df["ventas_femsa_cop_mes"]), nbinsx=60, marker_color=marca.ROJO))
    fig.update_layout(title="Las mismas ventas en logaritmo", bargap=0.02)
    marca.grafico(fig, 300)
marca.lectura(
    "Unas pocas tiendas muy grandes estiran la cola. En logaritmo la distribución es casi simétrica, "
    "por eso los modelos se entrenan en esa escala y el efecto de la nevera se expresa como un "
    "porcentaje: el mismo 27 % vale distinto en una tienda pequeña y en una grande.")

marca.siguiente("paginas/r2_preparacion.py", "Siguiente: preparación de datos")
marca.pie()
