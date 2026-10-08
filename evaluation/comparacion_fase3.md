# Comparación de modelos (Fase 3)

Cada celda es **BLEU / chrF** sobre el test común (`evaluation/test_comun.json`).

| Modelo | Global | Oro (ref. humana) | Ref. g1 | Ref. g2 | Ref. g3 |
|---|---|---|---|---|---|
| Base sin ajustar (zero-shot) | 37.0 / 53.9 | 1.4 / 8.6 (n=9) | 38.2 / 58.0 (n=54) | 40.7 / 54.6 (n=55) | 31.8 / 51.3 (n=56) |
| LoRA Generador 2 (Cohere) | 40.7 / 55.3 | 3.2 / 10.5 (n=9) | 41.9 / 59.4 (n=54) | 47.4 / 58.6 (n=55) | 33.4 / 50.6 (n=56) |
| LoRA Generador 3 (Google) | 42.3 / 57.9 | 3.8 / 13.9 (n=9) | 42.4 / 61.4 (n=54) | 45.7 / 59.5 (n=55) | 38.3 / 55.2 (n=56) |
| LoRA sobre la mezcla 1+2+3 | 42.4 / 57.2 | 5.3 / 10.7 (n=9) | 42.3 / 61.0 (n=54) | 46.4 / 58.1 (n=55) | 37.9 / 54.8 (n=56) |

Ver la docstring de `evaluation/tabla_comparativa.py` para cómo interpretar las columnas.
