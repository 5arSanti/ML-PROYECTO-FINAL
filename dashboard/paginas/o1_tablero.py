import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import carga
import datos
import filtros
import marca

df = carga.tiendas()
f = st.session_state["filtros"]
vista = datos.aplicar_filtros(df, f)

marca.encabezado("Operación", "Tablero de la decisión",
                 "Filtra por región, ciudad, tipo de negocio, zona o riesgo en la barra lateral. "
                 "Todas las cifras de esta página se recalculan con el recorte.")
if vista.empty:
    st.warning("No hay tiendas con esa combinación de filtros.")
    st.button("Limpiar filtros", on_click=filtros.limpiar, key="limpiar_vacio")
    st.stop()

r = datos.resumen_vista(df, f, carga.kpis())
marca.fila_kpis([
    ("Tiendas en vista", marca.num(r["tiendas"]),
     "de la lista recomendada" if f.universo == "seleccionadas" else "elegibles del recorte", False),
    ("Ganancia mensual", marca.mm(r["ganancia_total"]), marca.cop(r["ganancia_total"]), True),
    ("Ganancia media", marca.cop(r["ganancia_media"]), "por tienda al mes", False),
    ("Riesgo alto", marca.num(r["riesgo_alto"]), marca.pct(100 * r["riesgo_alto"] / r["tiendas"]), False),
    ("Retorno", f"{marca.dec(r['retorno'], 1)} veces", "sobre el costo de las neveras", False),
])

alto = vista[vista["es_alto"]]
fig = go.Figure()
fig.add_trace(go.Scattermap(lat=alto["latitud"], lon=alto["longitud"], mode="markers",
                            marker=dict(size=13, color=marca.NEGRO), name="Riesgo alto", hoverinfo="skip"))
fig.add_trace(go.Scattermap(
    lat=vista["latitud"], lon=vista["longitud"], mode="markers", name="Tiendas",
    marker=dict(size=9, color=vista["ganancia_estimada_cop_mes"], colorscale=marca.ESCALA_GANANCIA,
                cmin=float(vista["ganancia_estimada_cop_mes"].quantile(0.05)),
                cmax=float(vista["ganancia_estimada_cop_mes"].quantile(0.95)),
                colorbar=dict(title="Ganancia<br>COP/mes")),
    customdata=vista[["id_tienda", "ciudad", "tipo_negocio", "ganancia_estimada_cop_mes", "ranking",
                      "riesgo_cambio"]],
    hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} · %{customdata[2]}<br>"
                  "Ganancia: $ %{customdata[3]:,.0f}<br>Ranking: %{customdata[4]}<br>"
                  "Riesgo: %{customdata[5]}<extra></extra>"))
fig.update_layout(map=dict(style="carto-positron", center=dict(lat=float(vista["latitud"].mean()),
                                                               lon=float(vista["longitud"].mean())),
                           zoom=4.6 if not f.recorte_activo() else 5.5),
                  title="Mapa: color = ganancia mensual estimada; anillo negro = riesgo alto",
                  showlegend=False)
marca.grafico(fig, 560)

col1, col2 = st.columns(2)
for col, columna, titulo in ((col1, "region", "Ganancia por región"),
                             (col2, "tipo_negocio", "Ganancia por tipo de negocio")):
    with col:
        g = datos.agrupar(vista, columna)
        fig = go.Figure(go.Bar(x=g[columna], y=g["ganancia_total"] / 1e6, marker_color=marca.ROJO,
                               text=[marca.mm(v) for v in g["ganancia_total"]], textposition="outside",
                               customdata=g[["tiendas", "riesgo_alto"]],
                               hovertemplate="%{x}<br>%{customdata[0]} tiendas · "
                                             "%{customdata[1]} riesgo alto<extra></extra>"))
        fig.update_layout(title=titulo + " (millones de COP)")
        marca.grafico(fig, 340)

col1, col2, col3 = st.columns(3)
with col1:
    g = datos.agrupar(vista, "zona")
    fig = go.Figure(go.Bar(x=g["zona"], y=g["ganancia_total"] / 1e6, marker_color=marca.GRIS_OSCURO))
    fig.update_layout(title="Por zona (MM COP)")
    marca.grafico(fig, 300)
with col2:
    g = datos.agrupar(vista, "estrato").sort_values("estrato")
    fig = go.Figure(go.Bar(x=g["estrato"].astype(str), y=g["ganancia_total"] / 1e6, marker_color=marca.GRIS_OSCURO))
    fig.update_layout(title="Por estrato (MM COP)")
    marca.grafico(fig, 300)
with col3:
    g = datos.agrupar(vista, "ciudad").head(10).iloc[::-1]
    fig = go.Figure(go.Bar(x=g["ganancia_total"] / 1e6, y=g["ciudad"], orientation="h", marker_color=marca.ROJO))
    fig.update_layout(title="Top 10 ciudades (MM COP)")
    marca.grafico(fig, 300)

st.subheader("A quién visitar primero")
cuad = datos.cuadrantes_riesgo(vista)
prioridad = int((cuad["cuadrante"] == "Prioridad de retención").sum())
col1, col2 = st.columns([1.4, 1])
with col1:
    fig = px.scatter(cuad, x="prob_cambio", y="ganancia_estimada_cop_mes", color="cuadrante",
                     hover_name="id_tienda", hover_data={"ciudad": True, "cuadrante": False},
                     color_discrete_map={"Prioridad de retención": marca.ROJO,
                                         "Alta ganancia, riesgo bajo": marca.GRIS_OSCURO,
                                         "Baja ganancia, riesgo alto": marca.AMBAR,
                                         "Baja ganancia, riesgo bajo": marca.GRIS_CLARO},
                     labels={"prob_cambio": "probabilidad de cambio", "ganancia_estimada_cop_mes": "ganancia COP/mes",
                             "cuadrante": ""})
    fig.add_vline(x=datos.UMBRAL_RIESGO, line_dash="dash", line_color=marca.NEGRO)
    fig.add_hline(y=float(vista["ganancia_estimada_cop_mes"].median()), line_dash="dot", line_color=marca.GRIS)
    fig.update_layout(title="Ganancia frente a probabilidad de cambio")
    marca.grafico(fig, 400)
with col2:
    fig = go.Figure(go.Histogram(x=vista["prob_cambio"], nbinsx=40, marker_color=marca.GRIS))
    fig.add_vline(x=datos.UMBRAL_RIESGO, line_dash="dash", line_color=marca.ROJO,
                  annotation_text="umbral 0,25")
    fig.update_layout(title="Distribución de la probabilidad de cambio", bargap=0.03)
    marca.grafico(fig, 400)
marca.lectura(f"<b>{marca.num(prioridad)} tiendas</b> combinan ganancia sobre la mediana del recorte y riesgo "
              "alto: son la primera lista de visitas de la campaña de retención.")

st.subheader("Detalle de tiendas")
detalle = vista.sort_values("ganancia_estimada_cop_mes", ascending=False)[list(datos.COLUMNAS_DETALLE)]
st.dataframe(detalle, hide_index=True, width="stretch", height=420, column_config={
    "id_tienda": "Tienda",
    "ganancia_estimada_cop_mes": st.column_config.NumberColumn("Ganancia (COP/mes)", format="$ %,.0f"),
    "riesgo_cambio": "Riesgo",
    "prob_cambio": st.column_config.ProgressColumn("Prob. de cambio", min_value=0, max_value=1, format="%.2f"),
    "ranking": "Ranking",
    "region": "Región", "ciudad": "Ciudad", "tipo_negocio": "Tipo", "zona": "Zona",
    "efecto_pct_ventas": st.column_config.NumberColumn("Efecto (%)", format="%.1f"),
    "ventas_femsa_cop_mes": st.column_config.NumberColumn("Ventas actuales", format="$ %,.0f"),
})
st.download_button("Descargar el recorte (CSV)", detalle.to_csv(index=False).encode("utf-8"),
                   file_name="tiendas_recorte.csv", mime="text/csv")
marca.pie()
