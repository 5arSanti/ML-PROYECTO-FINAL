"""Filtros del bloque Operación, compartidos entre páginas."""
import pandas as pd
import streamlit as st

import datos

CLAVES = ("f_regiones", "f_ciudades", "f_tipos", "f_zonas", "f_riesgo", "f_universo")
UNIVERSOS = ("Las 1.000 seleccionadas", "Todas las elegibles")
ZONAS = ("Urbana", "Periurbana", "Rural")


def conservar_estado() -> None:
    for clave in CLAVES:
        if clave in st.session_state:
            st.session_state[clave] = st.session_state[clave]


def limpiar() -> None:
    for clave in CLAVES:
        st.session_state.pop(clave, None)


def barra(df: pd.DataFrame) -> datos.Filtros:
    with st.sidebar:
        st.markdown("**Filtros**")
        regiones = st.multiselect("Región", sorted(df["region"].unique()),
                                  key="f_regiones", placeholder="Todas")
        base = df[df["region"].isin(regiones)] if regiones else df
        validas = sorted(base["ciudad"].unique())
        if "f_ciudades" in st.session_state:
            st.session_state["f_ciudades"] = [c for c in st.session_state["f_ciudades"] if c in validas]
        ciudades = st.multiselect("Ciudad", validas, key="f_ciudades", placeholder="Todas")
        tipos = st.multiselect("Tipo de negocio", sorted(df["tipo_negocio"].unique()),
                               key="f_tipos", placeholder="Todos")
        zonas = st.multiselect("Zona", ZONAS, key="f_zonas", placeholder="Todas")
        riesgo = st.radio("Riesgo de cambio", ("Todos", "Alto", "Bajo"),
                          key="f_riesgo", horizontal=True)
        universo = st.radio("Tiendas", UNIVERSOS, key="f_universo")
        st.button("Limpiar filtros", on_click=limpiar, width="stretch")
    f = datos.Filtros(
        regiones=tuple(regiones), ciudades=tuple(ciudades), tipos=tuple(tipos),
        zonas=tuple(zonas), riesgo=riesgo,
        universo="seleccionadas" if universo == UNIVERSOS[0] else "elegibles",
    )
    n = len(datos.aplicar_filtros(df, f))
    st.sidebar.caption(f"{n:,} tiendas en vista".replace(",", "."))
    return f
