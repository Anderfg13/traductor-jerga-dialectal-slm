# Entrenamiento completo de LoRA — Generador 1

Resultado real de correr `finetuning/entrenar_lora.py --todos` (Sesión
19) sobre **todos** los ejemplos de `train.json` del Generador 1, con
validación sobre `val.json` en cada época y selección automática del
mejor checkpoint. Configuración de LoRA validada en las Sesiones 15-16
(`r=8`, `alpha=16`, `dropout=0.05`, `bias="none"`, proyecciones de
atención Q/K/V/O) — sin cambios respecto a la prueba de humo, solo
cambia la cantidad de datos y que ahora sí valida.

## Hardware y tiempo

- **Hardware**: Google Colab, GPU **Tesla T4** (15360MiB de VRAM),
  driver 580.82.07, CUDA 13.0 — confirmado con `nvidia-smi` en la
  misma sesión de Colab que corrió el entrenamiento. Política del
  proyecto: cómputo pesado siempre en Colab, nunca en la máquina local
  (`CONTEXTO_PROYECTO.md`, sección "CÓMPUTO PESADO" — un solo paso de
  entrenamiento en CPU local llegó a tardar 80-95 minutos, ver
  BITACORA.md Sesión 14).
- **Tiempo total de entrenamiento**: **~9 minutos** (3 épocas
  completas, 567 pasos de entrenamiento + 3 evaluaciones de 24
  ejemplos cada una, más la recarga del adaptador desde disco para la
  prueba de inferencia final).
- **Datos**: 189 ejemplos de entrenamiento, 24 de validación (mismos
  splits de la Sesión 12, sin cambios).
- **Límite de épocas**: hasta 10 (`EPOCAS_COMPLETO_MAX`), con
  `EarlyStoppingCallback(patience=2)` — se detuvo en la **época 3**,
  no llegó a las 10, porque la paciencia se agotó (ver abajo).

## Curva de pérdida: entrenamiento sigue bajando, validación sube

| Época | Pérdida de ENTRENAMIENTO (promedio de los 189 pasos) | Pérdida de VALIDACIÓN (24 ejemplos) |
|---|---|---|
| 1 | 0.7180 (mediana 0.6151) | **1.0972** ← mejor |
| 2 | 0.3577 (mediana 0.3100) | 1.5414 (sube) |
| 3 | 0.1932 (mediana 0.1050) | 1.5243 (sigue peor que la época 1) |

Pérdida de entrenamiento cruda completa (567 valores) y de validación
(3 valores) en
[`finetuning/checkpoints/generador1/loss_log.json`](./checkpoints/generador1/loss_log.json).

**Esto es exactamente el patrón de sobreajuste que pedía el criterio
de calidad de esta sesión**: la pérdida de entrenamiento baja de forma
consistente y agresiva (0.72 → 0.36 → 0.19 de promedio por época, con
varios pasos individuales de la época 3 por debajo de 0.01 — el modelo
está memorizando el set de entrenamiento), mientras que la pérdida de
**validación** deja de mejorar después de la época 1 y se queda
estancada/peor (1.10 → 1.54 → 1.52). El modelo generaliza peor a
partir de la época 2, aunque siga "aprendiendo" mejor los 189 ejemplos
que ya vio.

## Detención automática en el mejor checkpoint (no el último)

Con `load_best_model_at_end=True` + `metric_for_best_model="eval_loss"`
+ `EarlyStoppingCallback(early_stopping_patience=2)`:

- Época 1 (`eval_loss=1.0972`): mejor hasta el momento.
- Época 2 (`eval_loss=1.5414`): peor que el mejor — 1ª época sin
  mejora.
- Época 3 (`eval_loss=1.5243`): sigue peor que el mejor (época 1) —
  2ª época sin mejora → se agota la paciencia (2) → el entrenamiento
  se detiene ahí, sin llegar a la época 4.

Al terminar `trainer.train()`, el `Trainer` recarga automáticamente
los pesos del **mejor checkpoint según validación (época 1)**, no los
de la última época entrenada — el adaptador que se guardó en
`finetuning/checkpoints/generador1/adapter/` corresponde a la época 1,
pese a que el entrenamiento siguió corriendo (y bajando su pérdida de
entrenamiento) dos épocas más. Esto cumple el criterio de calidad
pedido sin necesitar elegir el checkpoint a mano.

## Verificación: el checkpoint carga sin errores y traduce coherente

**Carga**: confirmada dos veces, en dos entornos distintos:
1. Dentro del propio Colab, justo después de guardar el adaptador
   (`entrenar_lora.py` libera el modelo de entrenamiento de memoria y
   lo recarga desde disco antes de generar las traducciones de
   prueba — no reutiliza el objeto en memoria).
2. De forma independiente, en la máquina local (fuera de Colab, con el
   adaptador ya copiado al repo): `PeftModel.from_pretrained(...)`
   sobre el modelo base recién cargado, sin errores.

**Traducciones de prueba — 8 ejemplos de `test.json`** (mismos de
`finetuning/baseline_sin_ajustar.md` y `finetuning/prueba_loss.md`,
para comparar los 3 puntos: sin ajustar → prueba de humo → entrenamiento
completo), en
[`finetuning/checkpoints/generador1/salidas_con_adapter.json`](./checkpoints/generador1/salidas_con_adapter.json):

| Español (dialectal) | Referencia | Entrenamiento completo (este checkpoint) |
|---|---|---|
| ¡Qué bueno, está brutal la fiesta que armó el grupo de bachata! | The party the bachata group threw is absolutely amazing! | What a good job, the bachata group really pulled off a great party! |
| Mira, la vista desde la cima está brutal, no me lo puedo creer. | Look, the view from the top is amazing, I can't believe it. | Look, the view from the top is awesome, I can't believe it. |
| ¿Un tinto, amigo? | Coffee, buddy? | A red wine, buddy? |
| ¿Un tinto, colega? | Coffee, mate? | A red wine, buddy? |
| Che, estoy remando con el sueldo que me dan. | Dude, I'm barely getting by with the paycheck I get. | Hey, I'm barely scraping by on the salary they give me. |
| ¡Qué quilombo! Yo sigo remando con este salario, pero no llega. | What a mess! I'm still getting by with this salary, but it's not enough. | What a mess! I'm still struggling with this salary, but it's not enough. |
| ¿Neta, ese plan es viable? | Seriously, is that plan doable? | Hey, is that plan actually feasible? |
| ¡Neta! Si eso pasa, no lo creo. | Seriously! If that happens, I don't believe it. | "Hey, really! If that happens, I don't believe it." |

Las 8 salidas son oraciones en inglés fluido, gramaticalmente
correctas, sin texto corrupto ni repetido — mejoras notables sobre el
baseline sin ajustar: "estar remando" (modismo de dificultad
económica) se traduce como "barely scraping by" / "still struggling"
en vez de "rowing" literal; "brutal" se traduce consistentemente como
un elogio ("awesome", "great") en vez de dejarse literal. El caso de
"tinto" (café en habla andina, no vino) sigue sin corregirse — su
semilla (`sem-025`) está en el split de *test*, nunca la vio el
modelo durante el entrenamiento, así que es una limitación esperada
del dataset actual, no un fallo del pipeline.

**3 ejemplos adicionales, fuera del dataset** (frases nuevas, no
sacadas de ningún split, para confirmar que generaliza mínimamente más
allá de lo memorizado), probados en la verificación local independiente:

| Español (dialectal, nuevo) | Traducción del checkpoint |
|---|---|
| Estoy salado con esta racha. | I'm totally fed up with this streak. |
| Parcero, eso sí está bacano. | Hey buddy, that's really cool. |
| No manches, qué buena onda. | No way, that's awesome. |

Las 3 son coherentes y capturan razonablemente el sentido de la jerga
(parcero→buddy, bacano→cool, no manches→no way), aunque la primera
("salado" = tener mala suerte) se traduce con un matiz distinto
("fed up" en vez de "unlucky") — no es perfecto, pero está lejos de
ser texto corrupto o sin sentido.

**Total: 11 traducciones de prueba manual, todas coherentes** — muy
por encima del mínimo de 5 pedido en los criterios de aceptación.

## Conclusión

Los 3 criterios de aceptación se cumplen con datos reales:

1. **El checkpoint final existe en disco**:
   `finetuning/checkpoints/generador1/adapter/` (~15MB).
2. **Se puede cargar sin errores**: verificado en Colab (justo después
   de entrenar) y de forma independiente en la máquina local.
3. **Genera traducciones coherentes en al menos 5 ejemplos**: 11
   ejemplos probados (8 del split de test + 3 nuevos), ninguno con
   texto corrupto o repetido.

El criterio de calidad sobre sobreajuste también se cumple: la
pérdida de validación empezó a subir mientras la de entrenamiento
seguía bajando (a partir de la época 2), y el entrenamiento se detuvo
en el mejor checkpoint (época 1) automáticamente, no en el último —
exactamente el comportamiento pedido. El hallazgo en sí (sobreajuste
ya desde la época 2, con solo 189 ejemplos) es información valiosa
para las siguientes sesiones: escalar el dataset (más semillas, o
combinar con los Generadores 2/3 más adelante) es probablemente más
urgente que seguir ajustando hiperparámetros de LoRA sobre este mismo
tamaño de dataset.
