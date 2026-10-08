# Comparación del modelo fusionado con los individuales (PI2, respuesta preliminar)

Generado por `evaluation/comparacion_fusion.py`. Fusión = promedio simple y TIES de los adaptadores de los generadores 1, 2 y 3, hechos con `mergekit` sobre modelos completos (`merging/fusion_simple.md`). Mismo test común para todos los modelos (**174 entradas de 9 semillas**, verificado: mismas entradas, referencias y semillas), mismas métricas (sacrebleu).

**Mejor individual** (criterio fijado de antemano: mayor chrF global): **LoRA Generador 3** (42.3 / 57.9). El Generador 1 queda a menos de un punto y no se distingue de él; el Generador 2 queda por debajo (1.5 BLEU y 2.6 chrF menos, y en chrF esa diferencia sí se distingue del ruido).

## 1. Tabla comparativa (BLEU / chrF globales)

| Modelo | BLEU | chrF | Δ BLEU vs mejor individual | Δ chrF vs mejor individual |
|---|---|---|---|---|
| Base sin ajustar | 37.0 | 53.9 | -5.3 | -4.0 |
| LoRA Generador 1 | 42.2 | 57.5 | -0.0 | -0.4 |
| LoRA Generador 2 | 40.7 | 55.3 | -1.5 | -2.6 |
| LoRA Generador 3 | 42.3 | 57.9 | +0.0 | +0.0 |
| **Mejor individual (LoRA Generador 3)** | 42.3 | 57.9 | +0.0 | +0.0 |
| LoRA entrenado sobre la mezcla 1+2+3 | 42.4 | 57.2 | +0.2 | -0.7 |
| Fusión: promedio simple (mergekit) | 44.2 | 58.4 | +2.0 | +0.4 |
| Fusión: TIES (mergekit) | 44.0 | 58.0 | +1.8 | +0.1 |

## 2. Diferencia fusión − individual, con incertidumbre

Intervalo de 95 % por bootstrap sobre semillas (`evaluation/analisis_bootstrap.md`); `*` = el intervalo no incluye 0.

| Fusión − individual | ΔBLEU [IC 95 %] | ΔchrF [IC 95 %] |
|---|---|---|
| promedio simple (mergekit) − Generador 1 | +2.0 [+0.2, +4.2] * | +0.9 [-0.2, +2.2] |
| promedio simple (mergekit) − Generador 2 | +3.5 [+1.6, +6.1] * | +3.1 [+1.3, +5.6] * |
| promedio simple (mergekit) − Generador 3 **(mejor)** | +2.2 [+0.5, +4.2] * | +0.4 [-0.6, +1.5] |
| promedio simple (mergekit) − entrenado sobre la mezcla 1+2+3 | +1.9 [+0.9, +3.2] * | +1.1 [+0.1, +2.4] * |
| TIES (mergekit) − Generador 1 | +1.8 [+0.2, +3.5] * | +0.5 [-0.4, +1.5] |
| TIES (mergekit) − Generador 2 | +3.3 [+1.5, +5.4] * | +2.7 [+1.0, +4.8] * |
| TIES (mergekit) − Generador 3 **(mejor)** | +1.9 [-0.4, +4.6] | +0.0 [-2.2, +1.8] |
| TIES (mergekit) − entrenado sobre la mezcla 1+2+3 | +1.7 [+0.8, +2.6] * | +0.8 [-0.1, +1.6] |

## 3. Por dialecto (BLEU / chrF; n = entradas)

| Modelo | Andina | Caribeña | Chilena | Mexicana | Rioplatense |
|---|---|---|---|---|---|
| Mejor individual (LoRA Generador 3) | 38.7 / 56.5 (38) | 42.0 / 56.8 (39) | 39.5 / 53.4 (19) | 49.8 / 63.5 (40) | 37.5 / 57.4 (38) |
| Fusión: promedio simple (mergekit) | 39.6 / 55.6 (38) | 42.9 / 57.4 (39) | 44.8 / 55.7 (19) | 52.4 / 64.1 (40) | 42.6 / 58.2 (38) |
| Fusión: TIES (mergekit) | 38.0 / 54.7 (38) | 42.9 / 57.1 (39) | 47.6 / 57.9 (19) | 50.7 / 61.6 (40) | 43.5 / 59.5 (38) |

Con 1 o 2 semillas por dialecto, las diferencias entre dialectos son anecdóticas y no se interpretan.

## 4. Solo referencias humanas del banco de semillas (`oro`, n = 9)

| Modelo | BLEU | chrF |
|---|---|---|
| Base sin ajustar | 1.4 | 8.6 |
| Mejor individual (LoRA Generador 3) | 3.8 | 13.9 |
| Fusión: promedio simple (mergekit) | 4.9 | 14.1 |
| Fusión: TIES (mergekit) | 4.3 | 11.7 |

Nueve entradas no permiten concluir nada; se muestra por completitud.

## 5. Réplicas con otras implementaciones (consistencia)

| Modelo | BLEU | chrF |
|---|---|---|
| Promedio simple con PEFT (pesos 1/3) | 43.6 | 58.1 |
| Promedio exacto con PEFT (cat, pesos 1/3) | 43.5 | 58.1 |
| TIES con PEFT | 43.7 | 58.2 |
| DARE+TIES con PEFT | 43.8 | 57.7 |
| Destilación multi-maestro | 43.9 | 58.3 |

Todas las fusiones que promedian (en vez de sumar) quedan en el mismo rango: el resultado no depende de la herramienta.

## 6. Respuesta preliminar a PI2 (y cómo no pasarse)

- **La fusión no fue peor que el mejor individual**: promedio simple 44.2 / 58.4 y TIES 44.0 / 58.0, frente a 42.3 / 57.9 del mejor individual.
- **Pero la ventaja es pequeña y frágil.** Frente al mejor individual: promedio simple +2.2 [+0.5, +4.2] * BLEU y +0.4 [-0.6, +1.5] chrF; TIES +1.9 [-0.4, +4.6] BLEU y +0.0 [-2.2, +1.8] chrF. Donde el intervalo incluye 0, con estos datos no se distingue de un empate.
- **Sí supera con claridad al peor individual (Generador 2) y, en BLEU, al modelo entrenado sobre la mezcla.**
- **Entre promedio simple y TIES no hay diferencia distinguible**: la técnica de fusión importa menos que fusionar bien.
- **Lectura honesta**: una primera señal sugiere que fusionar los adaptadores es al menos tan bueno como el mejor modelo individual y quizás algo mejor en BLEU; no se puede afirmar que lo supere. Si el resultado hubiera sido peor, también se habría reportado.
- **Cautelas**: solo 9 semillas de prueba, una corrida por modelo, referencias mayormente sintéticas (con sesgo hacia el LLM que las escribió), decenas de comparaciones (un intervalo que apenas excluye 0 puede ser casualidad), el "mejor individual" se elige con el mismo test (lo favorece ligeramente), y sin evaluación humana (BLEU/chrF no miden retención de matices).
