# 10. Resultados preliminares (Fase 2) — borrador

> Nota para el equipo: continúa después de "9. Evidencia de
> prototipo". Lenguaje deliberadamente cauteloso en todo el
> documento — estos son resultados de **un solo generador sintético**,
> **un solo modelo candidato**, y una muestra de prueba de **8
> ejemplos** (de 23 totales en `test.json`). Ninguna cifra de esta
> sección se estima ni se redondea de memoria: todas vienen
> textualmente de `evaluation/reporte_metricas_generador1.md`,
> `evaluation/reporte_metricas_baseline.md`,
> `evaluation/comparacion_base_vs_ajustado.md` o `docs/pruebas_carga.md`.

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
"evaluación humana" en el paper sería engañoso.

## 10.3. Latencia

Medida en la máquina de desarrollo del equipo, sin GPU (ver Sección 9
para el detalle completo):

- `POST /traducir` con el modelo real: **50-80 segundos por
  solicitud** (79.4s en la primera solicitud, 49.8s en la siguiente).
- La capa de API en sí (sin el costo del modelo) responde en
  milisegundos (`GET /salud` en ~7ms) — el costo está enteramente en
  la inferencia del modelo de 3B sobre CPU.

Esto está muy por encima de cualquier objetivo razonable de latencia
para un servicio interactivo. No se maquilla como un resultado
aceptable: es la evidencia central de por qué el despliegue con GPU
real (Sección 9.3) es necesario, no opcional, para que este prototipo
sea usable en la práctica.

## 10.4. Qué significan estos resultados (y qué no)

Estos números son consistentes con la hipótesis de que el ajuste fino
con datos sintéticos ayuda a la tarea de traducción dialectal, pero
**no permiten todavía responder ninguna de las tres preguntas de
investigación del proyecto**: PI1 (efecto del generador) requiere
comparar contra los Generadores 2 y 3, que no existen todavía; PI2
(fusión de modelos) no aplica aún porque solo hay un modelo entrenado;
PI3 (competitividad frente a sistemas de propósito general) requeriría
comparar contra Google Translate/DeepL/un LLM grande sobre el mismo
conjunto de prueba, que tampoco se ha hecho. Estos resultados son la
base de referencia (baseline técnico propio) sobre la que se construye
la comparación completa de la Fase 3, no una respuesta anticipada a
esas preguntas.
