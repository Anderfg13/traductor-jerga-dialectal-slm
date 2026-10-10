# Entrenamiento completo de LoRA — mezcla

Generado por `finetuning/resumen_curva.py` a partir de `finetuning/checkpoints/mezcla/loss_log.json`. Mismo script y misma configuración de LoRA que el Generador 1 (verificado con `finetuning/verificar_config_identica.py`).

## Hardware y datos

- Hardware: Google Colab, GPU Tesla T4
- Tiempo total: ~52 min (tiempo de la celda de Colab, incluye cargar el modelo)
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

## Balance de la mezcla entre generadores

Criterio de calidad: que ningún generador domine solo por tener más ejemplos limpios.

| Generador | Ejemplos de entrenamiento | % | Semillas distintas |
|---|---|---|---|
| cohere | 513 | 34.3 % | 81 |
| google | 508 | 34.0 % | 81 |
| groq | 475 | 31.8 % | 81 |

Diferencia máxima entre generadores: 2.5 puntos porcentuales (38 ejemplos). **No se recortó para igualar**: los tres generadores cubren exactamente las mismas semillas de entrenamiento y cada uno generó 5-8 variantes por semilla, así que la mezcla ya sale casi equilibrada; igualar al mínimo habría descartado ejemplos válidos sin que ningún generador dominara. Los splits son por semilla y usan el mismo reparto fijo que los demás (`seeds/split_semillas.json`), igual que en la Sesión 12.
