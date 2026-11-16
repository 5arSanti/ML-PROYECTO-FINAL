import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dashboard"))

import datos  # noqa: E402

@pytest.fixture(scope="module")
def df():
    return datos.cargar_tiendas()


@pytest.fixture(scope="module")
def kpis():
    return datos.kpis_nacionales()


def test_carga_tiendas_agrega_banderas(df):
    assert len(df) == 12_700
    assert df["es_seleccionada"].sum() == 1_000
    assert {"es_rentable", "en_ventas", "en_trafico", "es_alto"} <= set(df.columns)


def test_archivo_faltante_lanza_error_claro():
    with pytest.raises(datos.DatosFaltantes, match="salidas/no_existe.csv"):
        datos.leer_csv("no_existe.csv")


def test_resumen_vista_sin_filtros_coincide_con_kpis(df, kpis):
    r = datos.resumen_vista(df, datos.Filtros(), kpis)
    assert r["tiendas"] == 1_000
    assert r["ganancia_total"] == pytest.approx(254_389_976, abs=1)
    assert r["riesgo_alto"] == 132
    assert r["retorno"] == pytest.approx(4.24, abs=0.01)


def test_filtro_region_cuadra_con_tablero_por_region(df):
    por_region = datos.leer_csv("tablero_por_region.csv").set_index("region")
    vista = datos.aplicar_filtros(df, datos.Filtros(regiones=("Caribe",)))
    assert len(vista) == por_region.loc["Caribe", "tiendas"]
    assert vista["ganancia_estimada_cop_mes"].sum() == por_region.loc["Caribe", "ganancia_total"]


def test_universo_elegibles_incluye_no_seleccionadas(df):
    vista = datos.aplicar_filtros(df, datos.Filtros(universo="elegibles"))
    assert len(vista) == 12_700


def test_agrupar_por_region_suma_la_lista(df):
    g = datos.agrupar(df[df["es_seleccionada"]], "region")
    assert g["tiendas"].sum() == 1_000
    assert g.iloc[0]["region"] == "Caribe"


def test_comparar_reglas_nacional_usa_csv(df):
    r = datos.comparar_reglas(df, datos.Filtros()).set_index("estrategia")
    assert r.loc["Lista causal", "ganancia_total"] == 254_389_976
    assert r.loc["Mayores ventas", "ganancia_total"] == 211_940_862
    assert r.loc["Mayor tráfico", "ganancia_total"] == 164_389_564
    assert r.loc["Mayores ventas", "no_rentables"] == 38
    assert not r["esperado"].any()


def test_comparar_reglas_con_recorte_usa_banderas(df):
    r = datos.comparar_reglas(df, datos.Filtros(regiones=("Caribe",))).set_index("estrategia")
    assert r.loc["Lista causal", "tiendas"] == 494
    assert r.loc["Selección aleatoria", "esperado"]
    assert r.loc["Lista causal", "ganancia_total"] > r.loc["Mayores ventas", "ganancia_total"]


def test_solape_nacional(df):
    s = datos.solape(df)
    assert (s["ambas"], s["solo_causal"], s["solo_ventas"]) == (640, 360, 360)
    assert s["perfil_causal"]["temperatura"] == pytest.approx(26.7, abs=0.05)
    assert s["perfil_ventas"]["temperatura"] == pytest.approx(19.4, abs=0.05)


def test_etiquetar_solape_solo_union(df):
    sol = datos.etiquetar_solape(df)
    assert len(sol) == 1_360
    assert set(sol["grupo"]) == {"Ambas", "Solo lista causal", "Solo regla de ventas"}


def test_mitad_de_la_ganancia(df):
    lista = df[df["es_seleccionada"]]
    assert datos.tiendas_para_mitad(lista["ganancia_estimada_cop_mes"]) == 289


def test_efecto_por_temperatura(df):
    t = datos.efecto_por_temperatura(df)
    assert list(t["banda"].astype(str)) == list(datos.BANDAS_TEMPERATURA[1])
    assert t["efecto"].iloc[0] == pytest.approx(15.5, abs=0.1)
    assert t["efecto"].iloc[-1] == pytest.approx(45.1, abs=0.1)


def test_cuadrantes_prioridad(df):
    c = datos.cuadrantes_riesgo(df[df["es_seleccionada"]])
    assert (c["cuadrante"] == "Prioridad de retención").sum() == 51


def test_escenario_base_reproduce_sensibilidad(df):
    e = datos.escenario(df)
    assert e.ganancia_total == pytest.approx(254_389_976, abs=1)
    assert e.coincidencias == 1_000
    assert e.rentables == 4_516
    assert len(e.ganancias_ordenadas) == 12_700


@pytest.mark.parametrize("kwargs, esperado", [
    ({"margen": 0.20}, 191_511_981),
    ({"costo": 90_000}, 224_389_976),
    ({"recorte_efecto": 0.25}, 175_792_482),
])
def test_escenario_sensibilidades(df, kwargs, esperado):
    assert datos.escenario(df, **kwargs).ganancia_total == pytest.approx(esperado, abs=1)


def test_buscar_tienda(df):
    assert datos.buscar_tienda(df, " t20612 ")["ranking"] == 1
    assert datos.buscar_tienda(df, "NOEXISTE") is None


def test_percentil():
    assert datos.percentil(pd.Series([1, 2, 3, 4]), 2) == 50.0
