import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dashboard"))

import marca  # noqa: E402


@pytest.mark.parametrize("funcion, valor, esperado", [
    (marca.cop, 254_389_976, "$ 254.389.976"),
    (marca.mm, 254_389_976, "254,4 MM"),
    (marca.pct, 27.085, "27,1 %"),
    (marca.num, 12_700, "12.700"),
    (marca.dec, 0.40208, "0,402"),
    (marca.cop, float("nan"), "—"),
])
def test_formato_es_co(funcion, valor, esperado):
    assert funcion(valor) == esperado


def test_etiqueta_conocida_y_desconocida():
    assert marca.etiqueta("clientes_prom_dia") == "Clientes por día"
    assert marca.etiqueta("otra_variable") == "Otra variable"


def test_wordmark_nombra_al_cliente():
    assert "Coca-Cola FEMSA" in marca.WORDMARK
    assert "Plan de neveras" in marca.WORDMARK
