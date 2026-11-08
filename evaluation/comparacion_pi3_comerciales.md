# PI3: modelo pequeño frente a traductores dedicados (Google Translate, DeepL)

Generado por `evaluation/comparar_comerciales.py`. Mismo test común. **Lectura con cautela**: 9 semillas de prueba, una corrida, referencias mayormente sintéticas, sin evaluación humana.

**No se evaluaron: google-translate** (sin clave de API o sin traducciones en caché). No hay resultado para ellos.

## Test común completo (n = 174)

| Sistema | BLEU | chrF |
|---|---|---|
| deepl (174) | 44.4 | 61.4 |
| Qwen2.5-3B base (sin ajustar) (174) | 37.0 | 53.9 |
| SLM ajustado: Generador 3 (174) | 42.3 | 57.9 |
| SLM ajustado: mezcla (174) | 42.4 | 57.2 |
| SLM ajustado: fusión lineal (mergekit) (174) | 44.2 | 58.4 |

## Solo referencias humanas (`oro`, sin sesgo de LLM) (n = 9)

| Sistema | BLEU | chrF |
|---|---|---|
| deepl (9) | 16.1 | 26.9 |
| Qwen2.5-3B base (sin ajustar) (9) | 1.4 | 8.6 |
| SLM ajustado: Generador 3 (9) | 3.8 | 13.9 |
| SLM ajustado: mezcla (9) | 5.3 | 10.7 |
| SLM ajustado: fusión lineal (mergekit) (9) | 4.9 | 14.1 |

## Incertidumbre: fusión lineal (mergekit) − traductor

1000 remuestreos de semillas con reemplazo, IC 95 %; `*` = el intervalo no incluye 0.

| Traductor | ΔBLEU | ΔchrF |
|---|---|---|
| deepl | +0.0 [-3.9, +3.9] | -3.1 [-6.5, -0.2] * |

Un traductor dedicado no usa el prompt de sistema del proyecto ni conoce el dialecto: si queda por debajo, es información sobre la jerga dialectal, no un juicio general de calidad.
