# PI3: modelo pequeño ajustado frente a sistemas de propósito general

Generado por `evaluation/comparar_sistemas_generales.py`. Mismo test común (`evaluation/test_comun.json`), mismo prompt de sistema, BLEU/chrF con las mismas referencias. **Lectura con cautela**: 9 semillas de prueba, una corrida, sin evaluación humana.

## 1. Solo referencias humanas del banco de semillas (`oro`, n = 9, sin ventaja circular)

| Sistema | Parámetros | n | BLEU | chrF |
|---|---|---|---|---|
| Qwen2.5-3B base (sin ajustar) | 3B (+15 MB de adaptador) | 9 | 1.4 | 8.6 |
| SLM ajustado: Generador 3 | 3B (+15 MB de adaptador) | 9 | 3.8 | 13.9 |
| SLM ajustado: mezcla | 3B (+15 MB de adaptador) | 9 | 5.3 | 10.7 |
| SLM ajustado: fusión lineal (mergekit) | 3B (+15 MB de adaptador) | 9 | 4.9 | 14.1 |
| SLM ajustado: fusión TIES (mergekit) | 3B (+15 MB de adaptador) | 9 | 4.3 | 11.7 |
| gpt-oss-20b | 20B | 9 | 5.4 | 17.1 |
| command-r | ~32-35B (no verificado) | 9 | 10.6 | 25.4 |
| gemini-3.5-flash-lite | no publicado | 9 | 5.2 | 18.1 |
| gpt-oss-120b | 120B | 9 | 7.4 | 20.3 |
| qwen3.8-27b | 27B | 9 | 11.5 | 17.8 |

## 2. Sin ventaja circular: cada generador excluye sus propias referencias

Cada fila compara el sistema y los modelos pequeños sobre las **mismas** entradas: las del test común cuya referencia NO escribió ese sistema. Los sistemas que no fueron generadores usan todo el test común.

### gpt-oss-20b (excluye `generador1`; n = 120 traducciones evaluadas de 120 entradas)

| Sistema | BLEU | chrF |
|---|---|---|
| **gpt-oss-20b** | 38.1 | 55.3 |
| Qwen2.5-3B base (sin ajustar) | 35.1 | 51.9 |
| SLM ajustado: Generador 3 | 40.9 | 56.2 |
| SLM ajustado: mezcla | 41.0 | 55.3 |
| SLM ajustado: fusión lineal (mergekit) | 41.6 | 56.1 |
| SLM ajustado: fusión TIES (mergekit) | 41.6 | 56.0 |

### command-r (excluye `generador2`; n = 119 traducciones evaluadas de 119 entradas)

| Sistema | BLEU | chrF |
|---|---|---|
| **command-r** | 43.7 | 60.5 |
| Qwen2.5-3B base (sin ajustar) | 35.4 | 53.6 |
| SLM ajustado: Generador 3 | 40.4 | 57.2 |
| SLM ajustado: mezcla | 40.2 | 56.8 |
| SLM ajustado: fusión lineal (mergekit) | 42.4 | 57.5 |
| SLM ajustado: fusión TIES (mergekit) | 43.0 | 57.6 |

### gemini-3.5-flash-lite (excluye `generador3`; n = 117 traducciones evaluadas de 118 entradas)

| Sistema | BLEU | chrF |
|---|---|---|
| **gemini-3.5-flash-lite** | 47.6 | 62.8 |
| Qwen2.5-3B base (sin ajustar) | 39.7 | 55.4 |
| SLM ajustado: Generador 3 | 44.1 | 59.5 |
| SLM ajustado: mezcla | 44.4 | 58.6 |
| SLM ajustado: fusión lineal (mergekit) | 47.9 | 60.7 |
| SLM ajustado: fusión TIES (mergekit) | 46.6 | 59.5 |

### gpt-oss-120b (test común completo; n = 174 traducciones evaluadas de 174 entradas)

| Sistema | BLEU | chrF |
|---|---|---|
| **gpt-oss-120b** | 48.0 | 62.8 |
| Qwen2.5-3B base (sin ajustar) | 37.0 | 53.9 |
| SLM ajustado: Generador 3 | 42.3 | 57.9 |
| SLM ajustado: mezcla | 42.4 | 57.2 |
| SLM ajustado: fusión lineal (mergekit) | 44.2 | 58.4 |
| SLM ajustado: fusión TIES (mergekit) | 44.0 | 58.0 |

### qwen3.8-27b (test común completo; n = 173 traducciones evaluadas de 174 entradas)

| Sistema | BLEU | chrF |
|---|---|---|
| **qwen3.8-27b** | 47.7 | 62.3 |
| Qwen2.5-3B base (sin ajustar) | 37.0 | 53.9 |
| SLM ajustado: Generador 3 | 42.3 | 57.9 |
| SLM ajustado: mezcla | 42.4 | 57.2 |
| SLM ajustado: fusión lineal (mergekit) | 44.2 | 58.4 |
| SLM ajustado: fusión TIES (mergekit) | 44.0 | 58.0 |

## Cómo leerlo

- Los generadores tienen ventaja en sus propias referencias; por eso la sección 2 las excluye. Aun así, entre los generadores y los SLM ajustados con sus datos hay una dependencia: el SLM aprendió a imitar a esos LLM.
- No hay Google Translate ni DeepL: son LLMs de propósito general, no sistemas de traducción dedicados.
- BLEU/chrF miden coincidencia con una referencia, no retención de matices.
