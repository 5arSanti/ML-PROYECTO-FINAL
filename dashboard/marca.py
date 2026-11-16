"""Identidad visual (inspirada en Coca-Cola FEMSA), formato es-CO y componentes."""
from __future__ import annotations

import math

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

ROJO = "#E41E2B"
ROJO_OSCURO = "#7A0E14"
NEGRO = "#111111"
GRIS_OSCURO = "#5F5A55"
GRIS = "#8A8580"
GRIS_CLARO = "#D9D5D0"
FONDO_SUAVE = "#F6F4F2"
VERDE = "#2E7D4F"
AMBAR = "#C77700"

COLORES_ESTRATEGIA = {
    "Lista causal": ROJO,
    "Mayores ventas": GRIS_OSCURO,
    "Mayor tráfico": GRIS,
    "Selección aleatoria": GRIS_CLARO,
}
COLORES_RIESGO = {"Alto": AMBAR, "Bajo": VERDE}
ESCALA_GANANCIA = [[0.0, "#F4A6AC"], [0.5, ROJO], [1.0, "#5C0A0F"]]

ETIQUETAS = {
    "antiguedad_anios": "Antigüedad de la tienda",
    "area_m2": "Área (m²)",
    "cerca_colegio": "Cerca de colegio",
    "cerca_parada_transporte": "Cerca de transporte",
    "ciudad": "Ciudad",
    "clientes_prom_dia": "Clientes por día",
    "departamento": "Departamento",
    "dias_abre_semana": "Días de apertura",
    "dist_cedi_km": "Distancia al CEDI",
    "dist_hard_discount_km": "Distancia a hard discount",
    "estrato": "Estrato",
    "horas_abre_dia": "Horas de apertura",
    "indice_precio_femsa": "Índice de precio FEMSA",
    "indice_precio_postobon": "Índice de precio Postobón",
    "n_referencias_total": "Referencias",
    "n_tiendas_competencia_500m": "Competencia a 500 m",
    "nevera_femsa_operativa": "Nevera FEMSA operativa",
    "nevera_postobon": "Nevera Postobón",
    "nevera_postobon_operativa": "Nevera Postobón operativa",
    "nevera_propia_tienda": "Nevera propia",
    "num_neveras_postobon": "Neveras Postobón",
    "pct_quiebre_femsa": "Quiebre FEMSA",
    "pct_quiebre_postobon": "Quiebre Postobón",
    "poblacion_500m": "Población a 500 m",
    "promos_activas_femsa": "Promociones FEMSA",
    "puertas_nevera_postobon": "Puertas nevera Postobón",
    "share_femsa_valor": "Participación FEMSA",
    "temperatura_media_c": "Temperatura media",
    "tipo_negocio": "Tipo de negocio",
    "visitas_mes_femsa": "Visitas FEMSA al mes",
    "visitas_mes_postobon": "Visitas Postobón al mes",
    "zona": "Zona",
}

pio.templates["kof"] = go.layout.Template(layout=dict(
    font=dict(family="Inter, -apple-system, 'Segoe UI', Roboto, sans-serif", color=NEGRO, size=13),
    colorway=[ROJO, GRIS_OSCURO, GRIS, GRIS_CLARO],
    paper_bgcolor="white",
    plot_bgcolor="white",
    separators=",.",
    title=dict(x=0, xanchor="left", font=dict(size=15, color=NEGRO, weight=600)),
    xaxis=dict(gridcolor="#EEEAE6", zeroline=False, linecolor=GRIS_CLARO, title_font_size=12,
               automargin=True),
    yaxis=dict(gridcolor="#EEEAE6", zeroline=False, linecolor=GRIS_CLARO, title_font_size=12,
               automargin=True),
    hoverlabel=dict(bgcolor=NEGRO, font_color="white", bordercolor=NEGRO),
    legend=dict(orientation="h", yanchor="top", y=-0.15, x=0),
    margin=dict(l=10, r=10, t=50, b=10),
))

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
  font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
}
.kof-marca {font-weight:700; font-size:1.05rem; color:#111111; letter-spacing:-.01em;
  border-left:5px solid #E41E2B; padding-left:10px; margin:4px 0 12px;}
.kof-marca span {display:block; font-weight:400; font-size:.78rem; color:#6B6560;}
.kof-eyebrow {font-size:.74rem; letter-spacing:.12em; text-transform:uppercase;
  color:#E41E2B; font-weight:700; margin-bottom:2px;}
.kof-titulo {font-size:2rem; font-weight:700; color:#111111; letter-spacing:-.02em;
  line-height:1.15; margin:0 0 6px;}
.kof-bajada {font-size:1.02rem; color:#4A4541; max-width:880px; margin-bottom:18px;}
.kof-kpi {background:#FFFFFF; border:1px solid #E6E1DC; border-radius:12px;
  padding:14px 16px; height:100%;}
.kof-kpi .lab {font-size:.70rem; letter-spacing:.06em; text-transform:uppercase;
  color:#6B6560; font-weight:700;}
.kof-kpi .val {font-size:1.6rem; font-weight:700; color:#111111; line-height:1.2;
  margin-top:4px; font-variant-numeric:tabular-nums;}
.kof-kpi .sub {font-size:.80rem; color:#6B6560; margin-top:2px;}
.kof-kpi.principal {border:2px solid #E41E2B;}
.kof-kpi.principal .val {color:#E41E2B;}
.kof-lectura {background:#F6F4F2; border-left:4px solid #E41E2B; border-radius:0 8px 8px 0;
  padding:12px 16px; margin:6px 0 18px; color:#2B2724; font-size:.95rem;}
.kof-lectura b {color:#111111;}
.kof-pie {font-size:.76rem; color:#8A8580; border-top:1px solid #E6E1DC;
  margin-top:28px; padding-top:10px;}
</style>
"""

WORDMARK = ('<div class="kof-marca">Plan de Neveras · FEMSA'
            '<span>Analítica comercial · Proyecto final ML</span></div>')


def _es(texto: str) -> str:
    return texto.replace(",", "§").replace(".", ",").replace("§", ".")


def _vacio(v) -> bool:
    return v is None or (isinstance(v, float) and math.isnan(v))


def num(v) -> str:
    return "—" if _vacio(v) else _es(f"{v:,.0f}")


def cop(v) -> str:
    return "—" if _vacio(v) else "$ " + _es(f"{v:,.0f}")


def mm(v, decimales: int = 1) -> str:
    return "—" if _vacio(v) else _es(f"{v / 1e6:,.{decimales}f}") + " MM"


def pct(v, decimales: int = 1) -> str:
    return "—" if _vacio(v) else _es(f"{v:,.{decimales}f}") + " %"


def dec(v, decimales: int = 3) -> str:
    return "—" if _vacio(v) else _es(f"{v:,.{decimales}f}")


def etiqueta(variable: str) -> str:
    return ETIQUETAS.get(variable, variable.replace("_", " ").capitalize())


def aplicar_estilo() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def encabezado(eyebrow: str, titulo: str, bajada: str = "") -> None:
    html = f'<div class="kof-eyebrow">{eyebrow}</div><div class="kof-titulo">{titulo}</div>'
    if bajada:
        html += f'<div class="kof-bajada">{bajada}</div>'
    st.markdown(html, unsafe_allow_html=True)


def kpi(etiqueta_kpi: str, valor: str, sub: str = "", principal: bool = False) -> None:
    clase = "kof-kpi principal" if principal else "kof-kpi"
    st.markdown(f'<div class="{clase}"><div class="lab">{etiqueta_kpi}</div>'
                f'<div class="val">{valor}</div><div class="sub">{sub}</div></div>',
                unsafe_allow_html=True)


def fila_kpis(items: list[tuple[str, str, str, bool]]) -> None:
    for col, (lab, val, sub, principal) in zip(st.columns(len(items)), items):
        with col:
            kpi(lab, val, sub, principal)
    st.write("")


def lectura(html: str) -> None:
    st.markdown(f'<div class="kof-lectura">{html}</div>', unsafe_allow_html=True)


def grafico(fig: go.Figure, alto: int = 380) -> None:
    fig.update_layout(template="kof", height=alto, title_x=0, title_xanchor="left")
    fig.update_traces(cliponaxis=False, selector=dict(type="bar"))
    st.plotly_chart(fig, width="stretch", theme=None, config={"displayModeBar": False})


def siguiente(ruta: str, texto: str) -> None:
    st.page_link(ruta, label=texto, icon=":material/arrow_forward:")


def pie() -> None:
    st.markdown('<div class="kof-pie">Proyecto final de Machine Learning · Universidad Libre. '
                'Datos simulados con fines académicos: no provienen de FEMSA, Postobón '
                'ni de tiendas reales.</div>', unsafe_allow_html=True)
