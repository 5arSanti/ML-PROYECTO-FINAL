import plotly.graph_objects as go
import streamlit as st

import carga
import datos
import marca

df = carga.tiendas()
f = st.session_state["filtros"]
lista = df[df["es_seleccionada"]]

marca.encabezado("Operación", "Consultar una tienda",
                 "Busca cualquiera de las 12.700 tiendas elegibles por su código.")

codigo = st.selectbox("id_tienda", sorted(df["id_tienda"]), index=None,
                      placeholder="Escribe o elige un código, por ejemplo T20612")
if not codigo:
    st.info("Elige una tienda para ver su ficha.")
    marca.pie()
    st.stop()

t = datos.buscar_tienda(df, codigo)
if t is None:
    st.error(f"No existe la tienda {codigo} entre las elegibles.")
    st.stop()
if codigo not in set(datos.aplicar_filtros(df, f)["id_tienda"]):
    st.caption("Esta tienda queda fuera del recorte actual de filtros; se muestra igual.")

seleccionada = bool(t["es_seleccionada"])
marca.fila_kpis([
    ("Decisión", "Instalar" if seleccionada else "No instalar",
     f"ranking {marca.num(t['ranking'])} de 12.700", seleccionada),
    ("Ganancia estimada", marca.cop(t["ganancia_estimada_cop_mes"]), "al mes con nevera", False),
    ("Efecto de la nevera", f"+{marca.pct(t['efecto_pct_ventas'])}", marca.cop(t["ventas_adicionales_cop_mes"]) + " de venta adicional", False),
    ("Riesgo de cambio", t["riesgo_cambio"], f"probabilidad {marca.dec(t['prob_cambio'], 2)} · umbral 0,25", False),
])

col1, col2 = st.columns([1, 1.2])
with col1:
    st.markdown("**Ficha**")
    filas = [
        ("Región / ciudad", f"{t['region']} · {t['ciudad']}"),
        ("Tipo de negocio / zona", f"{t['tipo_negocio']} · {t['zona']}"),
        ("Estrato", marca.num(t["estrato"])),
        ("Temperatura media", f"{marca.dec(t['temperatura_media_c'], 1)} °C"),
        ("Clientes por día", marca.num(t["clientes_prom_dia"])),
        ("Ventas FEMSA actuales", marca.cop(t["ventas_femsa_cop_mes"])),
        ("¿La elegiría la regla de mayores ventas?", "Sí" if t["en_ventas"] else "No"),
        ("¿La elegiría la regla de mayor tráfico?", "Sí" if t["en_trafico"] else "No"),
        ("Percentil de ganancia en la lista",
         marca.pct(datos.percentil(lista["ganancia_estimada_cop_mes"], t["ganancia_estimada_cop_mes"]), 0)),
        ("Percentil de efecto en la lista",
         marca.pct(datos.percentil(lista["efecto_pct_ventas"], t["efecto_pct_ventas"]), 0)),
    ]
    st.dataframe({"Dato": [a for a, _ in filas], "Valor": [b for _, b in filas]},
                 hide_index=True, width="stretch")
with col2:
    fig = go.Figure(go.Scattermap(lat=[t["latitud"]], lon=[t["longitud"]], mode="markers",
                                  marker=dict(size=18, color=marca.ROJO if seleccionada else marca.GRIS_OSCURO),
                                  text=[codigo], hoverinfo="text"))
    fig.update_layout(map=dict(style="carto-positron", zoom=11,
                               center=dict(lat=float(t["latitud"]), lon=float(t["longitud"]))))
    marca.grafico(fig, 420)

if seleccionada and t["es_alto"]:
    marca.lectura("Está en la lista y tiene riesgo alto: conviene incluirla en la campaña de retención.")
elif not seleccionada and t["ganancia_estimada_cop_mes"] > 0:
    marca.lectura("Es rentable pero no entra en las 1.000: quedaría en una ampliación del plan.")
elif not seleccionada:
    marca.lectura("Su ganancia estimada no cubre el costo de la nevera.")
marca.pie()
