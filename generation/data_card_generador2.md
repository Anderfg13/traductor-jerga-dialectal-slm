# Data card — dataset del Generador 2 (Cohere)

## Qué es

Dataset español-inglés de jerga y dialectos generado sintéticamente a partir de las 100 semillas del banco (`seeds/lote_01.json` + `seeds/lote_02.json`) con **Generador 2 = Cohere `command-r-08-2024`**, usando exactamente la misma plantilla de derivación (`generation/prompt_derivacion.md`) y el mismo script (`generation/generar_sintetico.py --generador 2`, luego `generation/consolidar.py`) que los otros dos generadores. Los tres datasets son comparables entre sí: lo único que cambia es el LLM.

## Tamaño y cobertura

| Etapa | Variantes | Semillas |
|---|---|---|
| Generadas (`dataset_generador2.json`) | 632 | 100 |
| Tras el filtro automático (`dataset_generador2_limpio.json`) | 632 | 100 |

| Dialecto | Variantes (limpio) |
|---|---|
| Rioplatense | 139 |
| Caribeña | 134 |
| Mexicana | 133 |
| Andina | 128 |
| Chilena | 98 |

Registro de las variantes: **informal 383 (61 %), formal 127 (20 %), jerga 122 (19 %)**. En comparación, el Generador 1 produjo 12 % formal y 30 % jerga, y el Generador 3, 7 % formal y 33 % jerga (`generation/comparacion_generadores.md`): Cohere escribió más registro formal y menos jerga con el mismo prompt. Es una hipótesis sobre por qué su adaptador rinde algo menos en chrF; no se probó.

## Cómo se generó

1. Semilla (`seeds/schema.md`) → plantilla de derivación (5-8 variantes por semilla variando contexto, registro y tono, conservando el significado y el dialecto).
2. Llamada a Cohere con reintentos y backoff; la salida cruda se guarda por semilla en `generation/raw/generador2/` antes de procesarla.
3. Consolidación (`consolidar.py`): parseo, descarte de vacías y duplicados exactos.
4. Filtro automático (`validar.py`, 4 reglas: longitud, casi-copia de la semilla, idioma sospechoso, duplicado exacto).

Acceso: clave "trial" gratuita de Cohere (cupo limitado de llamadas por mes), **costo 0**. Latencia medida con 3 llamadas de prueba (`generation/latencias_generadores.json`): mediana de ~27.6 s por semilla, con una de 72 s; mucho más lenta que Groq (~0.9 s) y Google (~2.9 s). El tiempo de las corridas reales no se registró (se pausaron y reanudaron; una se colgó).

## Filtro automático

632 de 632 aprobadas, 0 descartadas, 0 sospechosas (`generation/reporte_filtrado_dataset_generador2.md`). Que no descarte nada indica que el filtro detecta defectos de formato, no la calidad dialectal: no detecta mezcla de dialectos ni errores de sentido.

## Splits (por semilla, `seeds/split_semillas.json`)

El mismo reparto fijo que los demás generadores (81/10/9 semillas), sin ninguna semilla en más de un split.

| Split | Semillas | Variantes |
|---|---|---|
| train | 81 | 513 |
| val | 10 | 64 |
| test | 9 | 55 |

El test común de evaluación (`evaluation/test_comun.json`) usa las 9 semillas de test de los tres generadores más las referencias humanas del banco.

## Uso previsto y resultados

Se entrenó un adaptador LoRA con este dataset (`finetuning/curva_final_generador2.md`): ~19 min en T4, mejor época la 1. Sobre el test común quedó en 40.7 BLEU / 55.3 chrF, por debajo de los otros dos generadores en chrF (`evaluation/comparacion_pi1_automatica.md`).

## Limitaciones conocidas

- Referencias y variantes escritas por un LLM, no por hablantes nativos; pueden contener errores de sentido y estereotipos regionales que nadie verificó.
- Mayor proporción de registro formal que los otros generadores.
- El filtro no atrapa mezcla de dialectos (caso conocido: `sem-016` en el Generador 1) ni errores de significado.
- Solo 9 semillas de test: las conclusiones sobre el efecto del generador son tentativas.
- Revisar los términos de uso de Cohere antes de redistribuir el dataset (pendiente de revisión legal del equipo).
