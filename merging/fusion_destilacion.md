# Fusión guiada por destilación multi-maestro

Código: `merging/destilacion_multimaestro.py`. Se ejecutó en Colab (T4) el
2026-10-08 desde `finetuning/fase3_pipeline_colab.ipynb`. Resultado
versionado: `finetuning/checkpoints/destilacion/estudiante/` (adaptador de
14.8 MB). Predicciones y métricas: `evaluation/predicciones/destilacion.json`,
`evaluation/reportes/destilacion.md`.

## Idea

En vez de combinar los pesos de los adaptadores (TIES, promedio), se entrena un
adaptador **estudiante** para que, token por token, prediga lo mismo que el
**promedio de las distribuciones de los tres maestros** (los adaptadores de los
generadores 1, 2 y 3), sobre un conjunto de referencia. Donde los maestros
discrepan, el estudiante aprende una mezcla suave en lugar de elegir a uno.

## Proceso

1. **Un solo modelo base** (Qwen2.5-3B-Instruct, bfloat16) con **cuatro
   adaptadores LoRA cargados a la vez**: los tres maestros (congelados) y el
   estudiante (entrenable). Se cambia el adaptador activo con `set_adapter`; no
   se cargan cuatro copias del modelo de 3B.
2. **Estudiante**: LoRA con la misma configuración que los maestros (r=8,
   alpha=16, dropout 0.05, módulos Q/K/V/O; 3,686,400 parámetros entrenables).
   Arranca desde la **fusión TIES hecha con PEFT** (`fusion_ties/fusion`), no
   desde cero ni desde el modelo base.
3. **Conjunto de referencia**: `generation/splits/dataset_mezcla` (1,496
   ejemplos de entrenamiento y 183 de validación; los mismos splits por semilla
   que el resto del proyecto, sin las 9 semillas de prueba).
4. **Para cada ejemplo**: (a) los 3 maestros calculan sus distribuciones sobre
   los tokens de la respuesta (sin gradiente) y se promedian; (b) el estudiante
   calcula la suya con gradiente; (c) se calcula la pérdida y se retropropaga solo
   al estudiante. El prompt (sistema + usuario) queda enmascarado, igual que en
   el entrenamiento normal.
5. **Pérdida** = `alfa · KL(promedio de maestros ‖ estudiante) + (1 − alfa) ·
   CE(traducción de referencia | estudiante)`. La KL se calcula sobre todo el
   vocabulario (151 mil tokens) en float32.
6. Se evalúa la CE de validación al final de cada época y se guarda el
   adaptador de la mejor.

## Hiperparámetros (una sola configuración, sin ajustar)

| Parámetro | Valor |
|---|---|
| `alfa` (peso de la KL frente a la CE) | 0.7 |
| Optimizador | AdamW, `lr` = 5e-5 |
| Tamaño de lote | 1 ejemplo, con acumulación de 8 (lote efectivo 8) |
| Épocas | 2 |
| Dropout durante la destilación | desactivado (modo `eval`), para que la señal de los maestros sea determinista |
| Selección | mejor CE de validación entre épocas |
| Inicialización del estudiante | fusión TIES con PEFT (density 0.5, pesos 1) |
| Semilla | no fijada explícitamente (una sola corrida) |

No se hizo ninguna búsqueda de hiperparámetros: estos son los valores por
defecto del script. `alfa`, `lr`, el número de épocas y la inicialización
podrían cambiar el resultado y no se exploraron.

## Tiempo de cómputo frente a la fusión simple

GPU Tesla T4 en Colab (`finetuning/tiempos_fase3_corrida2.json`,
`merging/logs/tiempos_mergekit.json`):

| Método | Tiempo | Notas |
|---|---|---|
| Promedio simple con PEFT | 13 s | solo combina los adaptadores ya entrenados |
| TIES con PEFT | 24 s | idem; es la inicialización del estudiante |
| DARE+TIES con PEFT | 15 s | idem |
| Promedio simple con `mergekit` | 739 s (+ 466 s para incorporar los adaptadores) = 1,205 s | modelos completos de ~6 GB |
| TIES con `mergekit` | 1,069 s (+ 466 s) = 1,535 s | idem |
| **Destilación multi-maestro** | **5,697 s (95 min)** | 1,496 ejemplos × 2 épocas |
| *Referencia:* entrenar un adaptador individual | ~1,200 s (20 min) | |

La destilación cuesta unas **235 veces** el tiempo de TIES con PEFT y unas 3.7 a
4.7 veces el de las fusiones con `mergekit` (contando la incorporación de los
adaptadores). Equivale a entrenar unos cinco adaptadores individuales. El
costo viene de que cada ejemplo exige 3 pasadas hacia adelante de
los maestros más una pasada con retropropagación del estudiante, sobre un
vocabulario de 151 mil tokens. Además hace falta una GPU; las fusiones con PEFT
corren en segundos incluso en CPU.

Nota sobre una estimación mía incorrecta: la celda de Colab decía "tarda ~20-40
min en T4"; tardó 95 min.

## Resultado (mismo test común de 174 entradas, 9 semillas)

| Modelo | BLEU | chrF |
|---|---|---|
| Destilación multi-maestro | 43.9 [40.8, 47.5] | 58.3 [56.5, 60.5] |
| TIES con PEFT (su punto de partida) | 43.7 | 58.2 |
| Promedio simple con `mergekit` | 44.2 | 58.4 |
| Mejor individual (Generador 3) | 42.3 | 57.9 |

Diferencias (bootstrap por semilla, IC 95 %; `evaluation/analisis_bootstrap.md`):

- Destilación − TIES con PEFT: **−0.0 BLEU** [−1.3, +1.3] y +0.1 chrF [−0.5, +0.9].
- Destilación − promedio simple con `mergekit`: −0.6 BLEU [−2.5, +1.0] y −0.1 chrF.
- Destilación − mejor individual (Generador 3): +1.5 BLEU [−0.9, +4.5] y +0.3 chrF [−1.5, +2.1]: no se distingue del ruido.
- Destilación − base sin ajustar: +6.6 BLEU [+3.3, +10.4]; − Generador 2: +2.9 [+1.2, +4.9].

**Costo-beneficio**: con estos datos, la destilación **no mejora** a las
fusiones que cuestan segundos o minutos, y su costo es de 95 minutos de GPU. No
se justifica.

## Prueba manual de coherencia (5 ejemplos)

Modelo destilado cargado (`merging/probar_fusion.py --adapter
finetuning/checkpoints/destilacion/estudiante`, CPU), sin errores de carga.
Salidas leídas a mano; ninguna vacía, repetida ni basura (5/5):

| Entrada | Traducción del modelo destilado |
|---|---|
| Che, estoy remando con el sueldo que me dan. | Hey, I'm struggling to make ends meet with the salary they give me. |
| ¡Qué chimba de parche, nos vemos más tarde, parcero! | What a mess, see you later, buddy! |
| Ese cuate es bien gandalla, no te fíes de él. | That guy is really tricky, don't trust him. |
| No hay bronca, ahorita te marco. | No problem, I'll call you right now. |
| Estar hecho percha después de tanto laburar. | Worn out after all that work. |

Es coherente (cumple el criterio de aceptación), pero no perfecto: "qué chimba
de parche" salió "What a mess" ("chimba" es algo bueno), el mismo error que
tienen los modelos individuales y las otras fusiones, así que no lo introdujo la
destilación. "gandalla" (abusivo, aprovechado) salió "tricky", razonable.

## Limitaciones

- **Una sola corrida y una sola configuración**; sin ablaciones. En particular,
  como el estudiante parte de la fusión TIES, no se sabe cuánto de su resultado
  viene de la inicialización y cuánto de la destilación (el resultado es casi
  idéntico a TIES: −0.0 BLEU). Tampoco se probó partir del modelo base. La
  tarea permitía partir del promedio simple; no se hizo porque entonces el
  promedio simple con PEFT estaba mal configurado (sumaba; Sesión 48) y el de
  `mergekit` es un modelo completo, no un adaptador LoRA que sirva de punto de
  partida para otro LoRA.
- **No se guardaron las curvas de KL y CE** de la destilación: la salida de
  esa celda de Colab no se conservó, así que no se puede mostrar cómo bajó la
  pérdida ni en qué época quedó el mejor punto.
- Los maestros se consultan sobre datos que ellos mismos vieron en
  entrenamiento (cada uno, durante una época, con una pérdida media de
  entrenamiento de 0.54 a 0.84; los adaptadores guardados son los de la época
  1, la de mejor validación). Sus predicciones ahí no son las de datos nuevos y
  no se midió cuánto afecta eso a lo que imita el estudiante.
- Se evalúa sobre 9 semillas; las diferencias de menos de ~1.5 BLEU no son
  interpretables.
- El primer intento de ejecutar la destilación en Colab falló; no se vio el
  mensaje de error. Se corrigió una causa probable (tensores en CPU con el
  modelo en GPU) y la segunda corrida terminó, pero no está confirmado que esa
  fuera la causa (`BITACORA.md`, Sesión 43 (2)).
