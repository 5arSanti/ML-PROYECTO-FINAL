import numpy as np
import plotly.graph_objects as go
import streamlit as st

import carga
import datos
import marca

k = carga.kpis()
df = carga.tiendas()
comp = carga.tabla("comparacion_causal_vs_simple.csv")
simple, causal = comp["ventas_adicionales_cop"].iloc[0], comp["ventas_adicionales_cop"].iloc[1]
g_simple, g_causal = comp["ganancia_por_tienda"].iloc[0], comp["ganancia_por_tienda"].iloc[1]
sesgo = simple - causal
elegibles = int(k["Tiendas elegibles"])
rentables = int(k["Tiendas elegibles rentables"])

marca.encabezado(
    "Recorrido · 4 de 6",
    "La comparación obvia engaña: casi dos tercios no es la nevera",
    "Las neveras actuales se pusieron en las mejores tiendas. Para saber cuánto añade una nevera "
    "nueva hay que separar ese sesgo del efecto real.",
)
marca.fila_kpis([
    ("Efecto causal", f"+{marca.pct(k['Efecto promedio de la nevera'])}",
     f"IC 95 %: {marca.pct(datos.IC_EFECTO_PCT[0])} a {marca.pct(datos.IC_EFECTO_PCT[1])}", True),
    ("Venta adicional real", marca.cop(causal), "por tienda al mes", False),
    ("Diferencia simple", marca.cop(simple), f"sobreestima {marca.pct(100 * (simple / causal - 1), 0)}", False),
    ("Sesgo de selección", marca.pct(100 * sesgo / simple, 0), "de la brecha no es la nevera", False),
])

col1, col2 = st.columns([1.1, 1])
with col1:
    fig = go.Figure()
    fig.add_bar(name="Efecto real de la nevera", x=["Diferencia simple", "Efecto causal (DR-learner)"],
                y=[causal, causal], marker_color=marca.ROJO)
    fig.add_bar(name="Sesgo: eran mejores tiendas desde antes", x=["Diferencia simple", "Efecto causal (DR-learner)"],
                y=[sesgo, 0], marker_color=marca.GRIS_CLARO)
    fig.add_hline(y=datos.COSTO_NEVERA / datos.MARGEN, line_dash="dash", line_color=marca.NEGRO,
                  annotation_text="umbral de rentabilidad", annotation_position="top left")
    fig.update_layout(title="Venta adicional por tienda (COP al mes)", barmode="stack",
                      yaxis_tickformat=",.0f")
    marca.grafico(fig, 400)
with col2:
    st.markdown("**¿Con qué cifra se decide?**")
    eleccion = st.segmented_control("Cifra", ["Diferencia simple", "Efecto causal"],
                                    default="Efecto causal", label_visibility="collapsed")
    es_simple = eleccion == "Diferencia simple"
    marca.kpi("Venta adicional por tienda", marca.cop(simple if es_simple else causal), "al mes")
    st.write("")
    marca.kpi("Ganancia por tienda", marca.cop(g_simple if es_simple else g_causal),
              "0,25 × venta adicional − 60.000", principal=not es_simple)
    st.write("")
    marca.kpi("Tiendas que parecen rentables",
              f"las {marca.num(elegibles)}" if es_simple else marca.num(rentables),
              f"de {marca.num(elegibles)} elegibles")
    st.write("")
    marca.lectura("Con la diferencia simple cualquier tienda pagaría la nevera y no habría nada que decidir."
                  if es_simple else
                  f"Con el efecto causal solo {marca.num(rentables)} tiendas pagan el equipo: "
                  "escoger bien vale dinero.")

st.subheader("El calor es lo que manda")
t = datos.efecto_por_temperatura(df)
fig = go.Figure(go.Bar(x=t["banda"].astype(str), y=t["efecto"],
                       marker_color=["#F1E4E2", "#F0B3B7", "#E8737B", marca.ROJO, marca.ROJO_OSCURO],
                       text=[f"+{marca.pct(v)}" for v in t["efecto"]], textposition="outside"))
fig.update_layout(title="Aumento estimado de ventas por temperatura (12.700 elegibles)", yaxis_title="%")
marca.grafico(fig, 340)

col1, col2 = st.columns(2)
with col1:
    g = carga.tabla("validacion_gate.csv")
    corr = float(np.corrcoef(g["tau_predicho"], g["efecto_DR"])[0, 1])
    fig = go.Figure()
    fig.add_bar(name="Efecto medido (DR)", x=g["decil"], y=g["efecto_DR"], marker_color=marca.GRIS,
                error_y=dict(type="data", array=1.96 * g["ee"], color=marca.GRIS_OSCURO))
    fig.add_scatter(name="Efecto predicho", x=g["decil"], y=g["tau_predicho"], mode="lines+markers",
                    line=dict(color=marca.ROJO, width=3))
    fig.update_layout(title=f"El modelo ordena bien (correlación {marca.dec(corr)})",
                      xaxis_title="decil de efecto predicho", yaxis_title="efecto en log-ventas")
    marca.grafico(fig, 360)
with col2:
    b = carga.tabla("balance_covariables.csv").assign(
        abs_crudo=lambda d: d["SMD_crudo"].abs(), abs_pond=lambda d: d["SMD_ponderado"].abs()
    ).nlargest(12, "abs_crudo").iloc[::-1]
    nombres = [marca.etiqueta(v) for v in b["variable"]]
    fig = go.Figure()
    fig.add_scatter(name="Sin ajustar", x=b["abs_crudo"], y=nombres, mode="markers",
                    marker=dict(color=marca.GRIS, size=11))
    fig.add_scatter(name="Ponderado", x=b["abs_pond"], y=nombres, mode="markers",
                    marker=dict(color=marca.ROJO, size=11))
    fig.add_vline(x=0.1, line_dash="dash", line_color=marca.NEGRO)
    fig.update_layout(title="Balance antes y después del ajuste (|SMD|)")
    marca.grafico(fig, 360)

s = carga.tabla("sensibilidad_efecto.csv")
st.dataframe(s.rename(columns={"especificación": "Especificación", "efecto_%": "Efecto sobre ventas (%)"})
              [["Especificación", "Efecto sobre ventas (%)"]],
             hide_index=True, width="stretch",
             column_config={"Efecto sobre ventas (%)": st.column_config.NumberColumn(format="%.1f")})

marca.lectura(
    "El estimador es un <b>DR-learner</b> (doblemente robusto): combina un modelo de ventas con nevera, "
    "otro sin nevera y uno de la probabilidad de haberla recibido. Si uno de los tres está bien, el efecto "
    "no se cae. El efecto se mantiene entre 25,5 % y 27,1 % al cambiar la especificación, y tras el ajuste "
    "ninguna variable supera el umbral de desbalance.")

marca.siguiente("paginas/r5_riesgo.py", "Siguiente: riesgo de cambio")
marca.pie()
