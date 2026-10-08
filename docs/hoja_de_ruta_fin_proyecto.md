# Hoja de ruta para terminar el proyecto (Fase 3)

Última actualización: 2026-10-07. Reemplaza como lista maestra a
`docs/pendientes_despliegue.md` (que sigue siendo el detalle de los
pendientes del despliegue). Cada paso dice **quién/dónde** lo hace, el
**comando** y **dónde se anota el resultado**.

## Estado de partida (hecho y verificado)

- Fase 2 completa: API, contenedor, seguridad, observabilidad, E2E,
  despliegue público en Hugging Face (ver `docs/despliegue.md`).
- **Datos de los 3 generadores listos**, sobre las mismas 100 semillas
  (`seeds/lote_01` + `lote_02`) y el mismo reparto fijo de semillas
  (`seeds/split_semillas.json`):

  | Generador | Modelo | Variantes limpias | Train / Val / Test |
  |---|---|---|---|
  | 1 | Groq `openai/gpt-oss-20b` | 587 | 475 / 58 / 54 |
  | 2 | Cohere `command-r-08-2024` | 632 | 513 / 64 / 55 |
  | 3 | Google `gemini-3.5-flash-lite` (ver nota) | 625 | 508 / 61 / 56 |
  | Mezcla 1+2+3 | — | 1844 | 1496 / 183 / 165 |

  Nota: el Generador 3 se cambió de `gemini-3.6-flash` a
  `gemini-3.5-flash-lite` porque el nivel gratuito del primero permite
  solo 20 solicitudes por día.
- Scripts listos y probados localmente: fusión (TIES / DARE+TIES /
  lineal), destilación multi-maestro, predicciones, test común,
  métricas (BLEU/chrF con desglose por fuente), tabla comparativa,
  hojas ciegas de evaluación humana, kappa de Fleiss/Cohen (verificado
  contra valores publicados).

## Paso 1 — Entrenar, fusionar y medir (Colab, ~3 h) — **lo haces tú**

1. Sube la rama `develop` (ya incluye los datos) y abre
   `finetuning/fase3_pipeline_colab.ipynb` en Google Colab con GPU.
2. Corre las celdas en orden. Entrena 4 adaptadores (g1, g2, g3,
   mezcla), fusiona (TIES, DARE+TIES, lineal), destila, genera
   predicciones de 9 modelos y calcula métricas.
3. Descarga `resultados_fase3.zip`, descomprímelo en la raíz del repo
   y revisa `evaluation/comparacion_fase3.md`.
4. **Pásame los resultados** (o la tabla) y yo: documento, corrijo lo
   que falle, y escribo el análisis. Qué mirar: si alguna curva de
   pérdida muestra sobreajuste (`finetuning/checkpoints/*/loss_log.json`)
   y si la fusión iguala o supera al mejor individual (PI2).

## Paso 2 — Evaluación humana (personas externas) — **depende de otras personas**

Requisito de la propuesta: mínimo 3 hablantes nativos por dialecto
(5 dialectos → 15 evaluadores, `evaluation/reclutamiento_evaluadores.md`).

1. Tras el Paso 1:
   ```bash
   python evaluation/preparar_evaluacion_humana.py --modelos baseline generador1 generador2 generador3 mezcla fusion_ties destilacion --items-por-dialecto 12
   ```
2. Envía a cada evaluador SOLO su `hojas/<dialecto>.csv` y
   `instrucciones_evaluador.md`. **No** envíes `clave_modelos.json`.
3. Guarda lo que devuelvan como
   `evaluation/evaluacion_humana/respuestas/<dialecto>__<nombre>.csv`.
4. `python evaluation/kappa.py --salida evaluation/resultados_evaluacion_humana.md`
5. Antes de mandarla, la rúbrica pide calibración cruzada entre dos
   del equipo (`evaluation/rubrica_humana.md`, sección final): todavía
   sin hacer.

## Paso 3 — Cierre del despliegue (esperas de tiempo/cuota)

Ver `docs/pendientes_despliegue.md`: carga con 20 y 50 concurrentes en
el Space (cuota de ZeroGPU), `duration` menor, arranque en frío, y la
decisión de portar métricas/retroalimentación al Space.

## Paso 4 — Portabilidad (PI3) — **lo hago yo tras el Paso 1**

Medir y reportar con números: tamaño del adaptador (~15 MB) vs. el
modelo base, latencia GPU (Space: 2.5 s) vs. CPU local (~55 s), y si el
sistema corre sin internet una vez descargados los pesos (se puede
verificar desconectado). Hoy no hay una medición de "corre sin
internet" hecha.

## Paso 5 — Paper y entrega — **lo hago yo con tus resultados**

`paper/main.tex`: completar resultados (tablas de métricas, kappa),
discusión de PI1/PI2/PI3 con las cifras reales, limitaciones honestas
(tamaño del test, referencias sintéticas, un solo modelo base,
`gemini-3.5-flash-lite`), y regenerar `paper/main.pdf`. También: data
cards de los generadores 2 y 3 (existe solo la del 1) y actualizar
`README.md`.

## Cosas que NO se pueden hacer desde aquí

- Entrenar/fusionar/evaluar con GPU (Colab).
- Evaluación humana (personas).
- `git push` al Space de Hugging Face (requiere tu token).
