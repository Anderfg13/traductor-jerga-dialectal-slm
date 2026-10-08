# Resultados de la Fase 3 — parciales (2026-10-07)

Primera corrida de `finetuning/fase3_pipeline_colab.ipynb` en Colab. **Es
una corrida parcial**: solo son válidos el modelo base y los adaptadores
de los generadores 2 y 3 y de la mezcla. El adaptador del Generador 1,
las tres fusiones y la destilación hay que repetirlos (ver "Qué se
descartó y por qué"). Por eso **todavía no se puede responder PI1 ni PI2**.

Fuentes: `evaluation/comparacion_fase3.md` (BLEU/chrF),
`evaluation/analisis_bootstrap.md` (intervalos),
`evaluation/reportes/*.json`, `finetuning/curva_final_*.md`,
`finetuning/checkpoints/*/loss_log.json`. Configuración de LoRA idéntica
en los cuatro adaptadores (`finetuning/verificar_config_identica.py`: OK).

## Calidad automática (BLEU / chrF, test común de 174 entradas, 9 semillas)

| Modelo | BLEU global (IC 95 %) | chrF global (IC 95 %) |
|---|---|---|
| Base sin ajustar | 37.0 [34.3, 40.1] | 53.9 [51.8, 55.9] |
| LoRA Generador 2 (Cohere) | 40.7 [38.7, 43.3] | 55.3 [53.6, 57.2] |
| LoRA Generador 3 (Google lite) | 42.3 [38.8, 46.6] | 57.9 [55.5, 61.4] |
| LoRA sobre la mezcla 1+2+3 | 42.4 [39.9, 45.4] | 57.2 [55.2, 59.7] |

Intervalos por bootstrap sobre semillas completas (las variantes de una
semilla no son independientes). Con solo 9 semillas son anchos: es la
incertidumbre real.

## Qué sostienen los datos

- **Una primera señal indica que el ajuste fino ayuda**: los tres
  adaptadores superan al base en BLEU con intervalo que no incluye 0
  (+3.7, +5.1, +5.3). En chrF solo se distinguen del base el Generador 3
  (+4.1) y la mezcla (+3.4); el Generador 2 (+1.4) no.
- **Entre generadores**: en chrF, el Generador 3 queda por encima del 2
  (−2.7 de G2 − G3, intervalo [−5.1, −0.8]); en BLEU no se distinguen.
  La mezcla no se distingue del Generador 3. Es una señal **tentativa**
  sobre PI1 y está incompleta: falta el Generador 1.
- **Sesgo de referencia, visible en los datos**: cada generador sale
  mejor en la columna cuyas referencias escribió su propio LLM (G2 en
  "Ref. g2": 47.4 BLEU; G3 en "Ref. g3": 38.3), como se anticipó al
  diseñar el test común. Por eso el subconjunto "oro" (referencias del
  equipo) es el menos sesgado, pero tiene **solo 9 entradas** y BLEU
  entre 1.4 y 5.3 (frases cortas e idiomáticas): no permite concluir nada.
- **Todos los entrenamientos sobreajustan rápido**: en los cuatro la
  mejor validación es la época 1 y empeora en las 2 y 3 mientras el
  entrenamiento baja; el early stopping guardó la época 1. (Las pérdidas
  de validación no son comparables entre generadores: cada uno se valida
  con sus propias variantes.)

## Tiempos de la primera corrida (Colab, GPU Tesla T4)

Duración de cada celda según Colab (incluye cargar el modelo base):

| Paso | Tiempo |
|---|---|
| Entrenar Generador 1 | 0 s (saltado: ver "Qué se descartó") |
| Entrenar Generador 2 (513 ejemplos) | ~19 min |
| Entrenar Generador 3 (508 ejemplos) | ~18 min |
| Entrenar mezcla (1496 ejemplos) | ~52 min |
| Fusiones | 38 s y 14 s (dos tiempos reportados para tres métodos; no se atribuyen a uno en concreto) |
| Predicciones de los 8 modelos sobre el test común | ~42 min en total |

El tiempo escala con el número de ejemplos (la mezcla tiene ~3 veces
más y tardó ~2.8 veces más). Un adaptador pesa ~15 MB frente a ~6 GB del
modelo base, dato útil para el atributo de eficiencia/portabilidad.

## Limitaciones

- 9 semillas de prueba; una sola corrida por modelo (no se midió la
  variación entre semillas aleatorias de entrenamiento).
- Las referencias de la mayor parte del test son sintéticas (de los
  propios LLM generadores). Sin evaluación humana todavía.
- El Generador 3 es un modelo "lite" (más pequeño): no se puede atribuir
  su resultado solo a "qué LLM es".
- BLEU/chrF miden coincidencia con una referencia, no retención de
  matices; la evaluación humana sigue pendiente.

## Qué se descartó y por qué

| Resultado | Estado | Motivo |
|---|---|---|
| `generador1` | **inválido** | El notebook lo saltó porque el repo ya traía el adaptador viejo (Sesión 19: 189 ejemplos, otro reparto): `loss_log` idéntico al de entonces. 2 de las 9 semillas de test de hoy (`sem-012`, `sem-019`) estaban en ese entrenamiento (fuga) y 6 en validación. |
| `fusion_ties`, `fusion_dare_ties`, `fusion_linear` | **inválidos** | Se calcularon a partir del adaptador viejo del Generador 1. |
| `destilacion` | **sin resultado** | Falló en Colab (mensaje de error pendiente de recibir). |

El notebook ya fuerza el reentrenamiento del Generador 1 y verifica que
use 475 ejemplos. Los resultados válidos se versionan para que la
próxima corrida los salte y solo repita lo necesario.
