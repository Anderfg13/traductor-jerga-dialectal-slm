# Entrenamiento completo de LoRA — generador2

Generado por `finetuning/resumen_curva.py` a partir de `finetuning/checkpoints/generador2/loss_log.json`. Mismo script y misma configuración de LoRA que el Generador 1 (verificado con `finetuning/verificar_config_identica.py`).

## Hardware y datos

- Hardware: Google Colab, GPU Tesla T4
- Tiempo total: ~19 min (tiempo de la celda de Colab, incluye cargar el modelo)
- Ejemplos de entrenamiento: 513; de validación: 64
- Pasos de entrenamiento registrados: 1539; épocas evaluadas: 3

## Curva de pérdida

| Época | Pérdida de entrenamiento (promedio) | Pérdida de validación |
|---|---|---|
| 1 | 0.5417 (mediana 0.4861) | 0.5793 ← mejor |
| 2 | 0.2868 (mediana 0.2242) | 0.6071 |
| 3 | 0.1391 (mediana 0.0665) | 0.7275 |

- Mejor época por validación: **1** (pérdida 0.5793). Se guardó el adaptador de esa época (`load_best_model_at_end`), no el de la última (3).
- Sobreajuste: **sí** — la validación de la última época es peor que la mejor mientras el entrenamiento sigue bajando.
