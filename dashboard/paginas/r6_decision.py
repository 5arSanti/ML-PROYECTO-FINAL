import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import carga
import datos
import marca

df = carga.tiendas()
k = carga.kpis()
reglas = datos.comparar_reglas(df, datos.Filtros())
s = datos.solape(df)
lista = df[df["es_seleccionada"]]
mitad = datos.tiendas_para_mitad(lista["ganancia_estimada_cop_mes"])

marca.encabezado(
    "Recorrido · 6 de 6",
    "Instalar las 1.000 neveras donde el efecto paga el equipo",
    "Se ordenan las 12.700 elegibles por ganancia estimada y se toman las 1.000 primeras. "
    "El valor del modelo se mide contra lo que se haría sin él.",
)

st.markdown("**Compara criterios de selección**")
eleccion = st.segmented_control("Estrategia", list(datos.ESTRATEGIAS), default="Lista causal",
                                label_visibility="collapsed") or "Lista causal"
fila = reglas.set_index("estrategia").loc[eleccion]
base = reglas.set_index("estrategia").loc["Lista causal"]
diferencia = fila["ganancia_total"] - base["ganancia_total"]
marca.fila_kpis([
    ("Ganancia mensual", marca.mm(fila["ganancia_total"]), marca.cop(fila["ganancia_total"]),
     eleccion == "Lista causal"),
    ("Frente a la lista causal", "referencia" if eleccion == "Lista causal" else marca.mm(diferencia),
     "al mes" if eleccion != "Lista causal" else "la mejor estrategia", False),
    ("Tiendas no rentables", marca.num(fila["no_rentables"]), "ganancia estimada ≤ 0", False),
    ("Riesgo alto", marca.num(fila["riesgo_alto"]), "tiendas de la selección", False),
])

col1, col2 = st.columns([1.2, 1])
with col1:
    fig = go.Figure(go.Bar(
        x=reglas["estrategia"], y=reglas["ganancia_total"] / 1e6,
        marker_color=[marca.ROJO if e == eleccion else marca.GRIS_CLARO for e in reglas["estrategia"]],
        text=[marca.mm(v) for v in reglas["ganancia_total"]], textposition="outside"))
    fig.update_layout(title="Ganancia mensual por criterio (millones de COP)")
    marca.grafico(fig, 380)
with col2:
    st.markdown(f"**Por qué estas tiendas y no las más grandes** · coinciden {marca.num(s['ambas'])}")
    pc, pv = s["perfil_causal"], s["perfil_ventas"]
    st.dataframe(pd.DataFrame({
        "Indicador": ["Temperatura media", "Ventas actuales", "Clientes por día", "Ganancia estimada"],
        f"Solo lista causal ({s['solo_causal']})": [f"{marca.dec(pc['temperatura'], 1)} °C", marca.cop(pc["ventas"]),
                                                    marca.num(pc["clientes"]), marca.cop(pc["ganancia"])],
        f"Solo regla de ventas ({s['solo_ventas']})": [f"{marca.dec(pv['temperatura'], 1)} °C", marca.cop(pv["ventas"]),
                                                       marca.num(pv["clientes"]), marca.cop(pv["ganancia"])],
    }), hide_index=True, width="stretch")
    marca.lectura("La regla de ventas compra tamaño en ciudades frías, donde una nevera añade poco. "
                  "La lista causal compra capacidad de respuesta al equipo.")

c = datos.ganancia_acumulada(lista["ganancia_estimada_cop_mes"])
fig = go.Figure(go.Scatter(x=c["posicion"], y=c["acumulada"] / 1e6, mode="lines", fill="tozeroy",
                           line=dict(color=marca.ROJO, width=3)))
fig.add_vline(x=mitad, line_dash="dash", line_color=marca.NEGRO,
              annotation_text=f"{marca.num(mitad)} tiendas = mitad de la ganancia")
fig.update_layout(title="Ganancia acumulada de la lista, de la mejor a la peor tienda",
                  xaxis_title="neveras instaladas", yaxis_title="millones de COP al mes")
marca.grafico(fig, 340)

st.subheader("Recomendación")
st.markdown(
    f"1. **Instalar las 1.000 neveras de la lista causal.** Deja {marca.mm(k['Ganancia mensual total estimada'])} "
    f"al mes, {marca.pct(k['Ventaja sobre la mejor regla simple (%)'])} más que la mejor regla simple.\n"
    f"2. **Cruzar las {marca.num(k['Tiendas de riesgo Alto en la lista'])} tiendas de riesgo alto** con la campaña "
    "de retención (COP 50.000 por visita, 40 % de efectividad).\n"
    "3. **No asignar con la diferencia simple ni con la regla de mayores ventas.**\n"
    f"4. **Ampliar el plan sería rentable:** la tienda 1.000 todavía deja "
    f"{marca.cop(k['Ganancia de la tienda n° 1.000'])} al mes; esa decisión excede este entregable.")
st.dataframe(pd.DataFrame(datos.SUPUESTOS, columns=["Supuesto", "Qué implica"]),
             hide_index=True, width="stretch")

st.page_link("paginas/o1_tablero.py", label="Ir al tablero de operación", icon=":material/dashboard:")
marca.pie()
