# Prueba exploratoria: Jev (TypeSafe AI) como juez automático

Generado a partir de `evaluation/juez_jev.py` (modelo `jev-latest`). Jev no genera texto: para cada par (original dialectal, traducción) devuelve un puntaje 1-5 de "conserva el sentido y matiz". **Es una señal automática, no evaluación humana.** El juez ve solo el original y la traducción, no la referencia.

## Validación (9 entradas con referencia humana)

| Traducción | Puntaje medio |
|---|---|
| Control malo ("The weather is nice today.") | 1.35 |
| Qwen base | 2.40 |
| Mezcla | 2.68 |
| Fusión simple | 2.88 |
| DeepL | 3.14 |
| Referencia humana | 3.43 |

El orden es el esperado, pero n = 9 y la escala está comprimida (ni la referencia humana llega a 4).

## Test común completo (174 entradas, puntaje medio 1-5)

| Sistema | Puntaje |
|---|---|
| Qwen base | 3.00 |
| Mezcla | 3.22 |
| Fusión simple (mergekit) | 3.37 |
| Referencia del test | 3.71 |
| DeepL | 3.78 |

Diferencias (bootstrap por semilla, 2000 remuestreos, IC 95 %):

| Comparación | Δ puntaje |
|---|---|
| Fusión simple − base | +0.37 [+0.20, +0.54] |
| Fusión simple − mezcla | +0.15 [+0.08, +0.22] |
| Fusión simple − DeepL | −0.41 [−0.56, −0.26] |
| Fusión simple − referencia | −0.34 [−0.47, −0.19] |
| DeepL − referencia | +0.07 [−0.03, +0.16] |

## Lectura y cautelas

- Coincide con BLEU/chrF en que el ajuste mejora al base y en que la fusión simple queda por encima de la mezcla.
- **Difiere en DeepL**: BLEU lo da empatado con nuestro modelo; este juez lo ubica claramente por encima. Posible razón: el juez premia fluidez natural en inglés, y DeepL puntúa igual que la referencia del test. No sabemos si mide fidelidad dialectal o fluidez.
- No está validado contra hablantes nativos; con n = 9 la validación es de cordura. Es otro modelo de IA, con sus propios sesgos, y no sustituye la evaluación humana.
- No se usa en el paper como resultado principal; si se cita, solo como señal exploratoria.
