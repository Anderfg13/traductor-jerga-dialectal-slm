# Análisis de incertidumbre (bootstrap por semilla)

Test común: 174 entradas de 9 semillas; 1000 remuestreos de semillas con reemplazo (`evaluation/bootstrap.py`). Cada fila es la diferencia A − B; el intervalo es el 95 % del remuestreo y "P(A>B)" la fracción de remuestreos en que A supera a B. **Un intervalo que incluye 0 significa que con estos datos no se puede distinguir A de B.**

## Puntaje por modelo (IC 95 %)

| Modelo | BLEU | chrF |
|---|---|---|
| baseline | 37.0 [34.3, 40.1] | 53.9 [51.8, 55.9] |
| fusion_linear | 35.3 [32.5, 37.5] | 51.5 [49.6, 53.8] |
| fusion_ties | 43.7 [40.9, 47.1] | 58.2 [56.4, 60.4] |
| mergekit_linear | 44.2 [41.1, 48.3] | 58.4 [56.3, 61.2] |
| peft_cat_norm | 43.5 [40.5, 47.5] | 58.1 [56.0, 61.1] |
| peft_linear_norm | 43.6 [40.8, 47.4] | 58.1 [56.2, 60.7] |

## Diferencias entre modelos

| A − B | ΔBLEU (IC 95 %) | P(A>B) BLEU | ΔchrF (IC 95 %) | P(A>B) chrF |
|---|---|---|---|---|
| fusion_linear − baseline | -1.9 [-4.2, +0.3] | 5% | -2.4 [-4.4, -0.2] * | 2% |
| fusion_ties − baseline | +6.6 [+4.1, +9.6] * | 100% | +4.3 [+2.3, +6.9] * | 100% |
| mergekit_linear − baseline | +7.2 [+4.8, +10.1] * | 100% | +4.5 [+2.7, +6.8] * | 100% |
| peft_cat_norm − baseline | +6.5 [+4.0, +9.4] * | 100% | +4.3 [+2.3, +6.5] * | 100% |
| peft_linear_norm − baseline | +6.6 [+4.3, +9.3] * | 100% | +4.3 [+2.6, +6.2] * | 100% |
| fusion_linear − fusion_ties | -8.6 [-12.5, -5.6] * | 0% | -6.7 [-9.1, -4.7] * | 0% |
| fusion_linear − mergekit_linear | -9.2 [-13.3, -6.1] * | 0% | -7.0 [-9.7, -4.8] * | 0% |
| fusion_linear − peft_cat_norm | -8.4 [-12.3, -5.5] * | 0% | -6.7 [-9.4, -4.5] * | 0% |
| fusion_linear − peft_linear_norm | -8.5 [-12.4, -5.6] * | 0% | -6.7 [-9.2, -4.7] * | 0% |
| fusion_ties − mergekit_linear | -0.6 [-1.8, +0.5] | 14% | -0.2 [-1.4, +0.7] | 34% |
| fusion_ties − peft_cat_norm | +0.1 [-1.2, +1.6] | 57% | +0.0 [-1.1, +1.1] | 58% |
| fusion_ties − peft_linear_norm | +0.0 [-1.0, +1.4] | 50% | +0.0 [-0.9, +1.1] | 50% |
| mergekit_linear − peft_cat_norm | +0.7 [+0.1, +1.6] * | 99% | +0.3 [-0.2, +0.9] | 81% |
| mergekit_linear − peft_linear_norm | +0.7 [+0.0, +1.4] * | 98% | +0.3 [-0.2, +0.8] | 88% |
| peft_cat_norm − peft_linear_norm | -0.1 [-0.7, +0.6] | 38% | +0.0 [-0.4, +0.5] | 49% |

`*` = el intervalo de 95 % NO incluye 0 (diferencia distinguible con estos datos).
