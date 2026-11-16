import numpy as np
import plotly.graph_objects as go
import streamlit as st

import carga
import datos
import marca

df = carga.tiendas()
base = datos.escenario(df)

marca.encabezado("Operación", "Escenarios: qué pasa si cambian los supuestos",
                 "Aplica la fórmula del caso (margen × venta adicional − costo) a los efectos ya "
                 "estimados y vuelve a ordenar las 12.700 elegibles. No reentrena ningún modelo; "
                 "los filtros de la barra lateral no aplican aquí.")

col1, col2, col3, col4 = st.columns(4)
margen = col1.slider("Margen FEMSA (%)", 15, 35, 25, 1) / 100
costo = col2.slider("Costo de la nevera (COP/mes)", 30_000, 120_000, 60_000, 5_000)
n = col3.slider("Número de neveras", 500, 2_000, 1_000, 50)
recorte = col4.slider("Recorte del efecto (%)", 0, 50, 0, 5) / 100

e = datos.escenario(df, margen=margen, costo=costo, n=n, recorte_efecto=recorte)
marca.fila_kpis([
    ("Ganancia mensual", marca.mm(e.ganancia_total), f"{marca.mm(e.ganancia_total - base.ganancia_total)} frente a la base", True),
    ("Tiendas rentables", marca.num(e.rentables), "de 12.700 elegibles", False),
    ("Última tienda elegida", marca.cop(e.ultima), "ganancia de la tienda en el corte", False),
    ("Coinciden con la lista", marca.num(e.coincidencias), "de las 1.000 recomendadas", False),
])

acum = np.cumsum(e.ganancias_ordenadas)
fig = go.Figure(go.Scatter(x=np.arange(1, len(acum) + 1), y=acum / 1e6, mode="lines",
                           line=dict(color=marca.GRIS_OSCURO, width=3), name="Ganancia acumulada"))
fig.add_vline(x=n, line_dash="dash", line_color=marca.ROJO, annotation_text=f"{marca.num(n)} neveras")
fig.add_scatter(x=[int(acum.argmax()) + 1], y=[acum.max() / 1e6], mode="markers",
                marker=dict(color=marca.NEGRO, size=10), name="Máximo: aquí la siguiente tienda ya no paga")
fig.update_layout(title="Ganancia acumulada al instalar en orden de ganancia (12.700 elegibles)",
                  xaxis_title="neveras instaladas", yaxis_title="millones de COP al mes")
marca.grafico(fig, 400)

marca.lectura(
    "Margen y costo mueven la ganancia pero casi no cambian <b>qué</b> tiendas entran: reescalan a todas por "
    "igual. El supuesto que sí importa es la ignorabilidad del efecto, que ningún slider puede probar.")

st.markdown("**Sensibilidades calculadas en el cuaderno**")
sens = carga.tabla("sensibilidad_decision.csv")
st.dataframe(sens.rename(columns={"supuesto": "Supuesto", "ganancia_total": "Ganancia (COP/mes)",
                                  "coincide_con_lista": "Coinciden con la lista"}),
             hide_index=True, width="stretch",
             column_config={"Ganancia (COP/mes)": st.column_config.NumberColumn(format="$ %,.0f")})
marca.pie()
