# PI3: ¿es posible un modelo pequeño, eficiente, competitivo y portable?

Resumen de la evaluación de PI3 (2026-10-08). Detalle y fuentes:
`evaluation/pi3_portabilidad.md`, `evaluation/comparacion_pi3_sistemas_generales.md`
y `evaluation/analisis_bootstrap_pi3.md`. Es una **respuesta parcial y
tentativa**: 9 semillas de prueba, una corrida por modelo, sin evaluación
humana y sin sistemas de traducción dedicados.

## Veredicto, parte por parte

| Pregunta | Respuesta con los datos |
|---|---|
| ¿Es pequeño? | Sí: 3B de parámetros (6.17 GB en bfloat16) y 14.8 MB por especialización (0.24 % del base). |
| ¿Es portable (corre sin internet)? | **Sí**: con la red bloqueada a nivel de sockets y Hugging Face offline, 0 intentos de conexión y traducciones correctas. Requiere ~8 GB de RAM libre (6.7 GB medidos). |
| ¿Es eficiente? | Depende del hardware: en CPU, 46-65 s por traducción (no interactivo); con GPU T4, ~1.9 s; en el servicio público (ZeroGPU), 2.5 s. No se evaluó cuantización. |
| ¿Es competitivo con sistemas de propósito general? | **Solo en parte.** Frente a LLM grandes que no generaron datos (gpt-oss-120b, qwen3.8-27b) queda por debajo de forma distinguible (−3.4 a −3.9 BLEU, −4.0 a −4.5 chrF). Frente a `command-r` y `gemini-3.5-flash-lite` no se distingue en BLEU, y supera a `gpt-oss-20b` en BLEU (+3.5, intervalo [+0.2, +7.0]). |

## Competitividad en cifras

Mejor modelo pequeño: fusión lineal con `mergekit` (44.2 BLEU / 58.4 chrF
sobre el test común). Diferencia = pequeño − general, IC 95 % por bootstrap
sobre semillas, mismas entradas para ambos:

| Sistema general | n | ΔBLEU | ΔchrF |
|---|---|---|---|
| gpt-oss-120b (no generador) | 174 | −3.9 [−7.2, −1.5] * | −4.5 [−7.2, −2.6] * |
| qwen3.8-27b (no generador) | 173 | −3.4 [−6.8, −0.4] * | −4.0 [−6.3, −2.1] * |
| command-r (sin sus referencias) | 119 | −1.2 [−4.2, +2.3] | −2.9 [−5.4, +0.1] |
| gemini-3.5-flash-lite (sin sus referencias) | 117 | +0.6 [−2.8, +4.0] | −2.0 [−4.7, +0.4] |
| gpt-oss-20b (sin sus referencias) | 120 | +3.5 [+0.2, +7.0] * | +0.8 [−1.6, +3.3] |

`*` = el intervalo no incluye 0. Con los LLM grandes, el modelo pequeño
recorre más de la mitad de la distancia entre el modelo base (37.0 BLEU) y
ellos (48.0): 7.2 de 11.0 puntos.

## Cautelas que cambian la lectura

- **Sesgo a favor del modelo pequeño frente a los generadores**: aprendió
  de las traducciones de esos mismos LLM; "igualarlos" es en parte imitarlos.
  Por eso la comparación más limpia es la de los dos LLM grandes que no
  generaron datos, y ahí **pierde**.
- **Referencias humanas (n = 9)**: los LLM grandes puntúan más alto que el
  modelo pequeño (p. ej. 11.5 vs 4.9 BLEU, qwen3.8-27b vs fusión lineal). La
  brecha parece mayor que con referencias sintéticas, pero con 9 entradas no
  permite concluir nada.
- **No hay Google Translate ni DeepL** (sin clave): lo comparado son LLM de
  propósito general, no sistemas de traducción automática dedicados.
- **El tamaño de `command-r` y de `gemini-3.5-flash-lite` no está
  verificado** (se marca así en el informe).
- La prueba sin red bloquea los sockets dentro del proceso; no equivale a
  desconectar físicamente la máquina, y el primer arranque sí necesita
  internet para bajar los pesos. Se probó un adaptador, en CPU, no el servicio
  completo ni la imagen Docker.
- BLEU/chrF miden coincidencia con una referencia, no retención de matices.

## Lo que queda de PI3

- Comparar contra sistemas de traducción dedicados (Google Translate, DeepL)
  con la misma métrica.
- Cuantización (int8/int4) y formatos ligeros (GGUF) para CPU: probablemente
  acerquen el uso interactivo, no medido.
- Evaluación humana (retención de matices), que es lo que BLEU/chrF no miden.

## Frente a DeepL

Ver `evaluation/comparacion_pi3_comerciales.md` (generado por `evaluation/comparar_comerciales.py`): BLEU 44.4 (DeepL) vs 44.2 (fusion simple), diferencia +0.0 [-3.9, +3.9]; chrF 61.4 vs 58.4, diferencia -3.1 [-6.5, -0.2]. Google Translate no se evaluo (sin clave).
