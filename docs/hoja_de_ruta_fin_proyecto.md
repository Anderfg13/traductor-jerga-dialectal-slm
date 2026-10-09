# Hoja de ruta para terminar el proyecto (Fase 3)

Última actualización: 2026-10-07. Reemplaza como lista maestra a
`docs/pendientes_despliegue.md` (que sigue siendo el detalle de los
pendientes del despliegue). Cada paso dice **quién/dónde** lo hace, el
**comando** y **dónde se anota el resultado**.

## PENDIENTES ACTUALES (lista consolidada, 2026-10-08)

**Esta sección es la única que vale.** Las casillas de más abajo son un registro
histórico: varias aparecen sin marcar aunque ya se hicieron (corridas de Colab,
fusiones, aislamiento del promedio con PEFT, PI3, paper). Si algo de abajo
contradice esta sección, manda esta.

### A. Depende de ti o de otras personas

**Evaluación humana (PI1) — lo más importante que falta**
- [ ] Conseguir **3 evaluadores nativos por dialecto** (Caribeña, Andina, Rioplatense, Mexicana, Chilena = 15) y anotarlos en `evaluation/evaluadores.csv` con un ID (E1, E2...), no con nombre real. Hoy está vacío.
- [ ] Calibración cruzada de la rúbrica entre dos del equipo (5 ejemplos, diferencia máx. de 1 punto; ver el final de `evaluation/rubrica_humana.md`).
- [ ] Decidir si se añade el modelo base como control en la ronda.
- [ ] Enviar a cada evaluador **solo** su hoja (`evaluation/evaluacion_humana/hojas/<Dialecto>.csv`) y las instrucciones, con el texto de `evaluation/mensaje_evaluadores_pi1.md`. No compartir el repositorio ni la clave.
- [ ] **Guardar `evaluation/evaluacion_humana/clave_modelos.json` en un lugar seguro** (no está en git; si se pierde, la ronda no se puede interpretar: solo queda su hash).
- [ ] Guardar las hojas devueltas en `evaluation/evaluacion_humana/respuestas/` como `<Dialecto>__<ID>.csv` y avisarme.

**Paper**
- [ ] Que **un compañero que no lo haya visto lo lea de principio a fin** y anote referencias rotas o partes confusas.
- [ ] Que **Mariana y Paula revisen** las secciones de Resultados y Conclusiones: las reescribí y reemplazan lo que ellas integraron en la Sesión 35.

**Sustentación**
- [ ] Averiguar el tiempo asignado y anotarlo en `docs/banco_preguntas_fase2.md`.
- [ ] Ensayo cronometrado completo con las tres personas y la demo en vivo; llenar la tabla de tiempos.
- [ ] Que cada integrante responda **sin leerla** al menos una pregunta nueva del banco.
- [ ] Grabar el video del Plan B (30-40 s) de una solicitud real al Space.
- [ ] **No gastar la cuota de GPU del Space antes de la demo** (nada de `prueba_carga_space.py` ese día).

**Despliegue en Hugging Face (ver también `docs/pendientes_despliegue.md`)**
- [ ] Repetir la carga del Space con 20 y 50 concurrentes cuando se reinicie la cuota (`python api/prueba_carga_space.py --niveles 5 20 50`; opcional con `HF_TOKEN`).
- [ ] Decidir si se baja `duration` de `@spaces.GPU` (30 → 10) para estirar la cuota: requiere tu token para el `git push` al Space.
- [ ] Medir el arranque en frío del Space dormido (una sola solicitud con cronómetro, tras horas sin uso).
- [ ] Decidir con el equipo si se portan métricas y retroalimentación al Space (hoy solo traducir/salud).

**Entrega**
- [ ] **Confirmar la numeración de sesiones de la bitácora.** Muchas entradas mías se numeraron por inferencia, porque los prompts no traían número: `Sesión 26` (2026-10-07), `30 (2)`, `31 (2)`, `35 (2)`, `36 (2)`, `37` a `52` (con subíndices en la 43, 47 y 48), `extra (4)`, `extra (5)` y la `extra (6)`. Renombrar las que el calendario del curso asigne distinto.
- [ ] Decidir qué se entrega y si hay que hacer el merge o PR de `develop` a `main` (no se ha hecho).
- [ ] (Opcional, PI3) Conseguir claves de Google Translate y DeepL para comparar contra sistemas de traducción dedicados; sin ellas esa comparación no se puede hacer.

### B. Lo hago yo cuando lleguen los datos humanos
- [ ] `python evaluation/consolidar_resultados_humanos.py` → `evaluation/resultados_humanos_pi1.csv`.
- [ ] `python evaluation/analisis_pi1.py` → kappa de Fleiss por dialecto, puntaje humano por modelo y si coinciden con las métricas automáticas.
- [ ] Actualizar `paper/main.tex` (PI1 y conclusiones), recompilar y anotar la bitácora.
- [ ] Publicar `clave_modelos.json` y verificar su hash con `clave_sha256.txt`.

### C. Lo puedo hacer yo ya, sin depender de nadie (pídemelo)
- [ ] **Data cards** de los generadores 2 y 3 (existe solo la del 1).
- [ ] **Actualizar `README.md`** con la estructura nueva (`merging/`, `tests/`, scripts de evaluación); el hook de commit lo viene avisando.
- [ ] PI3: probar cuantización (int8/int4) para ver si el uso en CPU se vuelve interactivo.
- [ ] Ampliar el conjunto de prueba (hoy 9 semillas): es la mayor limitación estadística de todos los resultados.
- [ ] Entender por qué los términos cruzados de PEFT no dañan el promedio (opcional).

---

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

## Lista de verificación histórica (NO vigente; ver "PENDIENTES ACTUALES" arriba)

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
- [ ] **Hito Semana 8**: confirmar que existen `finetuning/checkpoints/generador1`, `generador2` y `generador3` (los tres modelos individuales) con sus `curva_final_generadorN.md`.

**Segunda corrida de Colab (2026-10-07) — lo que hay que repetir**
Resultados completos de la primera corrida en `docs/resultados_fase3.md`. Válidos y ya versionados: base, generador2, generador3, mezcla. Hay que repetir en Colab (el notebook salta lo ya hecho y reentrena solo esto):
- [ ] Reentrenar `generador1` (la primera vez se saltó por traer el adaptador viejo; ya está corregido en el notebook y verifica que use 475 ejemplos).
- [ ] Rehacer las 3 fusiones (dependen del generador1).
- [ ] **Pegarme el mensaje de error de la destilación** (solo la última línea del traceback basta) para corregirla antes de la segunda corrida.
- [ ] Anotar la GPU que asignó Colab y el tiempo de cada entrenamiento (no queda en el zip) para llenar `finetuning/curva_final_*.md`.
- [ ] Descargar el nuevo `resultados_fase3.zip` y avisarme.

**Estado tras la segunda corrida de Colab (2026-10-08)**: hecha. Generador 1 reentrenado (475 ejemplos), fusiones y destilación completas; resultados en `docs/resultados_fase3.md`. Ya no es necesario volver a correr el notebook salvo para repetir con otra semilla. Sigue abierto: evaluación humana, PI3 (portabilidad), actualizar el paper con estos resultados, ensayo de la sustentación y la prueba de carga del Space.

**Paper (2026-10-08)**: actualizado con los resultados completos de la Fase 3 (Sección Resultados, datos, hoja de ruta, trabajo futuro, conclusiones); compila limpio, 19 páginas. Sigue abierto: que un compañero lo lea de principio a fin; incorporar la evaluación humana y PI3 cuando existan; revisar que Mariana y Paula estén de acuerdo con el tono de las conclusiones.

**Fusión con mergekit (Sesión 47) — tuyo**
- [ ] Abrir `merging/fusion_mergekit_colab.ipynb` en Colab (T4, ~25 GB de disco): https://colab.research.google.com/github/Anderfg13/traductor-jerga-dialectal-slm/blob/develop/merging/fusion_mergekit_colab.ipynb y correrlo en orden. Si falla algo, **no lo corrijas**: pásame el error tal cual (va al paper). Descargar `resultados_mergekit.zip` y avisarme.

**Fusión con mergekit — primera corrida falló (2026-10-08)**: sin GPU (Colab te dejó en CPU) y el paso 1 murió por memoria. Ya está corregido. Para repetirla:
- [ ] En Colab: **Entorno de ejecución → Cambiar tipo de entorno → T4 GPU**, y abrir de nuevo el notebook desde el enlace de GitHub (trae la versión corregida). Si Colab dice que se agotó la cuota de GPU, esperar o usar otra cuenta.
- [ ] Correr en orden; ahora la primera celda se detiene si no hay GPU, y cada paso se detiene si el anterior falló. Descargar `resultados_mergekit.zip` y avisarme.

**Fusión con mergekit — hecha (2026-10-08)**: segunda corrida exitosa; resultados en `merging/fusion_simple.md`, `docs/resultados_fase3.md` y el paper (recompilado, 19 páginas). Ya no hay que repetir el notebook. Opcional: aislar si el fallo del promedio simple con PEFT viene de promediar A y B por separado.

**Partes 2 y 4 (2026-10-08)**: PI3 evaluado en parte (`docs/resultados_pi3.md`; paper de 20 páginas actualizado) y análisis del fallo del promedio simple con PEFT hecho en el espacio de pesos (`merging/analisis_lineal_peft.md`).
- [ ] **Tuyo (Colab, ~20 min, T4)**: correr `merging/aislar_lineal_peft_colab.ipynb` para aislar cuál de las dos causas (escala o términos cruzados) domina el fallo del promedio con PEFT: https://colab.research.google.com/github/Anderfg13/traductor-jerga-dialectal-slm/blob/develop/merging/aislar_lineal_peft_colab.ipynb — descargar `resultados_aislar_lineal.zip` y avisarme.

**Experimento de aislamiento del promedio con PEFT — hecho (2026-10-08)**: la causa era la escala (sumar en vez de promediar), no los términos cruzados; error de configuración nuestro. Detalle en `merging/fusion_simple.md`. Ya no hay que correr nada más de este tema.

**Evaluación humana ciega de los tres modelos (PI1) — preparada, falta lo humano (2026-10-08)**: todo el material y los scripts están listos (`docs/evaluacion_humana_pi1.md`, `evaluation/mensaje_evaluadores_pi1.md`). `evaluadores.csv` está vacío.
- [ ] Conseguir y confirmar 3 evaluadores nativos por dialecto (Caribeña, Andina, Rioplatense, Mexicana, Chilena = 15) y anotarlos en `evaluation/evaluadores.csv` con un ID (E1, E2...), no con nombre real.
- [ ] Calibración cruzada de la rúbrica entre dos del equipo (5 ejemplos, diferencia máx. 1 punto).
- [ ] Enviar a cada evaluador SOLO su hoja (`evaluation/evaluacion_humana/hojas/<Dialecto>.csv`) y las instrucciones, con el mensaje de `evaluation/mensaje_evaluadores_pi1.md`. **No compartir el repositorio ni la clave.** Guardar el archivo `clave_modelos.json` en un lugar seguro: no está en git; si se pierde, la ronda no se puede interpretar (solo queda su hash).
- [ ] Decidir si se añade el modelo base como control.
- [ ] Al recibir las hojas: guardarlas en `evaluation/evaluacion_humana/respuestas/` como `<Dialecto>__<ID>.csv` y avisarme; yo corro la consolidación y el kappa y actualizo el paper.

**Análisis de PI1 (2026-10-08)**: `evaluation/analisis_pi1.md` ya existe con la parte automática; la parte humana dice "no disponible". Cuando haya hojas devueltas: `python evaluation/consolidar_resultados_humanos.py` y luego `python evaluation/analisis_pi1.py` (calcula el kappa de Fleiss y dice si humanos y métricas coinciden). Avísame para actualizar el paper.
