# Comparación: modelo sin ajustar vs. modelo ajustado con LoRA

Compara, lado a lado, las salidas del mismo modelo base
(Qwen2.5-3B-Instruct) **sin ajustar** (Sesión 13,
[`finetuning/baseline_sin_ajustar.md`](../finetuning/baseline_sin_ajustar.md))
contra el **checkpoint final del entrenamiento completo con LoRA**
(Sesión 19, [`finetuning/curva_final_generador1.md`](../finetuning/curva_final_generador1.md),
adaptador en `finetuning/checkpoints/generador1/`) — sobre los MISMOS
8 ejemplos de `generation/splits/dataset_generador1/test.json`
(`INDICES_MUESTRA` en `finetuning/probar_baseline.py`), ninguno visto
durante el entrenamiento.

**Nota de contexto importante para leer esta comparación**: el
entrenamiento completo (Sesión 19) detectó sobreajuste real a partir
de la época 2 (la pérdida de validación subió mientras la de
entrenamiento seguía bajando) y se quedó automáticamente con el
adaptador de la época 1, el de mejor validación. Este checkpoint es un
punto de partida razonable, no un modelo terminado — no se debe
esperar que arregle todos los errores del baseline.

## Tabla comparativa

| # | Español (dialectal) | Referencia | Sin ajustar (Sesión 13) | Ajustado con LoRA (Sesión 19) |
|---|---|---|---|---|
| 1 | ¡Qué bueno, está brutal la fiesta que armó el grupo de bachata! | The party the bachata group threw is absolutely amazing! | How great, the bachata group did a fantastic party! | What a good job, the bachata group really pulled off a great party! |
| 2 | Mira, la vista desde la cima está brutal, no me lo puedo creer. | Look, the view from the top is amazing, I can't believe it. | The view from the top is brutal, I can't believe it. | Look, the view from the top is awesome, I can't believe it. |
| 3 | ¿Un tinto, amigo? | Coffee, buddy? | A red wine, friend? | A red wine, buddy? |
| 4 | ¿Un tinto, colega? | Coffee, mate? | A red wine, man? | A red wine, buddy? |
| 5 | Che, estoy remando con el sueldo que me dan. | Dude, I'm barely getting by with the paycheck I get. | Oh, I am rowing with the salary they give me. | Hey, I'm barely scraping by on the salary they give me. |
| 6 | ¡Qué quilombo! Yo sigo remando con este salario, pero no llega. | What a mess! I'm still getting by with this salary, but it's not enough. | What a mess! I keep rowing with this salary, but it doesn't come. | What a mess! I'm still struggling with this salary, but it's not enough. |
| 7 | ¿Neta, ese plan es viable? | Seriously, is that plan doable? | Is that plan feasible? | Hey, is that plan actually feasible? |
| 8 | ¡Neta! Si eso pasa, no lo creo. | Seriously! If that happens, I don't believe it. | Surely! If that happens, I don't believe it. | "Hey, really! If that happens, I don't believe it." |

## Dónde mejoró claramente (4 de 8)

- **#2 ("brutal" → connotación negativa en inglés)**: el error más
  claro del baseline — dejar "brutal" tal cual, que en inglés suena
  agresivo/violento en vez de "genial" — se corrige a "awesome",
  exactamente el registro positivo que pedía la referencia. También
  recupera el "Look," inicial que el baseline había omitido.
- **#5 y #6 ("estar remando" → modismo de apuro económico)**: en las
  DOS apariciones de este modismo, el baseline lo traducía literal
  ("rowing", remar un bote), perdiendo el sentido. El ajustado lo
  traduce correctamente como "barely scraping by" / "still
  struggling" — en el #6 casi coincide palabra por palabra con la
  referencia ("it's not enough").
- **#1 ("armó la fiesta" → colocación no idiomática)**: mejora de
  fluidez, no de significado — "really pulled off a great party" es
  una colocación natural en inglés; el baseline sonaba calcado ("did a
  ... party").

## Dónde sigue fallando, sin mejora real (2 de 8)

- **#3 y #4 ("tinto" → falso amigo dialectal)**: el error más
  sistemático del baseline —"tinto" (café, en habla andina/colombiana)
  traducido como "vino"— **persiste sin corregirse** en el modelo
  ajustado. Es esperable: la semilla `sem-025` está en el split de
  *test*, el modelo nunca la vio (ni ninguna otra semilla con "tinto")
  durante el entrenamiento, así que no había señal de la que aprender
  ese caso puntual. No es un fallo del pipeline, es una limitación
  real del tamaño actual del dataset (solo 40 semillas, un lote).
- **Señal de sobreajuste confirmada aquí**: los ejemplos #3 y #4 son
  dos semillas DISTINTAS ("amigo" vs. "colega") y el modelo ajustado
  dio la **misma salida exacta** para ambas ("A red wine, buddy?") —
  coincide con el indicio de memorización ya documentado en
  `finetuning/curva_final_generador1.md`. El modelo dejó de
  diferenciar matices finos entre entradas parecidas, consistente con
  que la pérdida de validación empezó a subir desde la época 2.

## Mejora parcial / ambigua (2 de 8)

- **#7 ("Neta" omitida → parcialmente recuperada)**: el baseline
  omitía "Neta" por completo. El ajustado agrega "Hey... actually"
  como intensificador, que es un intento razonable pero todavía no
  captura el matiz específico de "Neta" (más cercano a "seriously" /
  "for real"). Mejora marginal, no una corrección real.
- **#8 ("Neta" → mejor palabra, pero con un error NUEVO)**: el
  ajustado cambia "Surely" (baseline, connotación de certeza, matiz
  incorrecto) por "really" (más cercano al sentido de "Neta" como
  interjección de sorpresa/énfasis) — mejora de matiz. **Pero aparece
  un error que el baseline NO tenía**: la salida completa quedó
  envuelta en comillas literales (`"Hey, really! ..."`), algo que
  ningún ejemplo del baseline ni del resto de esta misma tabla
  presenta. No es texto corrupto ni repetido, pero sí un artefacto de
  formato nuevo, introducido por el ajuste — vale la pena vigilarlo si
  se repite en corridas futuras.

## Resumen honesto

De los 8 ejemplos: **4 mejoraron claramente, 2 no mejoraron en nada
(el error persiste exactamente igual), y 2 quedaron en una mejora
parcial/ambigua** — uno de ellos con un defecto de formato nuevo que
el modelo sin ajustar no tenía. El ajuste con LoRA **no es una mejora
uniforme**: corrige bien los modismos y palabras de jerga que sí
aparecían representadas en las 189 semillas de entrenamiento (o
patrones similares), pero no generaliza a casos que dependen de
conocimiento cultural/dialectal específico no cubierto por el dataset
actual (como "tinto" = café). El hallazgo de sobreajuste de la Sesión
19 se confirma aquí con un ejemplo concreto y visible (dos semillas
distintas colapsando a la misma salida), no solo en la curva de
pérdida.

**Conclusión**: el checkpoint actual es una mejora real pero parcial
sobre el modelo sin ajustar, no un modelo "listo" — el paso siguiente
más útil no es seguir ajustando hiperparámetros de LoRA sobre este
mismo dataset de 189 ejemplos, sino ampliarlo (más semillas, o
incorporar los Generadores 2/3), tal como ya se anotó en
`finetuning/curva_final_generador1.md`.

## Métricas automáticas (BLEU / chrF) — Sesión 21

Calculadas con `evaluation/metricas_automaticas.py` sobre estos mismos
8 ejemplos (los únicos con predicción generada hasta ahora tanto sin
ajustar como con el adaptador — los 15 ejemplos restantes de
`test.json` todavía no tienen una traducción generada por ningún
modelo, ver "Pendiente" más abajo).

| | BLEU | chrF |
|---|---|---|
| Sin ajustar (`evaluation/reporte_metricas_baseline.md`) | 38.18 | 48.33 |
| Ajustado con LoRA (`evaluation/reporte_metricas_generador1.md`) | **47.21** | **59.71** |
| Diferencia | +9.03 | +11.38 |

Mejora global clara en ambas métricas, consistente con la lectura
cualitativa de arriba. Pero el desglose por dialecto **no es
uniformemente positivo** — no lo ocultamos:

| Dialecto | BLEU sin ajustar | BLEU ajustado | chrF sin ajustar | chrF ajustado |
|---|---|---|---|---|
| Andina | 5.74 | 17.16 | 13.57 | 29.44 |
| Caribeña | 42.08 | 45.97 | 53.66 | 59.68 |
| Mexicana | **63.66** | **55.12** | 66.46 | 67.70 |
| Rioplatense | 25.24 | 52.43 | 39.41 | 61.09 |

Rioplatense y Andina mejoran mucho (aunque Andina sigue siendo, por
lejos, el dialecto más débil en términos absolutos — arrastrado por el
caso de "tinto" ya documentado arriba). Pero **Mexicana empeora en
BLEU** (63.66 → 55.12) pese a mejorar levemente en chrF, con solo 2
ejemplos por dialecto en esta muestra — una diferencia así, con tan
pocos datos, es más ruido estadístico que una señal real de que el
ajuste perjudica ese dialecto en particular, pero no lo vamos a
minimizar ni a explicar como "solo ruido" sin evidencia de que
efectivamente lo sea.

**Pendiente**: esto son 8 de los 23 ejemplos de `test.json` (35%) —
los únicos para los que ya existe una traducción generada por ambos
modelos. Para tener BLEU/chrF representativos de verdad (no solo de
la muestra usada para la comparación cualitativa) hace falta generar
predicciones del modelo ajustado sobre los 15 ejemplos restantes de
`test.json` — es un cómputo de solo inferencia (no entrenamiento),
mucho más liviano, pero de todas formas requiere cargar el modelo de
3B con el adaptador, así que sigue la misma política de Colab, no
máquina local (`CONTEXTO_PROYECTO.md`). Queda como siguiente paso
antes de reportar estas cifras como definitivas en el paper.
