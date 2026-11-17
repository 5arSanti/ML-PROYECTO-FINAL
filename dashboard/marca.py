"""Identidad visual (inspirada en Coca-Cola FEMSA), formato es-CO y componentes."""
from __future__ import annotations

import math

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

ROJO = "#C42A32"
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

TIPO_UI = "IBM Plex Sans, Helvetica Neue, Helvetica, Arial, sans-serif"
TIPO_TITULO = "Source Serif 4, 'Source Serif Pro', Georgia, 'Times New Roman', serif"

pio.templates["kof"] = go.layout.Template(layout=dict(
    font=dict(family=TIPO_UI, color=NEGRO, size=13),
    colorway=[ROJO, GRIS_OSCURO, GRIS, GRIS_CLARO],
    paper_bgcolor="white",
    plot_bgcolor="white",
    separators=",.",
    title=dict(x=0, xanchor="left", font=dict(family=TIPO_TITULO, size=16, color=NEGRO, weight=600)),
    xaxis=dict(gridcolor="#EEEAE6", zeroline=False, linecolor=GRIS_CLARO, title_font_size=12,
               automargin=True),
    yaxis=dict(gridcolor="#EEEAE6", zeroline=False, linecolor=GRIS_CLARO, title_font_size=12,
               automargin=True),
    hoverlabel=dict(bgcolor=NEGRO, font_color="white", bordercolor=NEGRO),
    legend=dict(orientation="h", yanchor="top", y=-0.15, x=0),
    margin=dict(l=10, r=10, t=50, b=10),
))

# Isotipo propio: nevera comercial con franja roja. No es el logotipo de Coca-Cola FEMSA.
ISOTIPO = """<svg class="kof-isotipo" viewBox="0 0 48 64" aria-hidden="true">
  <rect x="7" y="3" width="34" height="58" rx="1.5" fill="#fff" stroke="#111" stroke-width="2.4"/>
  <rect x="7" y="3" width="7" height="58" fill="#E41E2B"/>
  <rect x="20" y="14" width="15" height="1.8" fill="#D9D5D0"/>
  <rect x="20" y="20" width="15" height="1.8" fill="#D9D5D0"/>
  <rect x="20" y="26" width="11" height="1.8" fill="#D9D5D0"/>
  <rect x="36.5" y="24" width="2.8" height="11" fill="#111"/>
</svg>"""

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:wght@600;700&display=swap');
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
[data-testid="stMarkdown"], [data-testid="stWidgetLabel"] {{
  font-family: {TIPO_UI};
}}
::selection {{ background: {ROJO}; color: #fff; }}
header[data-testid="stHeader"] {{
  background: {ROJO};
  height: 4px;
  min-height: 4px;
}}
header[data-testid="stHeader"] * {{ display: none; }}
[data-testid="stToolbar"], [data-testid="stDecoration"],
.stDeployButton, #MainMenu {{ display: none !important; }}
section[data-testid="stSidebar"] {{
  background: {FONDO_SUAVE};
  border-right: 1px solid {GRIS_CLARO};
}}
[data-testid="stSidebarHeader"] {{
  background: {ROJO};
  margin: -1.15rem -1.5rem 0.75rem;
  padding: 16px 18px 14px;
}}
[data-testid="stSidebarHeader"] img,
img[data-testid="stSidebarLogo"] {{
  height: 96px !important;
  max-height: 96px !important;
  width: auto !important;
  object-fit: contain;
}}
[data-testid="stSidebarCollapseButton"] svg {{
  fill: #fff;
  color: #fff;
}}
[data-testid="stLogoSpacer"] {{
  min-height: 0;
}}
.kof-marca {{
  display: flex; align-items: center; gap: 10px;
  margin: 2px 0 18px; padding-bottom: 14px;
  border-bottom: 1px solid {GRIS_CLARO};
}}
.kof-isotipo {{ width: 28px; height: 38px; flex: 0 0 28px; display: block; }}
.kof-cliente {{ font-size: .68rem; font-weight: 600; color: {ROJO}; }}
.kof-producto {{ font-family: {TIPO_TITULO}; font-size: 1.12rem; font-weight: 700;
  color: {NEGRO}; line-height: 1.15; margin-top: 1px; }}
.kof-meta {{ font-size: .72rem; color: {GRIS_OSCURO}; margin-top: 2px; }}
.kof-titulo {{ font-family: {TIPO_TITULO}; font-size: 2.05rem; font-weight: 700;
  color: {NEGRO}; letter-spacing: -.02em; line-height: 1.18; margin: 4px 0 8px; }}
.kof-contexto {{ font-size: .88rem; color: {GRIS_OSCURO}; margin: -2px 0 10px; }}
.kof-bajada {{ font-size: 1.02rem; color: #3F3A36; max-width: 42rem; margin: 0 0 22px;
  line-height: 1.45; }}
.kof-kpi {{ background: #fff; border: 1px solid {GRIS_CLARO}; border-radius: 2px;
  padding: 12px 14px; height: 100%; }}
.kof-kpi .lab {{ font-size: .72rem; color: {GRIS_OSCURO}; font-weight: 500; }}
.kof-kpi .val {{ font-size: 1.55rem; font-weight: 600; color: {NEGRO}; line-height: 1.2;
  margin-top: 4px; font-variant-numeric: tabular-nums; }}
.kof-kpi .sub {{ font-size: .80rem; color: {GRIS_OSCURO}; margin-top: 2px; }}
.kof-kpi.principal .val {{ color: {ROJO}; }}
.kof-lectura {{ background: {FONDO_SUAVE}; border-top: 1px solid {ROJO};
  padding: 12px 16px; margin: 8px 0 20px; color: #2B2724; font-size: .95rem; }}
.kof-lectura b {{ color: {NEGRO}; }}
.kof-pie {{ font-size: .76rem; color: {GRIS}; border-top: 1px solid {GRIS_CLARO};
  margin-top: 32px; padding-top: 10px; max-width: 46rem; }}
</style>
"""

WORDMARK = (
    f'<div class="kof-marca">{ISOTIPO}<div>'
    '<div class="kof-cliente">Coca-Cola FEMSA</div>'
    '<div class="kof-producto">Plan de neveras</div>'
    '<div class="kof-meta">Analítica comercial · Universidad Libre</div>'
    "</div></div>"
)


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


def encabezado(contexto: str, titulo: str, bajada: str = "") -> None:
    html = f'<div class="kof-titulo">{titulo}</div>'
    if contexto and not contexto.casefold().startswith("operaci"):
        html += f'<div class="kof-contexto">{contexto}</div>'
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
    st.page_link(ruta, label=texto)


def pie() -> None:
    st.markdown('<div class="kof-pie">Proyecto final de Machine Learning · Universidad Libre. '
                'Datos simulados con fines académicos: no provienen de FEMSA, Postobón '
                'ni de tiendas reales.</div>', unsafe_allow_html=True)
