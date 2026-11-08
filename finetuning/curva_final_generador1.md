# Entrenamiento completo de LoRA — generador1

Generado por `finetuning/resumen_curva.py` a partir de `finetuning/checkpoints/generador1/loss_log.json`. Mismo script y misma configuración de LoRA que el Generador 1 (verificado con `finetuning/verificar_config_identica.py`).

## Hardware y datos

- Hardware: Google Colab, GPU Tesla T4
- Tiempo total: ~20 min (1216 s, medido por el notebook; incluye cargar el modelo)
- Ejemplos de entrenamiento: 475; de validación: 58
- Pasos de entrenamiento registrados: 1425; épocas evaluadas: 3

## Curva de pérdida

| Época | Pérdida de entrenamiento (promedio) | Pérdida de validación |
|---|---|---|
| 1 | 0.7134 (mediana 0.6360) | 0.7580 ← mejor |
| 2 | 0.4004 (mediana 0.3293) | 0.8060 |
| 3 | 0.2051 (mediana 0.1211) | 0.9095 |

- Mejor época por validación: **1** (pérdida 0.7580). Se guardó el adaptador de esa época (`load_best_model_at_end`), no el de la última (3).
- Sobreajuste: **sí** — la validación de la última época es peor que la mejor mientras el entrenamiento sigue bajando.
