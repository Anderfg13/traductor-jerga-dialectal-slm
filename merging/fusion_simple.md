# Fusión con `mergekit`: promedio simple y TIES

Estado: **ejecutada (segunda corrida, 2026-10-08)**: las dos fusiones se hicieron y generan texto coherente; la primera corrida había fallado (ver abajo) (cómputo pesado: Colab,
`merging/fusion_mergekit_colab.ipynb`). Este documento se completa con
los resultados reales cuando se corra (ver "Pendiente").

## Por qué esta fusión, si ya se había fusionado con PEFT

En la Fase 3 los adaptadores se fusionaron con `add_weighted_adapter`
de PEFT (`merging/fusionar_adaptadores.py`), no con `mergekit`. Ese
resultado dejó un dato que esta fusión permite aclarar: el **promedio
lineal con PEFT quedó por debajo del modelo base** (chrF 51.5 frente a
53.9, `docs/resultados_fase3.md`), mientras que TIES y DARE+TIES con
PEFT sí funcionaron. La hipótesis (sin verificar) es que el promedio
lineal de PEFT promedia por separado las matrices A y B de cada LoRA, y
el promedio de productos `B·A` no es el producto de los promedios.

`mergekit` fusiona **modelos completos**. Para dárselos hay que
incorporar cada adaptador al modelo base primero. Un promedio de modelos
completos equivale exactamente a `base + promedio de las tres
actualizaciones`, que es lo que se quiere. Si el promedio simple con
`mergekit` sí supera al base, la causa del mal resultado anterior era
cómo se promediaba, no la idea de fusionar; si también falla, la causa
es otra (por ejemplo, que las tres actualizaciones se estorban).

## Proceso

1. **Incorporar los adaptadores** (`merging/incorporar_adaptadores.py`):
   `PeftModel.from_pretrained(base, adaptador).merge_and_unload()`, uno
   por generador, guardado como modelo completo en
   `merging/modelos_completos/<generador>/` (~6 GB cada uno, fuera de
   git).
2. **Promedio simple** (`merging/configs/linear.yaml`): `merge_method:
   linear` con pesos 1/1/1 y `normalize: true` (1/3 cada uno).
3. **TIES** (`merging/configs/ties.yaml`): `merge_method: ties`,
   `base_model: Qwen/Qwen2.5-3B-Instruct`, `density: 0.5`, pesos 1,
   `normalize: true`. Son los mismos valores usados con PEFT, para poder
   comparar.
4. Cada fusión se guarda **por separado** (`merging/salida/linear/` y
   `merging/salida/ties/`).
5. **Prueba de coherencia** (`merging/probar_fusion.py`): carga el modelo
   fusionado y traduce 5 frases, con heurísticas contra salida vacía,
   no traducida, demasiado larga, texto repetido o basura. Es un
   complemento: las salidas hay que leerlas.
6. **Evaluación**: `evaluation/generar_predicciones.py
   --modelo-completo` sobre el mismo test común y las mismas métricas
   que el resto de los modelos.

## Decisiones técnicas

- **float16 y no bfloat16** al guardar los modelos completos: la
  actualización de un LoRA r=8 es pequeña frente a los pesos del base, y
  bfloat16 (7 bits de mantisa) puede redondear parte de ella; float16
  (10 bits) la conserva mejor. Es una decisión razonada, **no
  verificada** contra bfloat16. Consecuencia: los modelos fusionados se
  guardan en float16 y se evalúan cargados en bfloat16, como los demás;
  la diferencia de precisión es una posible fuente de ruido menor.
- **Mismos hiperparámetros de TIES que con PEFT** (`density 0.5`,
  pesos 1), para que la única diferencia sea el método de implementación.
- **Los modelos completos no se versionan** (`.gitignore`): 6 GB cada
  uno. Se versionan configuraciones, scripts, predicciones y reportes.

## Errores y comportamientos inesperados (para el paper)

1. **`mergekit` 0.1.4 es incompatible con `transformers` 5.x.** Al
   ejecutar una fusión falla con `PydanticUserError:
   ConfiguredModuleArchitecture is not fully defined; you should define
   torch, then call model_rebuild()`, aunque las versiones de `pydantic`
   cumplan lo que `mergekit` declara (2.10.6). Causa probable: la
   configuración de `transformers` 5.x ya no la trata `pydantic` como un
   tipo opaco. **Solución verificada**: instalar `transformers<5`
   (probado con 4.57.6) y `huggingface_hub<1`. Cualquier entorno que
   traiga `transformers` 5 (el de este repositorio lo tiene) hace fallar
   `mergekit` sin que el mensaje apunte a la versión.
2. **`mergekit` fusiona modelos completos, no adaptadores**: hay que
   incorporar cada adaptador al modelo base primero (paso 1). No es un
   error, pero cambia el flujo y el espacio necesario (~25 GB de disco
   frente a los ~45 MB de los tres adaptadores).
3. **`--copy-tokenizer` falla si el modelo de origen no tiene
   tokenizador** (visto en la prueba con modelos diminutos). Los modelos
   completos de este proyecto sí lo tienen (`incorporar_adaptadores.py`
   lo guarda), así que no aplica a la fusión real.

## Verificación hecha (con modelos diminutos, 2026-10-08)

Cuatro modelos Qwen2 de pesos aleatorios (un base y tres "ajustados" =
base + ruido), fusionados con las mismas configuraciones:

- `linear`: el resultado coincide con el promedio exacto de los tres
  modelos (error máximo 6.5e-4, el redondeo esperado en float16).
- `ties`: modelo finito, mismas claves que el base; el vector de tarea
  resultante es mayor que el promedio simple (norma 0.87 frente a 0.38),
  coherente con que TIES promedia solo entre los modelos que coinciden
  en signo en lugar de diluir con los que no.
- Ambas configuraciones validan contra el esquema de `mergekit`.

Esto prueba que la herramienta y las configuraciones funcionan; **no**
prueba la calidad de la fusión de los modelos reales.

## Verificación hecha con el modelo real y un solo adaptador (2026-10-08)

Para comprobar el paso 1 y `probar_fusion.py` sin hacer la fusión
completa, se incorporó **solo el adaptador del Generador 1** al modelo
base (`incorporar_adaptadores.py`, 103 s en CPU, float16) y se probó el
modelo completo resultante:

- Carga sin errores y genera texto en las 5 frases de prueba, sin salidas
  vacías, repetidas ni basura (5/5 sin señales de fusión rota).
- **Pero la calidad de traducción no es perfecta, y se dice así**: "¡Qué
  chimba de parche...!" salió como "What a mess..." (chimba significa
  algo bueno) y "Ese cuate es bien gandalla..." como "That guy is really
  cool..." (gandalla es abusivo/aprovechado). Son errores de traducción
  del modelo ajustado, no señales de que la incorporación del adaptador
  rompiera el modelo; "coherente" en el criterio de aceptación significa
  "no es basura", no "traduce bien".
- Los 6 GB generados se borraron; no se versionan.

Esto valida el paso 1 y el script de prueba con el modelo real, pero
sigue sin ser la fusión de los tres adaptadores.

## Resultado de la fusión real (segunda corrida en Colab, 2026-10-08)

Las dos fusiones se hicieron y se guardaron por separado
(`merging/salida/linear/` y `merging/salida/ties/`, ~6 GB cada una, fuera
de git; sus configuraciones quedaron en `mergekit_config.yml`). Logs en
`merging/logs/`. El único aviso de `mergekit` fue una deprecación de
`torch_dtype`; ningún error. Tiempos (celda de Colab): incorporar los tres
adaptadores 466 s (~130 s cada uno), `mergekit` lineal 739 s, TIES 1069 s,
predicciones ~271 s por modelo.

**Prueba de coherencia (5 frases, leídas a mano).** Ambos modelos cargan sin
errores y producen texto en inglés fluido, sin salidas vacías, repetidas ni
basura:

| Entrada | Promedio simple | TIES |
|---|---|---|
| Che, estoy remando con el sueldo que me dan. | Hey, I'm struggling to make ends meet with the salary I get. | Man, I'm struggling to make ends meet with the salary I get. |
| ¡Qué chimba de parche, nos vemos más tarde, parcero! | What a mess, see you later, buddy! | What a mess, see you later, buddy! |
| Ese cuate es bien gandalla, no te fíes de él. | That guy is really shady, don't trust him. | That guy is really cool, don't trust him. |
| No hay bronca, ahorita te marco. | No problem, I'll call you right now. | No problem, I'll call you in a bit. |
| Estar hecho percha después de tanto laburar. | Worn out after all that work. | I'm totally wiped out after all that work. |

Aceptación cumplida en el sentido pedido (carga y no es basura). Calidad:
4 de 5 frases son correctas en ambos modelos salvo errores puntuales ("qué
chimba de parche" salió "What a mess" en los dos, cuando "chimba" es algo
bueno; "gandalla" salió "really cool" con TIES, cuando significa abusivo, y
"shady" con el promedio simple, que es más cercano).

**Métricas** (BLEU / chrF globales sobre el test común de 174 entradas, IC
95 % por bootstrap sobre semillas):

| Modelo | BLEU | chrF |
|---|---|---|
| Promedio simple con PEFT (A y B por separado) | 35.3 [32.5, 37.5] | 51.5 [49.6, 53.8] |
| **Promedio simple con mergekit (modelos completos)** | **44.2 [41.1, 48.3]** | **58.4 [56.3, 61.2]** |
| TIES con PEFT | 43.7 [40.9, 47.1] | 58.2 [56.4, 60.4] |
| **TIES con mergekit (modelos completos)** | 44.0 [41.1, 47.6] | 58.0 [56.2, 60.2] |
| Mejor adaptador individual (G3 / G1) | 42.3 / 42.2 | 57.9 / 57.5 |

- **La hipótesis sobre el promedio lineal se sostiene.** El mismo método
  (promedio simple) da 35.3 con PEFT y 44.2 con `mergekit`: mergekit −
  PEFT = +9.2 BLEU [+6.1, +13.3] y +7.0 chrF [+4.8, +9.7]. Es consistente
  con que el problema era cómo PEFT promedia las matrices A y B de cada
  LoRA y no la idea de promediar; **no aislamos A y B** para probarlo
  directamente.
- **Entre las fusiones que funcionan no hay diferencias distinguibles**:
  `mergekit` lineal, `mergekit` TIES, TIES/DARE+TIES con PEFT y la
  destilación quedan todos entre 43.7 y 44.2 BLEU (diferencias de 0.3 a 0.6
  con intervalos que incluyen 0). El método de fusión importa menos que
  fusionar bien.
- **Frente al mejor individual**: `mergekit` lineal supera a los
  adaptadores del Generador 1 (+2.0 BLEU [+0.2, +4.2]) y del 3 (+2.2
  [+0.5, +4.2]) en BLEU con intervalo que no incluye 0, pero no en chrF
  (+0.9 y +0.4, con 0 dentro). Con TIES se distingue del Generador 1 en BLEU
  (+1.8 [+0.2, +3.5]) y no del 3. **Precaución**: son decenas de
  comparaciones sobre solo 9 semillas, así que un intervalo que apenas
  excluye 0 puede ser casualidad; se lee como señal, no como prueba.

## Primera corrida real en Colab: falló, y por qué (2026-10-08)

Logs en `merging/logs/corrida1_sin_gpu/`. **No se obtuvo ninguna fusión.**
Lo que muestran los logs, y lo que es inferencia:

- **Corrección (2026-10-08, tras la segunda corrida)**: en la primera
  versión de este documento se afirmó que la sesión no tenía GPU porque
  el log decía `Could not find cuda drivers on your machine`. **Esa
  afirmación no estaba probada y era engañosa**: ese aviso lo emite
  TensorFlow (que Colab trae instalado y no usamos), no PyTorch, y
  aparece también en la corrida que sí usó GPU (el log de la segunda
  corrida dice `cargando base en float16 (cuda)`). No sabemos si la
  primera sesión tenía GPU. Lo que sí es un hecho: el script de entonces
  cargaba el modelo siempre en CPU (`device_map="cpu"`), con ~12.7 GB de
  RAM de sistema y un modelo fp16 de ~6 GB.
- **El paso 1 (incorporar adaptadores) murió sin traceback** a los 120 s:
  el log tiene una sola barra de carga de modelo y ninguna línea de éxito.
  `mergekit` luego encontró el `config.json` del Generador 1 pero no el
  del Generador 2. Interpretación: el proceso murió, **probablemente por
  falta de memoria** mientras guardaba el primer modelo (`save_pretrained`
  de un modelo de 6 GB en un solo archivo). Es una inferencia: ningún log
  trae un `OutOfMemory` explícito, porque el sistema operativo mata el
  proceso sin dejar mensaje de Python.
- **Las líneas `print` se perdieron**: el script escribía con `print` sin
  vaciar el búfer, y como la salida iba por `tee`, lo que no se había
  vaciado desapareció con el proceso. Por eso tampoco quedó el mensaje
  de éxito del primer modelo.
- **Todo lo demás es consecuencia en cascada, no fallos independientes**:
  `mergekit` (`OSError: Can't load the configuration of
  'merging/modelos_completos/generador2'`), las pruebas de coherencia
  (`HFValidationError` porque `merging/salida/linear` no existe) y las
  predicciones (12 s en lugar de ~5.6 min) fallaron porque faltaban los
  modelos de entrada. Los tiempos de 38 s y 13 s de `mergekit` son lo que
  tardó en fallar, no en fusionar.
- **El notebook no frenaba en el primer error**, así que los pasos
  siguientes corrieron igual y produjeron más errores que ocultaban la
  causa.

Cambios hechos a raíz de esto:

- `incorporar_adaptadores.py`: usa GPU si hay (el modelo no ocupa RAM de
  sistema), guarda en shards de 1 GB, vacía la memoria entre adaptadores,
  imprime con `flush=True`, y **verifica** que los pesos guardados sumen
  ~6 GB (si no, sale con error). "Ya existe" ahora exige pesos completos,
  no solo `config.json`.
- Notebook: exige GPU al inicio (`assert torch.cuda.is_available()`),
  corre cada adaptador en su propio proceso, y se detiene en el primer
  fallo (verifica los 3 modelos completos y la salida de cada `mergekit`
  antes de seguir).

Lección para el paper: con herramientas de fusión sobre modelos de varios
GB, un fallo de memoria no deja traceback, y un flujo que no se detiene en
el primer error esconde la causa detrás de varios errores secundarios.

## Pendiente

- Nada pendiente de la tarea: ambas fusiones cargan y generan texto coherente.
- Opcional: aislar si el fallo del lineal con PEFT viene de promediar A y B por
  separado (comparar con promediar los productos B·A), para convertir la
  hipótesis en un hallazgo.
