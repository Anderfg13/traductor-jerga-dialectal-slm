# Borrador: resultados completos de la Fase 3 (para el paper)

> Consolida PI1 (parcial), PI2 y PI3. Cada cifra remite a su archivo. Lo que falta
> (evaluación humana, traductores comerciales, calidad cuantizada completa) figura como
> "No disponible" y no se rellena.

## PI1 — generador de datos
Parcial: solo métricas automáticas (`evaluation/comparacion_pi1_automatica.md`). Humano: **No disponible**
(`evaluation/analisis_pi1.md`).

## PI2 — fusión (completo con métricas automáticas)
Tabla de las cinco opciones y de todas las variantes: `evaluation/comparacion_completa_pi2.md`.

| Opción | BLEU | chrF |
|---|---|---|
| Base | 37.0 | 53.9 |
| Mejor individual (G3) | 42.3 | 57.9 |
| Mezcla | 42.4 | 57.2 |
| Fusión simple (mergekit) | 44.2 | 58.4 |
| Destilación multi-maestro | 43.9 | 58.3 |

Destilación − fusión simple: −0.6 BLEU [−2.5, +1.0], −0.1 chrF: marginal, con 95 min de T4 frente a
13 s-~20 min. La técnica de fusión no importa (43.7-44.2); importa promediar y no sumar.

## PI3 — modelo pequeño frente a otros sistemas y portabilidad
- Frente a LLMs generales (`docs/resultados_pi3.md`): −3.4 a −3.9 BLEU frente a gpt-oss-120b y qwen3.8-27b
  (significativo); no distinguible de command-r y gemini-lite; +3.5 sobre gpt-oss-20b, con sesgo de circularidad.
- Frente a DeepL (`evaluation/comparacion_pi3_comerciales.md`): BLEU 44.4 vs 44.2 (no distinguible), chrF 61.4 vs 58.4 (−3.1 [−6.5, −0.2]). Google Translate: **No disponible** (sin clave).
- Portabilidad (`evaluation/pi3_portabilidad.md`): adaptador de 14.8 MB sobre base de 6.17 GB; 0 conexiones; CPU 46-65 s,
  int8 28 s (3 frases, sin calidad medida), GPU ~2 s.

## Análisis cualitativo
`evaluation/analisis_cualitativo.md` (un lector, preliminar): de los 34 casos peor puntuados, ~47 % errores de significado,
~24 % pierden matiz, ~29 % aceptables.

## Lo que ningún resultado de esta fase puede afirmar
Generalización más allá de las 9 expresiones del test; calidad percibida por nativos; efecto de la cuantización sobre la calidad.
