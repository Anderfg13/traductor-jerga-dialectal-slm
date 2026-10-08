# Análisis de incertidumbre (bootstrap por semilla)

Test común: 174 entradas de 9 semillas; 2000 remuestreos de semillas con reemplazo (`evaluation/bootstrap.py`). Cada fila es la diferencia A − B; el intervalo es el 95 % del remuestreo y "P(A>B)" la fracción de remuestreos en que A supera a B. **Un intervalo que incluye 0 significa que con estos datos no se puede distinguir A de B.**

## Puntaje por modelo (IC 95 %)

| Modelo | BLEU | chrF |
|---|---|---|
| baseline | 37.0 [34.3, 40.1] | 53.9 [51.8, 55.9] |
| generador2 | 40.7 [38.7, 43.3] | 55.3 [53.6, 57.2] |
| generador3 | 42.3 [38.8, 46.6] | 57.9 [55.5, 61.4] |
| mezcla | 42.4 [39.9, 45.4] | 57.2 [55.2, 59.7] |

## Diferencias entre modelos

| A − B | ΔBLEU (IC 95 %) | P(A>B) BLEU | ΔchrF (IC 95 %) | P(A>B) chrF |
|---|---|---|---|---|
| generador2 − baseline | +3.7 [+0.4, +7.2] * | 99% | +1.4 [-1.3, +4.2] | 85% |
| generador3 − baseline | +5.1 [+2.5, +8.1] * | 100% | +4.1 [+2.1, +6.7] * | 100% |
| mezcla − baseline | +5.3 [+3.6, +7.6] * | 100% | +3.4 [+1.6, +5.6] * | 100% |
| generador2 − generador3 | -1.4 [-4.5, +1.6] | 17% | -2.7 [-5.1, -0.8] * | 0% |
| generador2 − mezcla | -1.6 [-3.6, +0.1] | 4% | -1.9 [-4.4, -0.3] * | 1% |
| generador3 − mezcla | -0.2 [-2.6, +2.2] | 43% | +0.8 [-1.1, +2.9] | 77% |

`*` = el intervalo de 95 % NO incluye 0 (diferencia distinguible con estos datos).
