"""Lecturas cacheadas de salidas/ para las páginas."""
import pandas as pd
import streamlit as st

import datos


@st.cache_data(show_spinner=False)
def tiendas() -> pd.DataFrame:
    return datos.cargar_tiendas()


@st.cache_data(show_spinner=False)
def kpis() -> dict[str, float]:
    return datos.kpis_nacionales()


@st.cache_data(show_spinner=False)
def tabla(nombre: str) -> pd.DataFrame:
    return datos.leer_csv(nombre)
