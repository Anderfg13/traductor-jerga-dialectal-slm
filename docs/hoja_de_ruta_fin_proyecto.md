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

---

## Lista de verificación (lo que sigue abierto)

Marca cada casilla cuando esté hecho y pega aquí el dato que se pide.

**Tuyo (Colab y personas)**
- [ ] Correr `finetuning/fase3_pipeline_colab.ipynb` completo en Colab con GPU. Pegar aquí la GPU usada y el tiempo total: ______
- [ ] Descargar `resultados_fase3.zip`, descomprimirlo en la raíz del repo y pasarme `evaluation/comparacion_fase3.md`.
- [ ] Revisar las curvas de `finetuning/checkpoints/*/loss_log.json` (¿sobreajuste?).
- [ ] Si `destilacion_multimaestro.py` falla en Colab (no se corrió nunca con el modelo real), pegarme el error.
- [ ] Calibración cruzada de la rúbrica entre dos del equipo (5 ejemplos, diferencia máx. 1 punto).
- [ ] Reclutar mínimo 3 hablantes nativos por dialecto (5 dialectos = 15 personas): `evaluation/reclutamiento_evaluadores.md`. Anotar nombres/contacto en `evaluation/evaluadores.csv`.
- [ ] Enviar solo `hojas/<dialecto>.csv` + `instrucciones_evaluador.md` (nunca `clave_modelos.json`) y recoger las respuestas en `evaluation/evaluacion_humana/respuestas/`.
- [ ] Pasada 24 h después del 2026-10-07: repetir la carga del Space con 20 y 50 concurrentes (`python api/prueba_carga_space.py --niveles 5 20 50`, ver `docs/pendientes_despliegue.md`).
- [ ] `git push` al Space si se decide bajar `duration` (requiere tu token de Hugging Face).
- [ ] **Que un compañero que no haya visto el documento lea `paper/main.pdf` de principio a fin** y anote cualquier referencia rota, sección confusa o a medio escribir (criterio de aceptación de la integración del paper; yo solo pude verificar la parte mecánica).

**Mío (cuando lleguen los resultados)**
- [ ] Documentar los resultados de Colab y corregir lo que falle.
- [ ] Portabilidad (PI3): tamaños, latencia, prueba sin internet.
- [ ] Actualizar `paper/main.tex`: sección de Resultados con las tablas de la Fase 3, discusión de PI1/PI2/PI3, limitaciones; recompilar con `paper/auditar_tex.py` y dos pasadas de pdflatex.
- [ ] Data cards de los generadores 2 y 3; actualizar `generation/test_apis.py` y README con `gemini-3.5-flash-lite`.
- [ ] Decidir con el equipo si se portan métricas/retroalimentación al Space (`docs/pendientes_despliegue.md`, punto 4).

**Sustentación (Fase 2) — tuyo y del equipo**
- [ ] Averiguar el tiempo asignado a la sustentación y anotarlo en `docs/banco_preguntas_fase2.md`.
- [ ] Ensayo completo cronometrado con las tres personas y la demo en vivo; llenar la tabla de tiempos (debe caer dentro del tiempo asignado).
- [ ] Que cada integrante responda **sin leerla** al menos una pregunta nueva del banco (despliegue/modelo/latencia/cuota/privacidad/generador 3/PEFT/alcance) y marcar la casilla.
- [ ] **No gastar la cuota de GPU del Space antes de la demo** (nada de `prueba_carga_space.py` ese día); probar el flujo de la demo como máximo 1-2 veces.
- [ ] Grabar el video del Plan B (30-40 s) de una solicitud real al Space.

**Después de entrenar en Colab (por cada adaptador: generador2, generador3, mezcla)**
- [ ] Verificar que `python finetuning/verificar_config_identica.py` termina en `OK` con los 4 adaptadores (la celda del notebook ya lo corre). Si falla, la comparación de PI1 no es válida: pegarme la salida.
- [ ] Generar el informe de cada curva con los datos reales: `python finetuning/resumen_curva.py generador2 --hardware "<GPU usada>" --tiempo "<minutos>" --ejemplos-train 513 --ejemplos-val 64` (ejemplos: G2 513/64, G3 508/61, mezcla 1496/183). Crea `finetuning/curva_final_generador2.md`.
- [ ] Prueba manual rápida de cada adaptador nuevo (3-5 frases, ver `evaluation/generar_predicciones.py`) y anotar si las traducciones son coherentes.
