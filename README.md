# Proyecto final de Machine Learning. Plan de neveras FEMSA

**Integrantes:** Rebeca Pedrozo Cueto · Daniela Fierro · Johel Santiago Arias Becerra

**Curso:** Machine Learning 2026-II

**Docente:** Gustavo Santos

**Tablero:** [Plan de Neveras en Streamlit](https://plan-neveras-femsa.streamlit.app)

¿En cuáles 1.000 tiendas debe FEMSA instalar sus 1.000 neveras nuevas, y cuánto ganaría cada mes?

Este repositorio tiene el programa completo: un cuaderno que corre de principio a fin desde la base original
y produce la lista de tiendas, la estimación de ganancia y todos los insumos del tablero, más la aplicación
Streamlit que presenta el recorrido y la operación.

---

## Resultado

| | |
|---|---|
| Tiendas elegidas | 1.000 de 12.700 elegibles |
| Ganancia mensual estimada | alrededor de COP 254 millones (unos COP 3.050 millones al año) |
| Retorno sobre el costo de las neveras | cerca de 4,2 veces |
| Método del efecto | DR-learner (doblemente robusto) con cross-fitting |
| Efecto causal de la nevera | +27 % sobre las ventas (IC 95 %: +25,8 % a +28,4 %) |
| Ventaja sobre la mejor regla simple | +20 % de ganancia, unos COP 42 millones al mes |

Las cifras exactas de cada corrida quedan impresas en el resumen ejecutivo del módulo 7 del cuaderno y en
`salidas/tablero_kpis.csv`. Aquí van redondeadas a propósito, porque entre versiones de scikit-learn los
resultados se mueven algunas décimas.

El núcleo del proyecto está en una sola comparación. La diferencia simple de promedios entre tiendas con y
sin nevera es de COP 748.000 al mes, y el efecto causal es de unos COP 275.000. La diferencia simple
sobreestima el efecto en más del 170 %, y cerca del 63 % de ella no es efecto de la nevera: es que FEMSA
puso sus neveras en las mejores tiendas.

Eso cambia la decisión por completo. Con la diferencia simple, cada tienda elegible parecería rendir
COP 127.000 al mes y las 12.700 serían rentables. Con el efecto causal, la ganancia promedio de una elegible
es de unos COP 8.700 y solo unas 4.500 se pagan la nevera.

---

## Cómo correrlo

El cuaderno está guardado con sus resultados y sus gráficos, así que se puede leer sin ejecutarlo.

### Opción A, Google Colab (recomendada)

1. Abrir el cuaderno en
   [Colab](https://colab.research.google.com/github/5arSanti/ML-PROYECTO-FINAL/blob/main/proyecto_final_neveras.ipynb).
2. Subir `base_refrescos_nevera.csv` al entorno con el ícono de carpeta, opción *Subir*. Si prefieren Drive,
   ajustar `RUTA_DRIVE` en el módulo 0.
3. **Entorno de ejecución → Ejecutar todo**.
4. La celda 7.6 descarga el entregable y un zip con toda la carpeta `salidas/`.

Tarda entre 8 y 12 minutos en una instancia estándar de Colab, sin GPU.

> Hay que correrlo en orden. Los conjuntos de variables del módulo 2 se arman con las columnas que existen
> en ese momento, así que re-ejecutar esas celdas después del módulo 5 cambiaría lo que ven los modelos.

### Opción B, local

```bash
pip install -r requirements.txt
jupyter notebook proyecto_final_neveras.ipynb
```

El cuaderno busca la base en `datos/base_refrescos_nevera.csv` o en el directorio actual. Necesita
scikit-learn 1.4 o superior, porque usa `root_mean_squared_error`.

### Tablero

El tablero lee solo la carpeta `salidas/`: si se vuelve a correr el cuaderno, toma las cifras nuevas.
Tiene dos bloques: *Recorrido*, seis pantallas que presentan el proyecto módulo por módulo, y
*Operación*, con filtros por región, ciudad y tipo de negocio, mapa de las 1.000 tiendas, comparación
con reglas simples, riesgo de cambio, importancia de variables, escenarios y consulta por `id_tienda`.

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

## Estructura

```
├── proyecto_final_neveras.ipynb       Programa completo (módulos 0 a 7)
├── requirements.txt                   Dependencias del cuaderno y del tablero
├── dashboard/                         Tablero Streamlit (app.py y páginas)
├── tests/                             Pruebas del tablero (pytest)
├── datos/
│   ├── base_refrescos_nevera.csv      Base original: 38.000 tiendas x 109 columnas
│   └── diccionario_base_tiendas.xlsx  Diccionario de variables (referencia, el cuaderno no lo lee)
├── salidas/                           Resultados de la corrida final (21 archivos)
│   ├── lista_grupoDaniJohelRebe.csv   Entregable: las 1.000 tiendas
│   ├── tablero_tiendas.csv            Insumo principal del tablero (12.700 filas)
│   ├── tablero_kpis.csv               Indicadores de resumen
│   └── ...                            Métricas, importancias, validaciones, sensibilidades
└── README.md
```

---

## Los módulos

El módulo 0 configura y valida la base, y el 7 exporta los resultados. Los seis módulos de análisis son:

| Módulo | Qué hace | Hallazgo principal |
|---|---|---|
| 1. Análisis exploratorio | Describe tiendas, ventas y neveras | Las ventas son log-normales, y las tiendas con nevera ya tenían 29 % más tráfico antes de recibirla |
| 2. Preparación de datos | Define variables y controla la fuga | Verifica numéricamente que 50 columnas contienen la respuesta, y define tres conjuntos de variables |
| 3. Modelo de ventas | 4 algoritmos con validación cruzada | Gradient Boosting con R² de 0,71 en test contra 0,66 del base lineal |
| 4. Efecto de la nevera | 5 estimadores causales y validación GATE | Efecto del 27 %, muy heterogéneo: de +4 % a +62 % según la tienda |
| 5. Riesgo de cambio | 3 modelos, desbalance, umbral por costos | ROC-AUC 0,82 y PR-AUC 0,40, con umbral económico en 0,25 y no en 0,5 |
| 6. Decisión | Las 1.000 tiendas y la ganancia | Unos COP 254 millones al mes, un 20 % más que la mejor regla simple |

### El hallazgo que resume el proyecto

Nuestra lista y la regla de "mayores ventas" comparten unas 640 tiendas. Las 360 que las separan: las que
solo elige el modelo están a 26,7 °C de media, venden COP 1,5 millones y dejan unos COP 178.000 de ganancia;
las que solo elige la regla de ventas están a 19,4 °C, venden COP 2,2 millones y dejan unos COP 60.000.

La regla de ventas escoge tiendas con COP 700.000 más de venta mensual y obtiene cerca de tres veces menos
ganancia. Está pagando por tamaño en ciudades frías, donde una nevera añade poco.

---

## Decisiones de modelación que vale la pena conocer

**1. Todo en logaritmo.** `log(ventas)` es casi perfectamente simétrico, con asimetría de 0,0 frente a 4,4
en niveles. El efecto de la nevera se comporta como un porcentaje y no como un monto fijo: por eso el mismo
27 % vale COP 90.000 en una tienda pequeña y COP 900.000 en una grande.

**2. El tratamiento se define con precisión.** El grupo con nevera de la base mezcla configuraciones: 1 o 2
neveras, de 1, 2 o 4 puertas, de 0 a 15 años, y unas 3.800 tiendas con la nevera averiada. Como FEMSA
instalará una nevera nueva y operativa, el análisis compara contra tiendas con exactamente esa
configuración. La sensibilidad muestra que la conclusión no depende de esa decisión: usar todas las tratadas,
o quedarse solo con las neveras de hasta 2 años, mueve el efecto menos de dos puntos porcentuales.

**3. Control de fuga en tres niveles.** Se excluyen las columnas que suman a la respuesta, verificado con
`np.allclose`, los resultados simultáneos (las ventas de Postobón del mismo mes están afectadas por el
tratamiento, y condicionar sobre ellas sesga el efecto) y las variables que describen la nevera FEMSA, que
son funciones determinísticas del tratamiento.

**4. Línea base observada.** Para una tienda elegible, que hoy no tiene nevera, sus ventas observadas son su
contrafactual sin nevera. No hay que predecirlas. Eso elimina el error de la línea base y deja solo la
incertidumbre del multiplicador.

**5. El modelo causal se valida ordenando, no prediciendo.** El efecto individual no es observable, así que
no hay R² posible. Lo que sí se puede validar es el orden: agrupamos las tiendas por decil de efecto
predicho y estimamos el efecto real de cada decil con el estimador doble robusto, que no usa el modelo de
efectos. Las dos series se correlacionan por encima de 0,98 y el decil superior tiene un efecto doce veces
mayor que el inferior. El balance de covariables pasa de un |SMD| máximo de 0,45 a 0,03 tras el ajuste, y el
propensity score se mantiene entre 0,08 y 0,88, sin problemas de positividad.

**6. El umbral de riesgo sale de los costos, no de 0,5.** Conviene actuar cuando
`0,40 × p × 500.000 > 50.000`, es decir `p > 0,25`. En los datos ese umbral teórico rinde unos COP 124
millones contra COP 126 millones del óptimo empírico, que está en 0,24: un 1 % de diferencia. El umbral que
sale de los costos es, en la práctica, el óptimo.

---

## Reproducibilidad

- Semilla fija `SEED = 42` en todos los modelos, particiones y validaciones cruzadas.
- Los mapas de categorías se fijan de forma explícita en `MAPAS_CAT`, así que la codificación no depende del
  orden de las filas.
- Dos corridas seguidas en el mismo entorno producen los mismos 1.000 `id_tienda` y las mismas cifras. Entre
  versiones distintas de scikit-learn los resultados se mueven algunas décimas, así que los textos citan
  cifras redondeadas y el detalle exacto queda impreso debajo de cada celda.
- El cuaderno valida la base al cargarla (38.000 filas, 109 columnas, 0 faltantes, 0 duplicados) y valida el
  entregable antes de escribirlo: exactamente 1.000 filas, sin repetidos y todas elegibles.

## Limitaciones

- **Ignorabilidad no verificable.** Si FEMSA usó un criterio que no está en la base al decidir dónde poner
  sus neveras, el efecto estimado seguiría sesgado. El balance de covariables después del ajuste no descarta
  eso.
- **Un solo mes.** Sin una línea de base previa no se puede usar diferencias en diferencias, que sería el
  método preferible.
- **SUTVA.** Instalar 1.000 neveras puede mover a la competencia o canibalizar tiendas vecinas.
- Los datos son simulados con fines académicos: no provienen de FEMSA, Postobón ni de tiendas reales.

## Declaración de uso de IA

El grupo usó Claude como asistente en el análisis, con las skills **/explore-data, /analyze y /validate-data.**

Con **/explore-data** exploró la estructura, las distribuciones y la calidad del conjunto de datos. Con **/analyze** formuló preguntas analíticas, interpretó resultados, identificó patrones y discutió alternativas metodológicas. Con **/validate-data** verificó cálculos y agregaciones, contrastó supuestos, buscó sesgos y revisó la coherencia entre resultados y conclusiones. También usó Claude para escribir y revisar el código del cuaderno y los textos explicativos.

La dirección del proyecto y las decisiones metodológicas son del grupo: la definición del tratamiento, la exclusión de variables por posible fuga de información (data leakage), la selección del estimador causal final y el criterio para elegir las 1.000 tiendas. Cada validación sugerida por la herramienta se revisó antes de aceptarla. Todos los integrantes pueden explicar, justificar y modificar el código, las decisiones metodológicas y los resultados de este cuaderno.
