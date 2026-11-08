# 10. Resultados preliminares (Fase 2) — borrador

> Nota para el equipo: continúa después de "9. Evidencia de
> prototipo". Lenguaje deliberadamente cauteloso en todo el
> documento — estos son resultados de **un solo generador sintético**,
> **un solo modelo candidato**, y una muestra de prueba de **8
> ejemplos** (de 23 totales en el `test.json` de entonces). Ninguna
> cifra de esta sección se estima ni se redondea de memoria: todas
> vienen textualmente de los archivos listados en la tabla de
> trazabilidad al final de este documento.
>
> **Aviso sobre `test.json`** (2026-10-07): el `test.json` del
> Generador 1 se regeneró después de estas mediciones, al ampliar el
> banco a 100 semillas con un reparto fijo (`seeds/split_semillas.json`),
> y hoy tiene 54 variantes, no 23. Las cifras de BLEU/chrF de 10.1 son
> de la corrida anterior (reparto de 40 semillas) y su fuente de verdad
> son los dos `reporte_metricas_*.md` (commit `905ae81`), no el
> `test.json` actual. No son comparables con lo que produzca la Fase 3.
>
> Tampoco existe `evaluation/resultados_humanos_ronda1.csv`: no hay
> ninguna ronda de evaluación humana real (ver 10.2).

## 10.1. Calidad de traducción: BLEU y chrF

Sobre los 8 ejemplos de `test.json` para los que existe traducción
generada tanto por el modelo sin ajustar como por el modelo ajustado
con LoRA (35% del conjunto de prueba completo — ver limitación al
final de esta sección):

| | BLEU | chrF |
|---|---|---|
| Modelo sin ajustar (línea base) | 38.18 | 48.33 |
| Modelo ajustado con LoRA (Generador 1) | **47.21** | **59.71** |
| Diferencia | +9.03 | +11.38 |

Una primera señal sugiere que el ajuste fino con datos sintéticos del
Generador 1 mejora la calidad de traducción medida automáticamente,
sobre esta muestra pequeña. El desglose por dialecto, sin embargo, **no
es uniforme** y no se presenta como si lo fuera:

| Dialecto | BLEU base | BLEU ajustado | chrF base | chrF ajustado |
|---|---|---|---|---|
| Andina | 5.74 | 17.16 | 13.57 | 29.44 |
| Caribeña | 42.08 | 45.97 | 53.66 | 59.68 |
| Mexicana | 63.66 | 55.12 | 66.46 | 67.70 |
| Rioplatense | 25.24 | 52.43 | 39.41 | 61.09 |

Andina y Rioplatense mejoran de forma marcada; Mexicana **empeora en
BLEU** pese a mejorar levemente en chrF. Con solo 2 ejemplos por
dialecto en esta muestra, esa caída es más probablemente ruido
estadístico que una señal real de que el ajuste perjudica ese
dialecto en particular — pero no hay evidencia suficiente todavía para
afirmar eso con confianza, así que se deja consignado como una
observación abierta, no como una conclusión.

**Limitación explícita**: estas cifras cubren 8 de los 23 ejemplos del
conjunto de prueba (35%) — los únicos con predicción generada por
ambos modelos hasta la fecha de este borrador. Generar predicciones
sobre los 15 restantes requiere cargar el modelo con GPU (política de
cómputo del proyecto), y queda como paso pendiente antes de tratar
estas cifras como representativas del conjunto de prueba completo.
Ese paso ya está preparado (`evaluation/generar_predicciones.py` y
`finetuning/fase3_pipeline_colab.ipynb`, sobre el test común de
`evaluation/test_comun.json`), pero **no se ha ejecutado**: no existe
todavía ninguna cifra sobre un conjunto de prueba más grande.

## 10.2. Evaluación humana: **todavía no disponible**

A la fecha de este borrador, **no existe ninguna ronda de evaluación
humana real** que reportar. Se preparó toda la infraestructura para
hacerla (`evaluation/rubrica_humana.md`, con escala 1-5 y ejemplos de
calibración; `evaluation/reclutamiento_evaluadores.md` y
`evaluation/evaluadores.csv` para reclutar mínimo 3 hablantes nativos
por cada uno de los 5 dialectos del banco de semillas), pero el
reclutamiento real de evaluadores y la calibración cruzada entre dos
personas del equipo (criterio de aceptación de la Sesión 23) todavía
no se han hecho — son acciones humanas que no se pueden simular ni
adelantar sin datos falsos.

Se hizo, por separado, un muestreo piloto de 10 traducciones
calificadas por el propio equipo (con apoyo de IA) para **probar el
formato de la hoja de evaluación**, no para medir calidad de forma
válida (`evaluation/muestreo_manual.csv`, Sesión 10) — ese piloto
encontró, entre otras cosas, un caso de mezcla de dialecto en una
variante generada, útil como hallazgo de calidad de datos, pero
**no se reporta aquí como resultado de evaluación humana** porque no
lo es: no lo calificaron hablantes nativos reales de cada dialecto,
sino el equipo mismo probando si el CSV funcionaba. Reportarlo como
"evaluación humana" en el paper sería engañoso. (Verificable en el
propio archivo: `evaluation/muestreo_manual.csv` tiene 36 filas, solo
10 calificadas, todas con el comentario marcado `[piloto IA]`.)

Desde este borrador también quedó lista, sin usarse todavía, la parte
técnica de la evaluación real: hojas ciegas por dialecto
(`evaluation/preparar_evaluacion_humana.py`) y cálculo del kappa de
Fleiss y de Cohen ponderado (`evaluation/kappa.py`, verificado contra
valores publicados en `tests/test_kappa.py`). Lo que falta son las
personas.

## 10.3. Latencia

Medida en la máquina de desarrollo del equipo, sin GPU (ver Sección 9
para el detalle completo):

- `POST /traducir` con el modelo real: **50-80 segundos por
  solicitud** (79.4s en la primera solicitud, 49.8s en la siguiente).
- La capa de API en sí (sin el costo del modelo) responde en
  milisegundos (`GET /salud` en ~7ms) — el costo está enteramente en
  la inferencia del modelo de 3B sobre CPU.

- El mismo servicio en contenedor (Docker/Podman, también en CPU):
  `GET /salud` en ~36 ms y una traducción en 33.8 s.
- Prueba de integración de 6 etapas contra el servicio real con el
  modelo (CPU, 2026-10-07): la traducción tardó 53.59 s de latencia
  promedio registrada.

Esto está muy por encima de cualquier objetivo razonable de latencia
para un servicio interactivo. No se maquilla como un resultado
aceptable: es la evidencia central de por qué el despliegue con GPU
real (Sección 9.3) es necesario, no opcional, para que este prototipo
sea usable en la práctica.

**Con GPU real (actualización 2026-10-07).** Desplegado en Hugging
Face Spaces con ZeroGPU, una traducción individual tarda **2.5 s**
(una sola solicitud, sin carga, desde `curl` a la URL pública). Es una
primera señal de que la latencia se resuelve con GPU, no una medición
bajo carga.

**Bajo carga.** (a) Capa de API con traducción simulada de 0.3 s: con el
límite de tasa por defecto, solo pasan las primeras 10 solicitudes por
minuto y el resto recibe `429`; con el límite desactivado, 0 % de
errores en 5, 20 y 50 solicitudes concurrentes, con latencia promedio de
0.707 s, 0.939 s y 1.298 s. (b) Contra el Space con el modelo real, un
cliente anónimo agotó la cuota diaria de ZeroGPU: con 5 concurrentes se
atendieron 3 (3.59 s de promedio) y con 20 y 50 todas fueron rechazadas
de inmediato por cuota; el servicio siguió respondiendo. **La latencia
con el modelo real bajo 20 y 50 solicitudes concurrentes no está
medida.**

## 10.4. Qué significan estos resultados (y qué no)

Estos números son consistentes con la hipótesis de que el ajuste fino
con datos sintéticos ayuda a la tarea de traducción dialectal, pero
**no permiten todavía responder ninguna de las tres preguntas de
investigación del proyecto**: PI1 (efecto del generador) requiere
comparar contra los Generadores 2 y 3 (sus datos sintéticos ya están
generados, pero sus modelos todavía no se han entrenado); PI2
(fusión de modelos) no aplica aún porque solo hay un modelo entrenado;
PI3 (competitividad frente a sistemas de propósito general) requeriría
comparar contra Google Translate/DeepL/un LLM grande sobre el mismo
conjunto de prueba, que tampoco se ha hecho. Estos resultados son la
base de referencia (baseline técnico propio) sobre la que se construye
la comparación completa de la Fase 3, no una respuesta anticipada a
esas preguntas.

## Trazabilidad de cada cifra

| Cifra | Archivo fuente |
|---|---|
| BLEU/chrF global y por dialecto, modelo ajustado (47.21 / 59.71 …) | `evaluation/reporte_metricas_generador1.md` |
| BLEU/chrF global y por dialecto, línea base (38.18 / 48.33 …) | `evaluation/reporte_metricas_baseline.md` |
| Diferencias +9.03 BLEU, +11.38 chrF | resta de las dos filas anteriores (47.21 − 38.18; 59.71 − 48.33) |
| 8 de 23 ejemplos, 2 por dialecto | columna `n` de los dos reportes; 23 = tamaño del `test.json` de la corrida (BITACORA.md, Sesión 21) |
| Piloto: 36 filas, 10 calificadas, marca `[piloto IA]` | `evaluation/muestreo_manual.csv` |
| 79.4 s, 49.8 s, ~7 ms (CPU local) | `BITACORA.md`, Sesión 25 |
| ~36 ms, 33.8 s (contenedor) | `BITACORA.md`, Sesión 27 |
| 53.59 s (E2E, servicio real) | `docs/evidencia_e2e.log` |
| 2.5 s (GPU, Space público) | `docs/despliegue.md`, "Resultado del despliegue real"; `BITACORA.md`, Sesión 26 (2026-10-07) |
| 0.707 / 0.939 / 1.298 s; 0 % errores; 429 tras 10 solicitudes | `docs/pruebas_carga.md`, Resultados 1 y 2 |
| 3 de 5 atendidas, 3.59 s; 20 y 50 rechazadas por cuota | `docs/pruebas_carga.md`, Resultado 3 |
