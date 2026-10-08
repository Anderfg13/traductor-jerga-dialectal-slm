# Incertidumbre de la comparación PI3 (bootstrap por semilla)

1000 remuestreos de semillas con reemplazo. Diferencia = modelo pequeño − sistema general; intervalo de 95 %. `*` = el intervalo no incluye 0. Cada sistema se compara sobre las mismas entradas, excluyendo las referencias que él mismo escribió (los generadores).

| Modelo pequeño | Sistema general | n | ΔBLEU (IC 95 %) | ΔchrF (IC 95 %) |
|---|---|---|---|---|
| mergekit_linear | gpt-oss-20b | 120 | +3.5 [+0.2, +7.0] * | +0.8 [-1.6, +3.3] |
| generador3 | gpt-oss-20b | 120 | +2.8 [-1.0, +7.0] | +1.0 [-1.7, +4.0] |
| mergekit_linear | command-r | 119 | -1.2 [-4.2, +2.3] | -2.9 [-5.4, +0.1] |
| generador3 | command-r | 119 | -3.1 [-7.1, +1.1] | -3.1 [-6.1, +0.7] |
| mergekit_linear | gemini-3.5-flash-lite | 117 | +0.6 [-2.8, +4.0] | -2.0 [-4.7, +0.4] |
| generador3 | gemini-3.5-flash-lite | 117 | -3.3 [-7.5, +0.3] | -3.2 [-6.1, -1.0] * |
| mergekit_linear | gpt-oss-120b | 174 | -3.9 [-7.2, -1.5] * | -4.5 [-7.2, -2.6] * |
| generador3 | gpt-oss-120b | 174 | -6.1 [-10.5, -2.7] * | -4.9 [-8.4, -2.5] * |
| mergekit_linear | qwen3.8-27b | 173 | -3.4 [-6.8, -0.4] * | -4.0 [-6.3, -2.1] * |
| generador3 | qwen3.8-27b | 173 | -5.6 [-10.1, -1.7] * | -4.5 [-7.4, -2.1] * |
