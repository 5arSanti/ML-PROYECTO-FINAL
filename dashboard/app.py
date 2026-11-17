"""Plan de Neveras FEMSA: presentación del proyecto y tablero de decisión."""
from pathlib import Path

import streamlit as st

import carga
import datos
import filtros
import marca

_ASSETS = Path(__file__).with_name("assets")
st.set_page_config(page_title="Plan de neveras · Coca-Cola FEMSA",
                   page_icon=str(_ASSETS / "marca.png"),
                   layout="wide")
filtros.conservar_estado()
marca.aplicar_estilo()
st.logo(str(_ASSETS / "marca.png"), icon_image=str(_ASSETS / "marca.png"))

RECORRIDO = [
    st.Page("paginas/r1_analisis.py", title="1. Análisis exploratorio", default=True),
    st.Page("paginas/r2_preparacion.py", title="2. Preparación de datos"),
    st.Page("paginas/r3_ventas.py", title="3. Modelo de ventas"),
    st.Page("paginas/r4_efecto.py", title="4. Efecto de la nevera"),
    st.Page("paginas/r5_riesgo.py", title="5. Riesgo de cambio"),
    st.Page("paginas/r6_decision.py", title="6. Decisión"),
]
OPERACION = [
    st.Page("paginas/o1_tablero.py", title="Tablero"),
    st.Page("paginas/o2_reglas.py", title="Comparar reglas"),
    st.Page("paginas/o3_senales.py", title="Señales"),
    st.Page("paginas/o4_escenarios.py", title="Escenarios"),
    st.Page("paginas/o5_tienda.py", title="Consultar tienda"),
]

pagina = st.navigation({"Recorrido": RECORRIDO, "Operación": OPERACION})

try:
    if pagina.url_path in {p.url_path for p in OPERACION}:
        st.session_state["filtros"] = filtros.barra(carga.tiendas())
    pagina.run()
except datos.DatosFaltantes as error:
    st.error(f"No se pudieron cargar los datos del tablero. {error}")
    st.info("Corre el cuaderno completo para regenerar la carpeta salidas/ y vuelve a cargar la página.")
