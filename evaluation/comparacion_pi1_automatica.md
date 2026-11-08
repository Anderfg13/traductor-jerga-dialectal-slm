# Comparación automática para PI1: modelos individuales

BLEU y chrF de los adaptadores LoRA de los tres generadores sobre el **mismo** conjunto de prueba (`evaluation/test_comun.json`). Generado por `evaluation/comparacion_pi1.py`.

## Verificación del conjunto de evaluación

- Los 4 modelos (base y los 3 adaptadores) se evaluaron sobre **las mismas 174 entradas**, con las mismas referencias y las mismas **9 semillas** (`sem-012, sem-019, sem-042, sem-053, sem-067, sem-078, sem-079, sem-088, sem-092`); el script aborta si cualquier modelo difiere.
- Es el mismo conjunto para todos, no uno derivado de cada generador. Contiene, por semilla de test: la expresión original con la **referencia humana del banco de semillas** (fuente `oro`) y las variantes de test de los tres generadores. Composición: `generador1` 54, `generador2` 55, `generador3` 56, `oro` 9.
- Las 9 semillas de test son las mismas que las de `seeds/split_semillas.json` y ninguna estuvo en entrenamiento de ningún modelo.

## Global (todas las referencias)

| Modelo | n | BLEU | chrF |
|---|---|---|---|
| Base sin ajustar (referencia) | 174 | 37.0 | 53.9 |
| LoRA Generador 1 (Groq) | 174 | 42.2 | 57.5 |
| LoRA Generador 2 (Cohere) | 174 | 40.7 | 55.3 |
| LoRA Generador 3 (Google lite) | 174 | 42.3 | 57.9 |

## Solo referencias humanas del banco de semillas (fuente `oro`)

Es la comparación que usa **únicamente** las traducciones escritas por el equipo, sin sesgo hacia ningún LLM generador. Tiene solo 9 entradas (frases cortas e idiomáticas), así que **no permite concluir nada**; se muestra por completitud.

| Modelo | n | BLEU | chrF |
|---|---|---|---|
| Base sin ajustar (referencia) | 9 | 1.4 | 8.6 |
| LoRA Generador 1 (Groq) | 9 | 4.0 | 10.5 |
| LoRA Generador 2 (Cohere) | 9 | 3.2 | 10.5 |
| LoRA Generador 3 (Google lite) | 9 | 3.8 | 13.9 |

## Por dialecto (todas las referencias)

BLEU / chrF; entre paréntesis, número de entradas.

| Modelo | Andina | Caribeña | Chilena | Mexicana | Rioplatense |
|---|---|---|---|---|---|
| Base sin ajustar (referencia) | 35.7 / 54.2 (38) | 36.9 / 54.3 (39) | 29.7 / 44.3 (19) | 44.9 / 58.1 (40) | 33.6 / 52.3 (38) |
| LoRA Generador 1 (Groq) | 36.0 / 55.2 (38) | 41.5 / 57.1 (39) | 39.0 / 51.9 (19) | 48.7 / 61.2 (40) | 44.7 / 59.2 (38) |
| LoRA Generador 2 (Cohere) | 37.2 / 54.9 (38) | 40.3 / 54.5 (39) | 44.6 / 56.4 (19) | 42.2 / 54.6 (40) | 41.5 / 57.0 (38) |
| LoRA Generador 3 (Google lite) | 38.7 / 56.5 (38) | 42.0 / 56.8 (39) | 39.5 / 53.4 (19) | 49.8 / 63.5 (40) | 37.5 / 57.4 (38) |

## Cómo leerla (respuesta preliminar a PI1)

- **Hay diferencia medible**: el adaptador del Generador 2 (Cohere) da menos chrF que los de los Generadores 1 y 3, y el 1 y el 3 son casi iguales.
- **Qué tanto de esa diferencia es ruido**: ver `evaluation/analisis_bootstrap.md` (intervalos de 95 % por remuestreo de semillas). G1 − G2: +2.3 chrF [+0.2, +4.2]; G3 − G2: +2.7 [+0.8, +5.3]; G1 − G3: −0.5 [−2.4, +1.1] (no distinguible). En BLEU no se distingue ninguno de los tres entre sí.
- **Con solo 9 semillas de prueba** cualquier desglose por dialecto (1 o 2 semillas por dialecto) es anecdótico: no se interpretan diferencias entre dialectos.
- **Sesgo de referencia**: cada generador sale favorecido con las referencias de su propio LLM (ver `evaluation/comparacion_fase3.md`); por eso la comparación limpia sería solo con referencias humanas, que aquí son 9 entradas.
- Es una respuesta **tentativa** a PI1; falta la evaluación humana.
