# Data card — dataset del Generador 3 (Google)

## Qué es

Dataset español-inglés de jerga y dialectos generado sintéticamente a partir de las 100 semillas del banco (`seeds/lote_01.json` + `seeds/lote_02.json`) con **Generador 3 = Google `gemini-3.5-flash-lite`**, con la misma plantilla de derivación (`generation/prompt_derivacion.md`) y el mismo script (`generation/generar_sintetico.py --generador 3`, luego `consolidar.py`) que los otros dos generadores.

**Es un modelo "lite"**, elegido por su cupo gratuito (15 solicitudes por minuto) y no por su calidad; el `gemini-3.6-flash` permitía solo 20 solicitudes por día en el nivel gratuito. Por eso "qué LLM es" no se separa de "qué tamaño tiene" al comparar generadores.

## Tamaño y cobertura

| Etapa | Variantes | Semillas |
|---|---|---|
| Generadas (`dataset_generador3.json`) | 625 | 100 |
| Tras el filtro automático (`dataset_generador3_limpio.json`) | 625 | 100 |

| Dialecto | Variantes (limpio) |
|---|---|
| Rioplatense | 136 |
| Andina | 133 |
| Caribeña | 131 |
| Mexicana | 131 |
| Chilena | 94 |

Registro: **informal 371 (59 %), jerga 208 (33 %), formal 46 (7 %)**. Es el generador con más jerga y menos registro formal (Generador 1: 30 % jerga, 12 % formal; Generador 2: 19 % jerga, 20 % formal).

## Cómo se generó

1. Semilla → plantilla de derivación (5-8 variantes por semilla).
2. Llamada a Google con reintentos y backoff; salida cruda por semilla en `generation/raw/generador3/`.
3. Consolidación y filtro automático iguales a los de los otros generadores.

Ajustes propios del Generador 3 (sin bifurcar el script): se desactiva el razonamiento (`thinking_level="minimal"`) y se sube `max_tokens` a 3000, porque de lo contrario gastaba el límite pensando. Sus respuestas tienen dos irregularidades de formato que `consolidar.py` corrige: a veces omite la comilla de apertura de un valor y a veces escribe `{"informal": "informal"}` en vez de `{"registro": "informal"}`.

Acceso: capa gratuita de AI Studio, **costo 0**. Latencia con 3 llamadas de prueba (`generation/latencias_generadores.json`): mediana ~2.9 s por semilla.

## Filtro automático

625 de 625 aprobadas, 0 descartadas, 0 sospechosas (`generation/reporte_filtrado_dataset_generador3.md`). Igual que con los otros generadores, el filtro detecta defectos de formato, no la calidad dialectal.

## Splits (por semilla, `seeds/split_semillas.json`)

| Split | Semillas | Variantes |
|---|---|---|
| train | 81 | 508 |
| val | 10 | 61 |
| test | 9 | 56 |

Mismo reparto fijo que los demás generadores; el test común de evaluación combina estas 9 semillas con las de los otros dos y las referencias humanas del banco (`evaluation/test_comun.json`).

## Uso previsto y resultados

Adaptador LoRA entrenado con este dataset (`finetuning/curva_final_generador3.md`): ~18 min en T4, mejor época la 1. En el test común: 42.3 BLEU / 57.9 chrF, el mejor de los tres individuales (no distinguible del Generador 1; `evaluation/comparacion_pi1_automatica.md`).

## Limitaciones conocidas

- Variantes y referencias escritas por un LLM pequeño, sin verificación de hablantes nativos; pueden contener errores de sentido y estereotipos.
- Los errores reales de significado que observamos en los modelos (polisemia regional, expresiones sustituidas por una inglesa parecida) no los detecta el filtro (`evaluation/analisis_cualitativo.md`).
- Cada generador sale favorecido en las referencias que escribió su propio LLM; al comparar, se debe excluir esa fuente (`evaluation/comparacion_fase3.md`).
- Solo 9 semillas de test.
- Revisar los términos de uso de Google antes de redistribuir el dataset (pendiente de revisión legal del equipo).
