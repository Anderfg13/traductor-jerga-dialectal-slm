# Análisis de incertidumbre (bootstrap por semilla)

Test común: 174 entradas de 9 semillas; 1000 remuestreos de semillas con reemplazo (`evaluation/bootstrap.py`). Cada fila es la diferencia A − B; el intervalo es el 95 % del remuestreo y "P(A>B)" la fracción de remuestreos en que A supera a B. **Un intervalo que incluye 0 significa que con estos datos no se puede distinguir A de B.**

## Puntaje por modelo (IC 95 %)

| Modelo | BLEU | chrF |
|---|---|---|
| baseline | 37.0 [34.3, 40.1] | 53.9 [51.8, 55.9] |
| destilacion | 43.9 [40.8, 47.5] | 58.3 [56.5, 60.5] |
| fusion_dare_ties | 43.8 [40.5, 47.5] | 57.7 [55.6, 60.2] |
| fusion_linear | 35.3 [32.5, 37.5] | 51.5 [49.6, 53.8] |
| fusion_ties | 43.7 [40.9, 47.1] | 58.2 [56.4, 60.4] |
| generador1 | 42.2 [38.7, 46.3] | 57.5 [55.5, 59.7] |
| generador2 | 40.7 [38.7, 43.3] | 55.3 [53.6, 57.1] |
| generador3 | 42.3 [39.0, 46.7] | 57.9 [55.7, 61.3] |
| mezcla | 42.4 [39.9, 45.5] | 57.2 [55.2, 59.8] |

## Diferencias entre modelos

| A − B | ΔBLEU (IC 95 %) | P(A>B) BLEU | ΔchrF (IC 95 %) | P(A>B) chrF |
|---|---|---|---|---|
| destilacion − baseline | +6.6 [+3.3, +10.4] * | 100% | +4.4 [+2.1, +7.2] * | 100% |
| fusion_dare_ties − baseline | +6.6 [+4.0, +9.5] * | 100% | +3.8 [+1.6, +6.5] * | 100% |
| fusion_linear − baseline | -1.9 [-4.2, +0.3] | 5% | -2.4 [-4.4, -0.2] * | 2% |
| fusion_ties − baseline | +6.6 [+4.1, +9.6] * | 100% | +4.3 [+2.3, +6.9] * | 100% |
| generador1 − baseline | +5.2 [+2.1, +8.6] * | 100% | +3.6 [+1.9, +5.6] * | 100% |
| generador2 − baseline | +3.7 [+0.3, +7.3] * | 99% | +1.4 [-1.3, +4.2] | 85% |
| generador3 − baseline | +5.1 [+2.4, +8.0] * | 100% | +4.1 [+2.1, +6.5] * | 100% |
| mezcla − baseline | +5.3 [+3.5, +7.6] * | 100% | +3.4 [+1.5, +5.6] * | 100% |
| destilacion − fusion_dare_ties | +0.0 [-1.7, +1.6] | 53% | +0.6 [-0.1, +1.3] | 95% |
| destilacion − fusion_linear | +8.6 [+5.3, +13.0] * | 100% | +6.9 [+4.6, +9.6] * | 100% |
| destilacion − fusion_ties | -0.0 [-1.3, +1.3] | 52% | +0.1 [-0.5, +0.9] | 61% |
| destilacion − generador1 | +1.4 [-0.7, +3.6] | 92% | +0.8 [-0.3, +2.2] | 91% |
| destilacion − generador2 | +2.9 [+1.2, +4.9] * | 100% | +3.0 [+1.5, +4.7] * | 100% |
| destilacion − generador3 | +1.5 [-0.9, +4.5] | 88% | +0.3 [-1.5, +2.1] | 62% |
| destilacion − mezcla | +1.3 [-0.5, +3.0] | 91% | +1.0 [-0.5, +2.4] | 92% |
| fusion_dare_ties − fusion_linear | +8.6 [+5.6, +12.5] * | 100% | +6.3 [+4.1, +8.7] * | 100% |
| fusion_dare_ties − fusion_ties | -0.0 [-1.3, +1.1] | 51% | -0.5 [-1.0, +0.1] | 4% |
| fusion_dare_ties − generador1 | +1.4 [-0.5, +3.4] | 92% | +0.2 [-0.7, +1.4] | 58% |
| fusion_dare_ties − generador2 | +2.9 [+1.1, +5.2] * | 100% | +2.4 [+0.8, +4.4] * | 100% |
| fusion_dare_ties − generador3 | +1.5 [-0.7, +4.1] | 90% | -0.3 [-2.0, +1.2] | 38% |
| fusion_dare_ties − mezcla | +1.3 [+0.1, +2.5] * | 98% | +0.4 [-0.7, +1.4] | 80% |
| fusion_linear − fusion_ties | -8.6 [-12.5, -5.6] * | 0% | -6.7 [-9.1, -4.7] * | 0% |
| fusion_linear − generador1 | -7.1 [-11.4, -3.7] * | 0% | -6.1 [-8.2, -4.2] * | 0% |
| fusion_linear − generador2 | -5.7 [-8.9, -3.0] * | 0% | -3.8 [-6.0, -1.8] * | 0% |
| fusion_linear − generador3 | -7.0 [-11.0, -4.4] * | 0% | -6.6 [-9.6, -4.1] * | 0% |
| fusion_linear − mezcla | -7.3 [-10.8, -4.5] * | 0% | -5.8 [-7.8, -3.7] * | 0% |
| fusion_ties − generador1 | +1.4 [-0.7, +4.1] | 89% | +0.7 [-0.3, +2.1] | 86% |
| fusion_ties − generador2 | +2.9 [+1.4, +4.5] * | 100% | +2.9 [+1.6, +4.6] * | 100% |
| fusion_ties − generador3 | +1.5 [-0.8, +4.1] | 91% | +0.2 [-1.6, +1.7] | 60% |
| fusion_ties − mezcla | +1.3 [+0.3, +2.4] * | 100% | +0.9 [-0.2, +1.9] | 94% |
| generador1 − generador2 | +1.5 [-1.4, +4.1] | 86% | +2.3 [+0.2, +4.2] * | 98% |
| generador1 − generador3 | +0.1 [-2.8, +3.4] | 52% | -0.5 [-2.4, +1.1] | 34% |
| generador1 − mezcla | -0.1 [-2.2, +1.9] | 46% | +0.3 [-0.9, +1.4] | 69% |
| generador2 − generador3 | -1.4 [-4.6, +1.7] | 17% | -2.7 [-5.3, -0.8] * | 0% |
| generador2 − mezcla | -1.6 [-3.6, +0.1] | 4% | -2.0 [-4.4, -0.3] * | 0% |
| generador3 − mezcla | -0.2 [-2.6, +2.1] | 43% | +0.7 [-1.1, +2.7] | 76% |

`*` = el intervalo de 95 % NO incluye 0 (diferencia distinguible con estos datos).
