import plotly.graph_objects as go
import streamlit as st

import carga
import datos
import marca

k = carga.kpis()
df = carga.tiendas()
m = carga.tabla("metricas_modelos_riesgo.csv")
curva = carga.tabla("curva_umbral_retencion.csv")
imp = carga.tabla("importancia_riesgo.csv").head(10).iloc[::-1]
optimo = curva.loc[curva["valor_neto"].idxmax()]
en_umbral = curva.iloc[(curva["umbral"] - datos.UMBRAL_RIESGO).abs().argmin()]

marca.encabezado(
    "Recorrido · 5 de 6",
    "Quién se puede ir, y cuándo conviene visitarlo",
    "Una de cada diez tiendas cambia de proveedor principal en seis meses. El umbral para actuar "
    "sale de los costos del caso, no del 0,5 de costumbre.",
)
marca.fila_kpis([
    ("Prevalencia", marca.pct(100 * datos.PREVALENCIA_CAMBIO), "cambia de proveedor en 6 meses", False),
    ("PR-AUC", marca.dec(m["PR_AUC"].iloc[0]), "cuatro veces la prevalencia", False),
    ("Umbral por costos", marca.dec(datos.UMBRAL_RIESGO, 2), "50.000 / (0,40 × 500.000)", True),
    ("Riesgo alto en la lista", marca.num(k["Tiendas de riesgo Alto en la lista"]), "de las 1.000 tiendas", False),
])

col1, col2 = st.columns([1.2, 1])
with col1:
    fig = go.Figure(go.Scatter(x=curva["umbral"], y=curva["valor_neto"] / 1e6, mode="lines",
                               line=dict(color=marca.GRIS_OSCURO, width=3), name="Valor neto"))
    fig.add_vline(x=datos.UMBRAL_RIESGO, line_dash="dash", line_color=marca.ROJO,
                  annotation_text="umbral 0,25", annotation_position="top right")
    fig.add_scatter(x=[optimo["umbral"]], y=[optimo["valor_neto"] / 1e6], mode="markers",
                    marker=dict(color=marca.ROJO, size=12), name="Óptimo empírico")
    fig.update_layout(title="Valor neto de una campaña de retención según el umbral",
                      xaxis_title="umbral de probabilidad", yaxis_title="millones de COP")
    marca.grafico(fig, 380)
with col2:
    fig = go.Figure(go.Bar(x=imp["importancia"], y=[marca.etiqueta(v) for v in imp["variable"]],
                           orientation="h", marker_color=marca.AMBAR))
    fig.update_layout(title="Señales que anticipan un cambio", xaxis_title="caída de PR-AUC al permutar")
    marca.grafico(fig, 380)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Tres modelos, por qué el boosting sin pesos**")
    st.dataframe(m.rename(columns={"modelo": "Modelo", "ROC_AUC": "ROC-AUC", "PR_AUC": "PR-AUC",
                                   "prob_media": "Probabilidad media"}),
                 hide_index=True, width="stretch",
                 column_config={c: st.column_config.NumberColumn(format="%.3f")
                                for c in ("ROC-AUC", "PR-AUC", "Brier", "Probabilidad media")})
with col2:
    st.markdown("**Tres puntos de la curva**")
    puntos = curva[curva["umbral"].round(2).isin([0.20, 0.25, 0.50])]
    st.dataframe(puntos.rename(columns={"umbral": "Umbral", "n": "Tiendas marcadas", "precision": "Precisión",
                                        "recall": "Recall", "valor_neto": "Valor neto (COP)"}),
                 hide_index=True, width="stretch",
                 column_config={"Umbral": st.column_config.NumberColumn(format="%.2f"),
                                "Precisión": st.column_config.NumberColumn(format="%.3f"),
                                "Recall": st.column_config.NumberColumn(format="%.3f"),
                                "Valor neto (COP)": st.column_config.NumberColumn(format="$ %,.0f")})

marca.lectura(
    "No se usa <i>accuracy</i>: decir que nadie cambia acertaría el 90,5 % y no serviría. El boosting con pesos "
    "ordena igual de bien pero infla las probabilidades, así que el umbral se aplica sobre el modelo sin pesos. "
    f"Conviene visitar cuando 0,40 × p × 500.000 supera 50.000. El óptimo empírico ({marca.dec(optimo['umbral'], 2)}, "
    f"{marca.mm(optimo['valor_neto'])}) casi coincide con el teórico ({marca.mm(en_umbral['valor_neto'])}).")

marca.siguiente("paginas/r6_decision.py", "Siguiente: la decisión")
marca.pie()
