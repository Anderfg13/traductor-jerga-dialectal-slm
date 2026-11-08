# Comparación de los tres generadores sintéticos (primer insumo para PI1)

Mismas 100 semillas (`seeds/lote_01` + `lote_02`), misma plantilla de prompt, mismo filtro (`generation/validar.py`). Generado por `generation/comparar_generadores.py`; leer primero la nota sobre tiempo y costo al final.

## Resumen: una fila por generador

| Generador | Ejemplos generados | Tras el filtro | Filtrado | Tiempo por llamada | Tiempo estimado, 100 semillas | Costo |
|---|---|---|---|---|---|---|
| G1 Groq `openai/gpt-oss-20b` | 589 | 587 | 2 (0.3 %) | 0.9 s (rango 0.9-1.3) | ~1 min | $0 (capa gratuita); 100 semillas (sin contar regeneraciones), ~48k tokens de entrada y ~50k de salida |
| G2 Cohere `command-r-08-2024` | 632 | 632 | 0 (0.0 %) | 27.6 s (rango 16.2-72.3) | ~46 min | $0 (capa gratuita); 100 semillas (sin contar regeneraciones), ~48k tokens de entrada y ~61k de salida |
| G3 Google `gemini-3.5-flash-lite` | 625 | 625 | 0 (0.0 %) | 2.9 s (rango 2.8-3.0) | ~5 min | $0 (capa gratuita); 100 semillas (sin contar regeneraciones), ~48k tokens de entrada y ~61k de salida |

## Estadísticas de los datos

| | G1 | G2 | G3 |
|---|---|---|---|
| Variantes por semilla (prom., mín-máx) | 5.9 (5-7) | 6.3 (6-7) | 6.2 (6-7) |
| Palabras por texto dialectal (prom.) | 14.0 | 12.9 | 15.0 |
| Palabras por traducción (prom.) | 13.2 | 13.3 | 15.5 |
| Registro `formal` | 12 % | 20 % | 7 % |
| Registro `informal` | 58 % | 61 % | 59 % |
| Registro `jerga` | 30 % | 19 % | 33 % |
| Textos repetidos entre semillas | 0 | 0 | 0 |
| 'che' en variantes no rioplatenses (mezcla de dialecto) | 6 | 0 | 0 |

## Cómo leerla para PI1

- **El filtro casi no distingue generadores** (0.3 % vs 0 %): solo mira vacíos, duplicados, longitud, parecido a la semilla e idioma. La diferencia de calidad entre generadores tendrá que salir de los modelos entrenados con cada uno, no de esta tabla.
- **Mezcla de dialecto**: G1 tiene variantes con "che" en dialectos que no son rioplatenses; G2 y G3 no. Es un indicio con una heurística de un solo marcador y pocos casos, no una conclusión.
- **Registro**: G2 produce más registro formal y menos jerga que G1 y G3, con el mismo prompt.
- G3 es un modelo "lite", más pequeño que los otros dos: una diferencia entre generadores no se puede atribuir solo a "qué LLM es".
- Los tres tienen tamaño comparable (589 / 632 / 625), así que el tamaño del dataset no es una variable de confusión grande.

## Nota sobre tiempo y costo

El tiempo de las corridas reales no se guardó (se pausaron, se reanudaron y la de Cohere se colgó una vez), así que el tiempo por llamada se midió aparte con 3 llamadas reales por generador (`sem-006`, `sem-007`, `sem-018`) y el total es esa mediana x 100: una estimación de generación secuencial **sin contar reintentos por límite de tasa**, que en la práctica alargaron mucho la corrida (Google lite permite 15 por minuto; Cohere trial fue lento). Con solo 3 mediciones es una referencia gruesa. El costo en dinero fue 0 porque los tres usan capa gratuita; los tokens son aproximados (caracteres / 4). No se calculó un costo "si fuera de pago" porque no se verificaron tarifas vigentes.
