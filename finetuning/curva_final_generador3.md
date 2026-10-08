# Entrenamiento completo de LoRA — generador3

Generado por `finetuning/resumen_curva.py` a partir de `finetuning/checkpoints/generador3/loss_log.json`. Mismo script y misma configuración de LoRA que el Generador 1 (verificado con `finetuning/verificar_config_identica.py`).

## Hardware y datos

- Hardware: NO REGISTRADO
- Tiempo total: NO REGISTRADO
- Ejemplos de entrenamiento: 508; de validación: 61
- Pasos de entrenamiento registrados: 1524; épocas evaluadas: 3

## Curva de pérdida

| Época | Pérdida de entrenamiento (promedio) | Pérdida de validación |
|---|---|---|
| 1 | 0.8351 (mediana 0.7731) | 0.7631 ← mejor |
| 2 | 0.5404 (mediana 0.4753) | 0.8775 |
| 3 | 0.3003 (mediana 0.2458) | 1.1006 |

- Mejor época por validación: **1** (pérdida 0.7631). Se guardó el adaptador de esa época (`load_best_model_at_end`), no el de la última (3).
- Sobreajuste: **sí** — la validación de la última época es peor que la mejor mientras el entrenamiento sigue bajando.
