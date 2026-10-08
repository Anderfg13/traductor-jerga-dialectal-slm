# Resultados de la Fase 3 (corrida completa, 2026-10-08)

Salida de `finetuning/fase3_pipeline_colab.ipynb` (Google Colab, GPU
Tesla T4). Corrida completa y válida: los 4 adaptadores se entrenaron
con las mismas semillas por split y la **misma configuración de LoRA**
(`finetuning/verificar_config_identica.py`: OK), y el Generador 1 se
reentrenó con 475 ejemplos (en la primera corrida se había saltado por
error y se descartó; ver `BITACORA.md` Sesión 43).

Fuentes: `evaluation/comparacion_fase3.md` (BLEU/chrF),
`evaluation/analisis_bootstrap.md` (intervalos),
`evaluation/reportes/*.json`, `finetuning/curva_final_*.md`,
`finetuning/tiempos_fase3_corrida2.json`.

**Alcance y cautela.** El test común tiene 174 entradas de **solo 9
semillas**; una corrida por modelo; la mayoría de las referencias son
sintéticas. Los intervalos de 95 % salen de remuestrear semillas
completas. Las conclusiones de abajo son **señales tentativas**, no
resultados definitivos, y no incluyen evaluación humana ni PI3.

## Resultados (BLEU / chrF globales, IC 95 %)

| Modelo | BLEU | chrF |
|---|---|---|
| Base sin ajustar | 37.0 [34.3, 40.1] | 53.9 [51.8, 55.9] |
| LoRA Generador 1 (Groq) | 42.2 [38.7, 46.3] | 57.5 [55.5, 59.7] |
| LoRA Generador 2 (Cohere) | 40.7 [38.7, 43.3] | 55.3 [53.6, 57.1] |
| LoRA Generador 3 (Google lite) | 42.3 [39.0, 46.7] | 57.9 [55.7, 61.3] |
| LoRA sobre la mezcla 1+2+3 | 42.4 [39.9, 45.5] | 57.2 [55.2, 59.8] |
| Fusión TIES | 43.7 [40.9, 47.1] | 58.2 [56.4, 60.4] |
| Fusión DARE+TIES | 43.8 [40.5, 47.5] | 57.7 [55.6, 60.2] |
| Fusión lineal (promedio) | 35.3 [32.5, 37.5] | 51.5 [49.6, 53.8] |
| Fusión por destilación multi-maestro | 43.9 [40.8, 47.5] | 58.3 [56.5, 60.5] |

## Qué sugieren los datos

**Ajuste fino.** Una primera señal indica que ajustar con datos
sintéticos ayuda: los tres adaptadores individuales superan al base en
BLEU (+3.7 a +5.2, intervalo sin 0); en chrF el Generador 2 (+1.4) no se
distingue del base.

**PI1 — efecto del generador (tentativo).** Los Generadores 1 y 3 no se
distinguen entre sí (ΔBLEU +0.1, ΔchrF −0.5, intervalos amplios). El
Generador 2 (Cohere) queda por debajo de ambos en chrF (G1−G2 +2.3
[+0.2, +4.2]; G3−G2 +2.7 [+0.8, +5.3]) y no se distingue en BLEU. Una
hipótesis, **no probada**, es que Cohere generó más registro formal y
menos jerga con el mismo prompt (20 % formal / 19 % jerga, frente a 12 % /
30 % de G1 y 7 % / 33 % de G3; `generation/comparacion_generadores.md`).
El Generador 3 es un modelo "lite" más pequeño, así que "qué LLM es" no
se separa de "qué tamaño tiene". Cada generador además sale mejor en la
columna cuyas referencias escribió su propio LLM (sesgo de referencia).

**PI2 — fusión (tentativo).** Las tres fusiones útiles (TIES, DARE+TIES,
destilación) igualan al mejor modelo individual y lo superan por ~+1.4
BLEU y entre −0.3 y +0.8 chrF, **pero ese margen no se distingue del ruido**
(intervalos que incluyen 0: p. ej. TIES − G1 +1.4 [−0.7, +4.1]). Sí
superan de forma distinguible al Generador 2 y, en BLEU, al modelo
entrenado sobre la mezcla (TIES − mezcla +1.3 [+0.3, +2.4]; en chrF no).
No se puede afirmar que la fusión supere al mejor individual; solo que
no es peor y que una primera señal apunta a que podría ser algo mejor.

**La destilación no aporta sobre TIES.** Destilación − TIES: ΔBLEU −0.0,
ΔchrF +0.1 (indistinguibles). Costó ~95 min de GPU frente a ~24 s de
TIES. Con estos datos no se justifica el costo extra.

**La fusión lineal perjudica.** Queda por debajo del base en chrF (−2.4
[−4.4, −0.2]) y muy por debajo del resto. Es plausible (no verificado)
que se deba a promediar por separado las matrices A y B de cada
adaptador LoRA, lo que no equivale a promediar sus actualizaciones. Es un
resultado sobre esta implementación, no sobre la fusión en general.

**Sobreajuste rápido.** En los cuatro entrenamientos la mejor validación
es la época 1 y empeora después mientras el entrenamiento baja; el early
stopping guardó la época 1. (Las pérdidas de validación no son
comparables entre generadores: cada uno valida con sus propias
variantes.)

**Subconjunto "oro"** (referencias del equipo, sin sesgo de generador):
solo **9 entradas**, BLEU entre 0.9 y 10.5. Un valor como el 10.5 de
DARE+TIES no se interpreta; con n=9 no permite concluir nada.

## Tiempos (GPU Tesla T4)

| Paso | Tiempo | Fuente |
|---|---|---|
| Entrenar Generador 1 (475 ejemplos) | ~20 min | `tiempos_fase3_corrida2.json` |
| Entrenar Generador 2 (513) | ~19 min | celda de Colab, corrida 1 |
| Entrenar Generador 3 (508) | ~18 min | celda de Colab, corrida 1 |
| Entrenar mezcla (1496) | ~52 min | celda de Colab, corrida 1 |
| Fusión TIES / DARE+TIES / lineal | 24 s / 15 s / 13 s | `tiempos_fase3_corrida2.json` |
| Destilación multi-maestro | ~95 min | `tiempos_fase3_corrida2.json` |
| Predicciones sobre el test común (174), por modelo | ~5.6 min | `tiempos_fase3_corrida2.json` |

Los tiempos incluyen cargar el modelo base. Un adaptador pesa ~15 MB
frente a ~6 GB del modelo base. Una fusión por TIES cuesta segundos y no
requiere datos; reentrenar con la mezcla cuesta ~52 min.

## Limitaciones

- 9 semillas de prueba; una sola corrida por modelo (no se midió la
  variación entre semillas aleatorias de entrenamiento).
- Referencias mayormente sintéticas; sin evaluación humana todavía.
- BLEU/chrF miden coincidencia con una referencia, no retención de
  matices.
- Un solo modelo base (Qwen2.5-3B-Instruct): no se sabe si los
  resultados se sostienen con otro.
- PI3 (portabilidad, competitividad frente a sistemas generales) no se
  evaluó.
