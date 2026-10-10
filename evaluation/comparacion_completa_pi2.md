# Comparación completa para PI2: fusión simple, destilación, mezcla e individuales

Generado por `evaluation/comparacion_completa_pi2.py`. Mismas 174 entradas de 9 semillas para todos los modelos (verificado), mismas métricas (sacrebleu). Intervalo de 95 % entre corchetes (bootstrap por semilla).

## 1. Todas las variantes

| Modelo | BLEU [IC 95 %] | chrF [IC 95 %] |
|---|---|---|
| **Referencias** | | |
| Base sin ajustar | 37.0 [34.3, 40.1] | 53.9 [51.8, 55.9] |
| **Modelos individuales** | | |
| LoRA Generador 1 (Groq) | 42.2 [38.7, 46.3] | 57.5 [55.5, 59.7] |
| LoRA Generador 2 (Cohere) | 40.7 [38.7, 43.3] | 55.3 [53.6, 57.1] |
| LoRA Generador 3 (Google lite) | 42.3 [39.0, 46.7] | 57.9 [55.7, 61.3] |
| **Entrenamiento sobre la mezcla de los tres datasets** | | |
| LoRA sobre la mezcla 1+2+3 | 42.4 [39.9, 45.5] | 57.2 [55.2, 59.8] |
| **Fusión simple (promedio)** | | |
| Promedio simple, mergekit (modelos completos) | 44.2 [41.1, 48.3] | 58.4 [56.3, 61.2] |
| Promedio simple, PEFT (pesos 1/3) | 43.6 [40.8, 47.4] | 58.1 [56.2, 60.7] |
| Promedio exacto, PEFT cat (pesos 1/3) | 43.5 [40.5, 47.5] | 58.1 [56.0, 61.1] |
| Promedio PEFT con pesos 1.0 (suma; error de configuración) | 35.3 [32.5, 37.5] | 51.5 [49.6, 53.8] |
| **Fusión TIES / DARE** | | |
| TIES, mergekit (modelos completos) | 44.0 [41.1, 47.6] | 58.0 [56.2, 60.2] |
| TIES, PEFT | 43.7 [40.9, 47.1] | 58.2 [56.4, 60.4] |
| DARE+TIES, PEFT | 43.8 [40.5, 47.5] | 57.7 [55.6, 60.2] |
| **Fusión guiada por destilación** | | |
| Destilación multi-maestro (parte de TIES PEFT) | 43.9 [40.8, 47.5] | 58.3 [56.5, 60.5] |

## 2. Las cinco opciones que compara PI2

| Opción | BLEU | chrF |
|---|---|---|
| Base sin ajustar | 37.0 | 53.9 |
| Mejor individual (criterio fijo: mayor chrF): LoRA Generador 3 (Google lite) | 42.3 | 57.9 |
| Entrenar sobre la mezcla | 42.4 | 57.2 |
| Fusión simple (mergekit) | 44.2 | 58.4 |
| Fusión por destilación | 43.9 | 58.3 |

Ranking por chrF: fusión simple > destilación > mejor individual > mezcla > base. Por BLEU, el primero es **Fusión simple (mergekit)** (44.2).

## 3. ¿Es grande o marginal la diferencia entre fusión simple y destilación?

- Destilación − fusión simple (mergekit): BLEU -0.6 [-2.5, +1.0], chrF -0.1 [-1.3, +1.0]. **Marginal**: el intervalo incluye 0 en ambas métricas, no se distingue de un empate. La destilación costó 95 min de GPU frente a 13 s (promedio simple con PEFT) o ~20 min (con mergekit, contando la incorporación de adaptadores) de la fusión simple (`merging/fusion_destilacion.md`).

## 4. Diferencias clave (con intervalo)

| A − B | ΔBLEU | ΔchrF |
|---|---|---|
| mergekit_linear − generador3 | +2.2 [+0.5, +4.2] * | +0.4 [-0.6, +1.5] |
| mergekit_linear − mezcla | +1.9 [+0.9, +3.2] * | +1.1 [+0.1, +2.4] * |
| destilacion − generador3 | +1.5 [-0.9, +4.5] | +0.3 [-1.5, +2.1] |
| destilacion − mezcla | +1.3 [-0.5, +3.0] | +1.0 [-0.5, +2.4] |
| mergekit_ties − mergekit_linear | -0.3 [-1.3, +0.7] | -0.4 [-1.8, +0.7] |
| destilacion − mergekit_ties | -0.4 [-1.9, +1.0] | +0.3 [-0.7, +1.2] |

`*` = el intervalo no incluye 0.

## 5. Respuesta completa (pero cautelosa) a PI2

- **¿La fusión iguala o supera al mejor individual?** Lo iguala siempre y, en BLEU, parece superarlo por ~2 puntos con la fusión simple de mergekit (intervalo que apenas excluye 0); en chrF no se distingue. No se puede afirmar que lo supere.
- **¿Y al entrenamiento sobre la mezcla de todos los datos?** Las fusiones lo superan en BLEU (~+1.3 a +1.9, intervalos que excluyen 0 salvo la destilación); en chrF solo la fusión simple lo supera con claridad. Es decir, fusionar adaptadores ya entrenados dio un resultado al menos tan bueno como volver a entrenar con todos los datos, a una fracción del costo (de 13 s a unos 20 min según la herramienta, frente a ~52 min de reentrenar con la mezcla).
- **¿Importa la técnica de fusión?** Con estos datos no: simple, TIES, DARE+TIES y destilación quedan en 43.7-44.2 BLEU, sin diferencias distinguibles entre ellas. Importa fusionar bien: sumar en vez de promediar dio 35.3.
- **Cautelas**: 9 semillas de prueba, una corrida por modelo, referencias mayormente sintéticas, decenas de comparaciones, sin evaluación humana.
