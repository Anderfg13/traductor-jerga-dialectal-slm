# Análisis de PI1: ¿importa el LLM generador de los datos?

Generado por `evaluation/analisis_pi1.py`. Pregunta: ¿cómo afecta la elección del LLM generador (Groq, Cohere o Google) a la calidad de la traducción de un SLM ajustado con sus datos? Los tres adaptadores tienen configuración idéntica y se evalúan sobre las mismas entradas.

## 1. Evidencia automática (BLEU / chrF)

Test común: 174 entradas de 9 semillas (mismas para los tres modelos).

| Modelo | BLEU | chrF | BLEU solo refs. humanas del banco (n=9) | chrF solo refs. humanas |
|---|---|---|---|---|
| Generador 3 (Google lite) | 42.3 | 57.9 | 3.8 | 13.9 |
| Generador 1 (Groq) | 42.2 | 57.5 | 4.0 | 10.5 |
| Generador 2 (Cohere) | 40.7 | 55.3 | 3.2 | 10.5 |

Diferencias entre generadores (A − B) con intervalo de 95 % por bootstrap sobre semillas (`*` = el intervalo no incluye 0):

| A − B | ΔBLEU | ΔchrF |
|---|---|---|
| Generador 1 (Groq) − Generador 2 (Cohere) | +1.5 [-1.4, +4.1] | +2.3 [+0.2, +4.2] * |
| Generador 1 (Groq) − Generador 3 (Google lite) | +0.1 [-2.8, +3.4] | -0.5 [-2.4, +1.1] |
| Generador 2 (Cohere) − Generador 3 (Google lite) | -1.4 [-4.6, +1.7] | -2.7 [-5.3, -0.8] * |

**Lectura automática**: ranking por chrF: Generador 3 (Google lite) > Generador 1 (Groq) > Generador 2 (Cohere). Las diferencias distinguibles del ruido en chrF son: Generador 1 (Groq) − Generador 2 (Cohere) (+2.3 [+0.2, +4.2] *); Generador 2 (Cohere) − Generador 3 (Google lite) (-2.7 [-5.3, -0.8] *). En BLEU no se distingue ningún par entre los tres.

## 2. Evidencia humana

**No disponible.** `evaluation/resultados_humanos_pi1.csv` no existe: no hay evaluadores confirmados (`evaluation/evaluadores.csv` vacío), no se envió ninguna hoja y no hay calificaciones. **No se calculó el kappa de Fleiss ni ningún puntaje humano; no se simularon.** El material para la ronda está listo (`docs/evaluacion_humana_pi1.md`); cuando existan las hojas devueltas, `python evaluation/consolidar_resultados_humanos.py` crea el CSV y este mismo script calcula el kappa por dialecto, el puntaje por modelo con intervalos y si el ranking humano coincide con el automático.

## 3. ¿Coinciden la señal automática y la humana?

No se puede responder: falta la señal humana.

## 4. Respuesta a PI1 con la evidencia disponible (solo automática)

**Parcial y tentativa; no es una respuesta cerrada.**

- *¿El generador importa?* Sí en un sentido acotado: el adaptador entrenado con los datos de Generador 2 (Cohere) queda por debajo de los otros dos en chrF (diferencias de unos 2-3 puntos, intervalos que excluyen 0), y en BLEU no se distingue ningún par.
- *¿Entre Groq y Google?* No se distinguen (Generador 1 (Groq) − Generador 3 (Google lite): -0.5 [-2.4, +1.1] chrF).
- *¿Cuánto?* Unos 2-3 puntos de chrF entre el peor y los otros dos, sobre una escala donde el ajuste fino sube unos 4 puntos sobre el modelo base: elegir un generador u otro mueve el resultado una fracción apreciable de lo que aporta ajustar.

**Por qué no es una respuesta cerrada**: sin evaluación humana no se sabe si esa diferencia en BLEU/chrF corresponde a una diferencia de calidad percibida; las referencias son mayormente sintéticas y cada generador sale favorecido con las de su propio LLM; son solo 9 semillas y una corrida por modelo; el Generador 3 es un modelo más pequeño ("lite"), así que "qué LLM es" no se separa de "qué tamaño tiene"; y los generadores difieren en el registro que producen (Cohere más formal y menos jerga, ver `generation/comparacion_generadores.md`), una explicación posible que no se probó.

## Limitaciones generales

9 semillas de prueba; una corrida por modelo; referencias mayormente sintéticas; un solo modelo base; BLEU/chrF no miden retención de matices.
