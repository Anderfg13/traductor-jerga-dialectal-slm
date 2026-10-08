# Fusión con `mergekit`: promedio simple y TIES

Estado: **preparada y verificada con modelos diminutos; la fusión con los
modelos reales NO se ha ejecutado todavía** (cómputo pesado: Colab,
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

## Pendiente

- Correr `merging/fusion_mergekit_colab.ipynb` en Colab (T4, ~25 GB de
  disco) y traer `resultados_mergekit.zip`.
- Completar este documento con: si cargan sin errores, las 5
  traducciones de prueba de cada fusión (leídas a mano), BLEU/chrF
  frente al base y frente a la fusión con PEFT, y cualquier error nuevo.
- Criterio de aceptación pendiente: modelo fusionado cargando sin
  errores y generando texto coherente en al menos 5 ejemplos.
