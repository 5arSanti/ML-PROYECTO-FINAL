from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "dashboard" / "app.py")
PAGINAS = [
    "paginas/r1_analisis.py", "paginas/r2_preparacion.py", "paginas/r3_ventas.py",
    "paginas/r4_efecto.py", "paginas/r5_riesgo.py", "paginas/r6_decision.py",
    "paginas/o1_tablero.py", "paginas/o2_reglas.py", "paginas/o3_senales.py",
    "paginas/o4_escenarios.py", "paginas/o5_tienda.py",
]


def abrir(pagina: str) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    at.switch_page(pagina)
    at.run()
    assert not at.exception, at.exception
    return at


def textos(at: AppTest) -> str:
    partes = [m.value for m in at.markdown] + [s.value for s in at.subheader]
    partes += [c.value for c in at.caption] + [c.value for c in at.sidebar.caption]
    return "\n".join(partes)


@pytest.mark.parametrize("pagina", PAGINAS)
def test_pagina_carga_sin_errores(pagina):
    abrir(pagina)


def test_r1_muestra_la_recomendacion():
    assert "254,4 MM" in textos(abrir("paginas/r1_analisis.py"))


def test_r2_muestra_los_tres_conjuntos():
    assert "Tres conjuntos, tres preguntas" in textos(abrir("paginas/r2_preparacion.py"))


def test_r3_muestra_r2_de_prueba():
    assert "0,706" in textos(abrir("paginas/r3_ventas.py"))


def test_r4_cambia_con_la_cifra_elegida():
    at = abrir("paginas/r4_efecto.py")
    assert "+27,1 %" in textos(at)
    at.segmented_control[0].set_value("Diferencia simple")
    at.run()
    assert not at.exception, at.exception
    assert "las 12.700" in textos(at)


def test_r5_muestra_el_umbral():
    assert "Umbral por costos" in textos(abrir("paginas/r5_riesgo.py"))


def test_r6_cambia_con_la_estrategia():
    at = abrir("paginas/r6_decision.py")
    at.segmented_control[0].set_value("Mayores ventas")
    at.run()
    assert not at.exception, at.exception
    assert "211,9 MM" in textos(at)


def test_o1_prioridad_de_retencion_nacional():
    assert "51 tiendas" in textos(abrir("paginas/o1_tablero.py"))


def test_o1_filtro_region():
    at = abrir("paginas/o1_tablero.py")
    at.multiselect(key="f_regiones").set_value(["Caribe"])
    at.run()
    assert not at.exception, at.exception
    assert "494 tiendas en vista" in textos(at)


def test_o2_solape_nacional():
    assert "Coinciden 640 tiendas" in textos(abrir("paginas/o2_reglas.py"))


def test_o3_tres_paneles():
    t = textos(abrir("paginas/o3_senales.py"))
    for titulo in ("Ventas de hoy", "Dónde rinde más una nevera", "Quién se puede ir"):
        assert titulo in t


def test_o4_escenario_margen():
    at = abrir("paginas/o4_escenarios.py")
    assert "254,4 MM" in textos(at)
    at.slider[0].set_value(20)
    at.run()
    assert not at.exception, at.exception
    assert "191,5 MM" in textos(at)


def test_o5_consulta_tienda():
    at = abrir("paginas/o5_tienda.py")
    at.selectbox[0].set_value("T20612")
    at.run()
    assert not at.exception, at.exception
    assert "Instalar" in textos(at)
