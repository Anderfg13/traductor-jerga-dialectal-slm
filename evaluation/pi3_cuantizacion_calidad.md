# PI3: efecto de la cuantización sobre la calidad (bitsandbytes, GPU)

Generado por `evaluation/pi3_cuantizacion_gpu.py --informe`. Modelo: base + adaptador del promedio exacto (`peft_cat_norm`) fusionado, mismo test común (174 entradas, 9 semillas). **Es cuantización de bitsandbytes en GPU, no la dinámica de PyTorch en CPU** (`evaluation/pi3_portabilidad.md`).

| Variante | BLEU | chrF | ΔBLEU vs fp16 (IC 95 %) | ΔchrF vs fp16 (IC 95 %) |
|---|---|---|---|---|
| fp16 (referencia) | 43.6 | 58.2 | — | — |
| int8 | 42.7 | 57.6 | -0.9 [-1.6, -0.1] * | -0.5 [-1.1, +0.1] |
| nf4 | 42.1 | 56.9 | -1.6 [-2.7, -0.6] * | -1.3 [-2.5, -0.3] * |

`*` = el intervalo no incluye 0 (pérdida o ganancia distinguible).

| Variante | Memoria GPU (modelo) | Latencia mediana (174 entradas, una por una) |
|---|---|---|
| fp16 | 6.17 GB | 0.83 s |
| int8 | 3.40 GB | 4.04 s |
| nf4 | 2.01 GB | 1.25 s |

GPU: Tesla T4 (Google Colab). Fuente: línea JSON que imprime cada corrida
(`merging/logs/cuant_<variante>.log`).

**Dato contraintuitivo que no ocultamos:** int8 es más lento que fp16 y que
nf4, a pesar de usar menos memoria. Es un efecto conocido de la
cuantización int8 de `bitsandbytes` (el costo de descuantizar en cada
operación puede superar el ahorro de ancho de banda en GPUs como la T4),
pero no investigamos la causa exacta en este proyecto — queda como
observación, no como conclusión. Quien necesite latencia baja en GPU debe
usar nf4 o fp16, no int8.

**Tiempos de la corrida completa** (`merging/logs/tiempos_cuantizacion.json`):
reconstruir el adaptador fusionado 92.7 s; traducir las 174 entradas en
fp16 307.7 s (~5.1 min), en int8 935.2 s (~15.6 min), en nf4 651.3 s
(~10.9 min). Total medido ≈ 33 min, más instalación de dependencias y
descarga del modelo base: ≈ 45 min de principio a fin en Colab (T4).
