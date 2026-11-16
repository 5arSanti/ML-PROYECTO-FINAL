import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import carga
import datos
import marca

df = carga.tiendas()
f = st.session_state["filtros"]
rec = datos.recortar(df, f)

marca.encabezado("Operación", "Lista causal frente a reglas simples",
                 "Las cuatro estrategias se valoran con el mismo efecto estimado: solo cambia el "
                 "criterio de selección.")
if rec.empty:
    st.warning("No hay tiendas con esa combinación de filtros.")
    st.stop()

reglas = datos.comparar_reglas(df, f)
if f.recorte_activo():
    st.caption("Con filtros activos se muestran las tiendas de cada regla que caen en el recorte. "
               "La selección aleatoria es un valor esperado.")

col1, col2 = st.columns([1.3, 1])
with col1:
    fig = go.Figure(go.Bar(
        x=reglas["estrategia"], y=reglas["ganancia_total"] / 1e6,
        marker_color=[marca.COLORES_ESTRATEGIA[e] for e in reglas["estrategia"]],
        text=[marca.mm(v) for v in reglas["ganancia_total"]], textposition="outside"))
    fig.update_layout(title="Ganancia mensual por estrategia (millones de COP)")
    marca.grafico(fig, 380)
with col2:
    tabla = reglas.assign(
        ganancia=[marca.cop(v) for v in reglas["ganancia_total"]],
        tiendas=[marca.num(v) for v in reglas["tiendas"]],
    )[["estrategia", "tiendas", "ganancia", "no_rentables", "riesgo_alto"]]
    st.dataframe(tabla.rename(columns={"estrategia": "Estrategia", "tiendas": "Tiendas", "ganancia": "Ganancia (COP/mes)",
                                       "no_rentables": "No rentables", "riesgo_alto": "Riesgo alto"}),
                 hide_index=True, width="stretch")
    mejor_simple = reglas.iloc[1:3]["ganancia_total"].max()
    causal = reglas.iloc[0]["ganancia_total"]
    if mejor_simple > 0:
        marca.lectura(f"En este recorte la lista causal deja <b>{marca.mm(causal - mejor_simple)}</b> más al mes "
                      f"que la mejor regla simple ({marca.pct(100 * (causal / mejor_simple - 1))}).")

s = datos.solape(rec)
st.subheader(f"Coinciden {marca.num(s['ambas'])} tiendas; las que no coinciden explican la diferencia")
col1, col2 = st.columns([1, 1.3])
with col1:
    pc, pv = s["perfil_causal"], s["perfil_ventas"]
    st.dataframe(pd.DataFrame({
        "Indicador": ["Temperatura media", "Ventas actuales", "Clientes por día", "Ganancia estimada"],
        f"Solo lista causal ({s['solo_causal']})": [f"{marca.dec(pc['temperatura'], 1)} °C", marca.cop(pc["ventas"]),
                                                    marca.num(pc["clientes"]), marca.cop(pc["ganancia"])],
        f"Solo regla de ventas ({s['solo_ventas']})": [f"{marca.dec(pv['temperatura'], 1)} °C", marca.cop(pv["ventas"]),
                                                       marca.num(pv["clientes"]), marca.cop(pv["ganancia"])],
    }), hide_index=True, width="stretch")
with col2:
    sol = datos.etiquetar_solape(rec)
    colores = {"Ambas": marca.GRIS_OSCURO, "Solo lista causal": marca.ROJO, "Solo regla de ventas": marca.AMBAR}
    fig = go.Figure()
    for grupo, color in colores.items():
        d = sol[sol["grupo"] == grupo]
        fig.add_trace(go.Scattermap(lat=d["latitud"], lon=d["longitud"], mode="markers", name=grupo,
                                    marker=dict(size=7, color=color), text=d["id_tienda"],
                                    hovertemplate="%{text}<extra>" + grupo + "</extra>"))
    fig.update_layout(map=dict(style="carto-positron", zoom=4.4,
                               center=dict(lat=float(rec["latitud"].mean()), lon=float(rec["longitud"].mean()))),
                      title="Dónde quedan las tiendas de cada criterio")
    marca.grafico(fig, 460)
marca.pie()
