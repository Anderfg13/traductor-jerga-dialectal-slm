# Entrenamiento completo de LoRA — mezcla

Generado por `finetuning/resumen_curva.py` a partir de `finetuning/checkpoints/mezcla/loss_log.json`. Mismo script y misma configuración de LoRA que el Generador 1 (verificado con `finetuning/verificar_config_identica.py`).

## Hardware y datos

- Hardware: NO REGISTRADO
- Tiempo total: NO REGISTRADO
- Ejemplos de entrenamiento: 1496; de validación: 183
- Pasos de entrenamiento registrados: 4488; épocas evaluadas: 3

## Curva de pérdida

| Época | Pérdida de entrenamiento (promedio) | Pérdida de validación |
|---|---|---|
| 1 | 0.6634 (mediana 0.5988) | 0.6902 ← mejor |
| 2 | 0.4287 (mediana 0.3709) | 0.7267 |
| 3 | 0.2522 (mediana 0.1789) | 0.7924 |

- Mejor época por validación: **1** (pérdida 0.6902). Se guardó el adaptador de esa época (`load_best_model_at_end`), no el de la última (3).
- Sobreajuste: **sí** — la validación de la última época es peor que la mejor mientras el entrenamiento sigue bajando.
