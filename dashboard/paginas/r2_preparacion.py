import pandas as pd
import streamlit as st

import datos
import marca

marca.encabezado(
    "Recorrido · 2 de 6",
    "Cada modelo ve solo lo que podría saber al decidir",
    "Si una columna ya contiene la respuesta, el modelo luce perfecto y no sirve para una tienda "
    "nueva. Por eso hay tres conjuntos de variables, uno por pregunta.",
)
marca.fila_kpis([
    ("Columnas en la base", marca.num(datos.COLUMNAS_BASE), "38.000 tiendas, un mes", False),
    ("Fuga directa", "50", "columnas que suman o derivan la respuesta", True),
    ("Resultados simultáneos", "4", "ventas del mismo mes afectadas por la nevera", False),
    ("Variables de la nevera", "6", "describen el tratamiento: fuera del modelo causal", False),
])

st.subheader("Tres conjuntos, tres preguntas")
st.dataframe(pd.DataFrame(datos.CONJUNTOS, columns=["Conjunto", "Pregunta que responde", "Qué excluye"]),
             hide_index=True, width="stretch")

col1, col2, col3 = st.columns(3)
with col1:
    marca.lectura("<b>Fuga directa.</b> La suma de los diez SKU FEMSA es exactamente la venta. "
                  "Se verificó como identidad numérica sobre las 38.000 filas, no como sospecha.")
with col2:
    marca.lectura("<b>Resultados simultáneos.</b> Las ventas de Postobón del mismo mes reaccionan "
                  "a la nevera FEMSA. Condicionar sobre ellas sesgaría el efecto.")
with col3:
    marca.lectura("<b>La nevera misma.</b> Número, puertas o antigüedad son el tratamiento. "
                  "Pueden describir ventas de hoy, no explicar el efecto de una nevera nueva.")

marca.lectura("El conjunto de riesgo sí ve la foto de hoy, incluidas las ventas: el cambio de proveedor "
              "ocurre en los seis meses siguientes, así que esa información estaría disponible al "
              "decidir una campaña. Partición 80/20 con semilla 42 y validación cruzada de cinco folds.")

marca.siguiente("paginas/r3_ventas.py", "Siguiente: modelo de ventas")
marca.pie()
