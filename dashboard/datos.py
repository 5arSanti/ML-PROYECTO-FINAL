"""Carga de salidas/ y cálculos del tablero. No depende de Streamlit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
SALIDAS = RAIZ / "salidas"

MARGEN = 0.25
COSTO_NEVERA = 60_000
N_NEVERAS = 1_000
UMBRAL_RIESGO = 0.25
VALOR_EVITAR_CAMBIO = 500_000
COSTO_RETENCION = 50_000
EFECTIVIDAD_RETENCION = 0.40
PREVALENCIA_CAMBIO = 0.095
TRAFICO_EXTRA_PCT = 29
DIFERENCIA_SIMPLE_COP = 748_474
IC_EFECTO_PCT = (25.8, 28.4)
COLUMNAS_BASE = 109

EMBUDO = (
    ("Base", 38_000),
    ("Con nevera FEMSA (no elegibles)", 25_069),
    ("Sin nevera FEMSA", 12_931),
    ("Nevera Postobón y menos de 12 m²", 231),
    ("Elegibles", 12_700),
    ("Neveras a instalar", 1_000),
)

CONJUNTOS = (
    ("Variables de ventas", "¿Cuánto vende una tienda tal como está?",
     "50 columnas de fuga directa y 4 resultados simultáneos"),
    ("Variables causales", "¿Cuánto añade una nevera nueva?",
     "Lo anterior y 6 variables de la nevera FEMSA"),
    ("Variables de riesgo", "¿Quién cambia de proveedor en seis meses?",
     "Solo el identificador y el propio objetivo"),
)

SUPUESTOS = (
    ("Ignorabilidad", "Si la asignación original usó un criterio que no está en la base, "
                      "el efecto seguiría sesgado."),
    ("Un solo mes", "No hay línea de base previa, de modo que no se puede usar "
                    "diferencias en diferencias."),
    ("SUTVA", "Instalar 1.000 neveras puede mover a la competencia o canibalizar tiendas vecinas."),
    ("Datos simulados", "Las cifras no son un resultado comercial de FEMSA ni de Postobón."),
)

COLUMNAS_TIENDAS = (
    "id_tienda", "region", "ciudad", "zona", "tipo_negocio", "latitud", "longitud", "estrato",
    "temperatura_media_c", "clientes_prom_dia", "ventas_femsa_cop_mes", "efecto_pct_ventas",
    "ventas_adicionales_cop_mes", "ganancia_estimada_cop_mes", "ranking", "seleccionada",
    "prob_cambio", "riesgo_cambio", "rentable", "en_regla_ventas", "en_regla_trafico",
)

BANDAS_TEMPERATURA = (
    (0, 16, 20, 24, 28, 50),
    ("< 16 °C", "16-20 °C", "20-24 °C", "24-28 °C", "> 28 °C"),
)

ESTRATEGIAS = ("Lista causal", "Mayores ventas", "Mayor tráfico", "Selección aleatoria")

COLUMNAS_DETALLE = (
    "id_tienda", "ganancia_estimada_cop_mes", "riesgo_cambio", "prob_cambio", "ranking",
    "region", "ciudad", "tipo_negocio", "zona", "efecto_pct_ventas", "ventas_femsa_cop_mes",
)


class DatosFaltantes(RuntimeError):
    """Falta un archivo de salidas/ o una columna esperada."""


def leer_csv(nombre: str) -> pd.DataFrame:
    ruta = SALIDAS / nombre
    if not ruta.exists():
        raise DatosFaltantes(f"Falta el archivo salidas/{nombre}.")
    return pd.read_csv(ruta)


def cargar_tiendas() -> pd.DataFrame:
    df = leer_csv("tablero_tiendas.csv")
    faltan = [c for c in COLUMNAS_TIENDAS if c not in df.columns]
    if faltan:
        raise DatosFaltantes(
            f"A salidas/tablero_tiendas.csv le faltan columnas: {', '.join(faltan)}.")
    df = df.copy()
    for origen, destino in (("seleccionada", "es_seleccionada"), ("rentable", "es_rentable"),
                            ("en_regla_ventas", "en_ventas"), ("en_regla_trafico", "en_trafico")):
        df[destino] = df[origen].eq("Sí")
    df["es_alto"] = df["riesgo_cambio"].eq("Alto")
    return df


def kpis_nacionales() -> dict[str, float]:
    k = leer_csv("tablero_kpis.csv")
    return dict(zip(k["indicador"], k["valor"].astype(float)))


@dataclass(frozen=True)
class Filtros:
    regiones: tuple[str, ...] = ()
    ciudades: tuple[str, ...] = ()
    tipos: tuple[str, ...] = ()
    zonas: tuple[str, ...] = ()
    riesgo: str = "Todos"
    universo: str = "seleccionadas"

    def recorte_activo(self) -> bool:
        return bool(self.regiones or self.ciudades or self.tipos or self.zonas
                    or self.riesgo != "Todos")


def recortar(df: pd.DataFrame, f: Filtros) -> pd.DataFrame:
    m = pd.Series(True, index=df.index)
    if f.regiones:
        m &= df["region"].isin(f.regiones)
    if f.ciudades:
        m &= df["ciudad"].isin(f.ciudades)
    if f.tipos:
        m &= df["tipo_negocio"].isin(f.tipos)
    if f.zonas:
        m &= df["zona"].isin(f.zonas)
    if f.riesgo == "Alto":
        m &= df["es_alto"]
    elif f.riesgo == "Bajo":
        m &= ~df["es_alto"]
    return df[m]


def aplicar_filtros(df: pd.DataFrame, f: Filtros) -> pd.DataFrame:
    r = recortar(df, f)
    return r[r["es_seleccionada"]] if f.universo == "seleccionadas" else r


def resumen(df: pd.DataFrame) -> dict[str, float]:
    n = len(df)
    total = float(df["ganancia_estimada_cop_mes"].sum())
    return {
        "tiendas": n,
        "ganancia_total": total,
        "ganancia_media": total / n if n else 0.0,
        "riesgo_alto": int(df["es_alto"].sum()),
        "retorno": total / (n * COSTO_NEVERA) if n else 0.0,
        "ventas_adicionales": float(df["ventas_adicionales_cop_mes"].sum()),
    }


def resumen_vista(df: pd.DataFrame, f: Filtros, kpis: dict[str, float]) -> dict[str, float]:
    r = resumen(aplicar_filtros(df, f))
    if not f.recorte_activo() and f.universo == "seleccionadas":
        r["ganancia_total"] = kpis["Ganancia mensual total estimada"]
        r["ganancia_media"] = kpis["Ganancia promedio por tienda"]
        r["retorno"] = kpis["Retorno sobre el costo"]
    return r


def agrupar(df: pd.DataFrame, columna: str) -> pd.DataFrame:
    return (df.groupby(columna, observed=True)
              .agg(tiendas=("id_tienda", "size"),
                   ganancia_total=("ganancia_estimada_cop_mes", "sum"),
                   riesgo_alto=("es_alto", "sum"))
              .reset_index()
              .sort_values("ganancia_total", ascending=False, ignore_index=True))


def comparar_reglas(df: pd.DataFrame, f: Filtros) -> pd.DataFrame:
    if not f.recorte_activo():
        c = leer_csv("comparacion_reglas.csv")
        return pd.DataFrame({
            "estrategia": ESTRATEGIAS,
            "tiendas": [N_NEVERAS] * 4,
            "ganancia_total": c["ganancia_total_mes"].round().astype(int).to_numpy(),
            "no_rentables": c["tiendas_no_rentables"].astype(int).to_numpy(),
            "riesgo_alto": c["riesgo_alto"].astype(int).to_numpy(),
            "esperado": [False] * 4,
        })
    r = recortar(df, f)
    g = r["ganancia_estimada_cop_mes"]
    filas = []
    for nombre, mascara in zip(ESTRATEGIAS[:3], (r["es_seleccionada"], r["en_ventas"], r["en_trafico"])):
        s = r[mascara]
        filas.append({
            "estrategia": nombre,
            "tiendas": len(s),
            "ganancia_total": int(s["ganancia_estimada_cop_mes"].sum()),
            "no_rentables": int((s["ganancia_estimada_cop_mes"] <= 0).sum()),
            "riesgo_alto": int(s["es_alto"].sum()),
            "esperado": False,
        })
    n = filas[0]["tiendas"]
    hay = len(r) > 0
    filas.append({
        "estrategia": ESTRATEGIAS[3],
        "tiendas": n,
        "ganancia_total": int(round(n * g.mean())) if hay else 0,
        "no_rentables": int(round(n * (g <= 0).mean())) if hay else 0,
        "riesgo_alto": int(round(n * r["es_alto"].mean())) if hay else 0,
        "esperado": True,
    })
    return pd.DataFrame(filas)


def _perfil(s: pd.DataFrame) -> dict[str, float]:
    return {
        "temperatura": float(s["temperatura_media_c"].mean()),
        "ventas": float(s["ventas_femsa_cop_mes"].mean()),
        "clientes": float(s["clientes_prom_dia"].mean()),
        "ganancia": float(s["ganancia_estimada_cop_mes"].mean()),
    }


def solape(df_recorte: pd.DataFrame) -> dict:
    c = df_recorte["es_seleccionada"]
    v = df_recorte["en_ventas"]
    solo_c = df_recorte[c & ~v]
    solo_v = df_recorte[v & ~c]
    return {
        "ambas": int((c & v).sum()),
        "solo_causal": len(solo_c),
        "solo_ventas": len(solo_v),
        "perfil_causal": _perfil(solo_c),
        "perfil_ventas": _perfil(solo_v),
    }


def etiquetar_solape(df_recorte: pd.DataFrame) -> pd.DataFrame:
    c = df_recorte["es_seleccionada"]
    v = df_recorte["en_ventas"]
    grupo = np.select([c & v, c & ~v, ~c & v],
                      ["Ambas", "Solo lista causal", "Solo regla de ventas"], default="")
    out = df_recorte.assign(grupo=grupo)
    return out[out["grupo"] != ""]


def ganancia_acumulada(ganancias) -> pd.DataFrame:
    g = np.sort(np.asarray(ganancias, dtype=float))[::-1]
    return pd.DataFrame({"posicion": np.arange(1, len(g) + 1), "acumulada": np.cumsum(g)})


def tiendas_para_mitad(ganancias) -> int:
    c = ganancia_acumulada(ganancias)["acumulada"].to_numpy()
    return int(np.searchsorted(c, c[-1] / 2) + 1)


def efecto_por_temperatura(df: pd.DataFrame) -> pd.DataFrame:
    cortes, etiquetas = BANDAS_TEMPERATURA
    banda = pd.cut(df["temperatura_media_c"], list(cortes), labels=list(etiquetas))
    return (df.assign(banda=banda)
              .groupby("banda", observed=True)
              .agg(efecto=("efecto_pct_ventas", "mean"), tiendas=("id_tienda", "size"))
              .reset_index())


def cuadrantes_riesgo(df: pd.DataFrame) -> pd.DataFrame:
    g = df["ganancia_estimada_cop_mes"]
    alta = g > g.median()
    alto = df["es_alto"]
    cuadrante = np.select(
        [alta & alto, alta & ~alto, ~alta & alto],
        ["Prioridad de retención", "Alta ganancia, riesgo bajo", "Baja ganancia, riesgo alto"],
        default="Baja ganancia, riesgo bajo")
    return df.assign(cuadrante=cuadrante)


@dataclass(frozen=True)
class ResultadoEscenario:
    ganancia_total: float
    rentables: int
    ultima: float
    coincidencias: int
    ganancias_ordenadas: np.ndarray


def escenario(df: pd.DataFrame, margen: float = MARGEN, costo: float = COSTO_NEVERA,
              n: int = N_NEVERAS, recorte_efecto: float = 0.0) -> ResultadoEscenario:
    g = margen * df["ventas_adicionales_cop_mes"].to_numpy(dtype=float) * (1 - recorte_efecto) - costo
    orden = np.argsort(-g, kind="stable")
    top = orden[:n]
    oficial = set(df.loc[df["es_seleccionada"], "id_tienda"])
    elegidas = set(df["id_tienda"].to_numpy()[top])
    return ResultadoEscenario(
        ganancia_total=float(g[top].sum()),
        rentables=int((g > 0).sum()),
        ultima=float(g[top[-1]]),
        coincidencias=len(oficial & elegidas),
        ganancias_ordenadas=g[orden],
    )


def buscar_tienda(df: pd.DataFrame, id_tienda: str) -> pd.Series | None:
    fila = df[df["id_tienda"] == id_tienda.strip().upper()]
    return None if fila.empty else fila.iloc[0]


def percentil(serie: pd.Series, valor: float) -> float:
    return float((serie <= valor).mean() * 100)
