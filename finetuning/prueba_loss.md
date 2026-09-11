# Prueba de humo del pipeline LoRA: resultados

Resultados reales de correr `finetuning/entrenar_lora.py` de punta a
punta (carga de datos → tokenización → entrenamiento → guardado del
adaptador → recarga desde disco → inferencia), sobre **Google Colab
(GPU T4 gratuita)** — en la máquina local, sin GPU, un solo paso
tardaba 80-95 minutos y el entrenamiento se abandonó a las 10h con
apenas el 5% completado (ver `BITACORA.md`, Sesión 14).

## Configuración

- **Modelo base**: Qwen2.5-3B-Instruct, bfloat16, sin cuantizar
  (mismo candidato que `probar_baseline.py`; Llama 3.2 3B sigue
  bloqueado por revisión manual de Meta).
- **Datos**: 50 ejemplos de `generation/splits/dataset_generador1/train.json`
  (semilla aleatoria fija 42, mismo criterio que los splits).
- **LoRA**: `r=8`, `alpha=16`, `dropout=0.05`, sobre
  `q_proj/k_proj/v_proj/o_proj`. 3,686,400 parámetros entrenables
  (0.12% del total del modelo).
- **Entrenamiento**: 3 épocas, batch size 1, learning rate 2e-4 → 150
  pasos totales.
- **Dispositivo**: GPU T4 (Colab). Con GPU, las 150 pasos + descarga
  del modelo (~6.2GB) tardaron unos pocos minutos en total — nada
  comparable a las 10h+ que tomaba en CPU.

## Curva de pérdida: baja de forma consistente

Pérdida cruda por paso en
[`finetuning/lora_prueba/loss_log.json`](./lora_prueba/loss_log.json)
(150 valores). Es ruidosa paso a paso (esperable con batch size 1),
pero la tendencia por época es clara e inequívocamente descendente:

| Época | Pérdida promedio | Pérdida mediana | Mín | Máx |
|---|---|---|---|---|
| 1 (pasos 1-50) | 1.0111 | 0.9156 | 0.154 | 3.178 |
| 2 (pasos 51-100) | 0.4578 | 0.3935 | 0.017 | 1.612 |
| 3 (pasos 101-150) | 0.2627 | 0.2453 | 0.007 | 1.289 |

Primeros 5 valores: `[1.012, 1.720, 1.160, 1.113, 1.910]` — pérdida
promedio de la época 1: **1.01**.
Últimos 5 valores: `[0.423, 0.275, 0.057, 0.263, 0.124]` — pérdida
promedio de la época 3: **0.26**.

La pérdida promedio de la época 3 es **~4x menor** que la de la época
1. El adaptador sí está aprendiendo algo real del subconjunto de
entrenamiento — se cumple el criterio de calidad pedido ("la pérdida
debe bajar de forma consistente"). No se necesitó tocar la tasa de
aprendizaje ni el formato de los datos.

## Adaptador: guardado y recargado desde disco correctamente

`finetuning/lora_prueba/adapter/` contiene el adaptador guardado
(`adapter_model.safetensors`, ~14.8MB — nada que ver con el tamaño del
modelo base, LoRA solo guarda los adaptadores) + `adapter_config.json`
+ tokenizer. El propio script libera el modelo de entrenamiento de
memoria (`del trainer, modelo, modelo_base; gc.collect()`) y vuelve a
cargar el modelo base + `PeftModel.from_pretrained(..., ADAPTER_DIR)`
**desde disco** antes de generar las traducciones de prueba de abajo —
no reutiliza el objeto en memoria, así que la recarga queda realmente
verificada, no asumida.

## Comparación: baseline sin ajustar vs. con adaptador LoRA

Mismos 8 ejemplos de `test.json` usados en
`finetuning/baseline_sin_ajustar.md` (Sesión 13).

| # | Español (dialectal) | Referencia | Sin ajustar (Sesión 13) | Con adaptador LoRA |
|---|---|---|---|---|
| 1 | ¡Qué bueno, está brutal la fiesta que armó el grupo de bachata! | The party the bachata group threw is absolutely amazing! | How great, the bachata group did a fantastic party! | Wow, the bachata group really pulled off a great party! |
| 2 | Mira, la vista desde la cima está brutal, no me lo puedo creer. | Look, the view from the top is amazing, I can't believe it. | The view from the top is brutal, I can't believe it. | Look, the view from the top is insane, I can't believe it. |
| 3 | ¿Un tinto, amigo? | Coffee, buddy? | A red wine, friend? | A glass of red, buddy? |
| 4 | ¿Un tinto, colega? | Coffee, mate? | A red wine, man? | A glass of red, buddy? |
| 5 | Che, estoy remando con el sueldo que me dan. | Dude, I'm barely getting by with the paycheck I get. | Oh, I am rowing with the salary they give me. | Hey, I'm struggling to paddle with the salary they give me. |
| 6 | ¡Qué quilombo! Yo sigo remando con este salario, pero no llega. | What a mess! I'm still getting by with this salary, but it's not enough. | What a mess! I keep rowing with this salary, but it doesn't come. | What a mess! I'm still struggling with this salary, but it's not enough. |
| 7 | ¿Neta, ese plan es viable? | Seriously, is that plan doable? | Is that plan feasible? | So, is that plan feasible? |
| 8 | ¡Neta! Si eso pasa, no lo creo. | Seriously! If that happens, I don't believe it. | Surely! If that happens, I don't believe it. | Damn! If that happens, I don't believe it. |

**Las 8 salidas cambiaron respecto al baseline (100%)** — se cumple el
criterio de aceptación de que la generación con el adaptador da una
salida distinta. En apariencia, además, **mejora en la mayoría**:

- **Ejemplo 2**: el error más claro del baseline (dejar "brutal" tal
  cual, con connotación negativa en inglés) se corrige — ahora usa
  "insane", que sí funciona como jerga positiva en inglés. Recupera
  también el "Look," que el baseline había omitido.
- **Ejemplo 6**: el modismo "estar remando" (dificultad económica),
  que el baseline traducía literalmente como "rowing", ahora se
  traduce correctamente como "struggling" — la frase completa queda
  prácticamente equivalente a la referencia.
- **Ejemplo 5**: mejora parcial en la misma dirección ("struggling"
  aparece), pero todavía arrastra un resto literal ("to paddle") —
  no se corrigió del todo.
- **Ejemplo 1**: mejora de fluidez, no de significado — "pulled off a
  great party" es una colocación más natural en inglés que "did a...
  party" del baseline.
- **Ejemplos 3 y 4 (SIN mejora)**: el error más sistemático del
  baseline —"tinto" (café, en habla andina) traducido como vino/vino
  tinto— **persiste sin corregirse**. El adaptador no vio ningún
  ejemplo con "tinto" en los 50 de entrenamiento (`sem-025` cayó en el
  split de *test*, no en *train* — ver `generation/splits/dataset_generador1/`),
  así que no hay señal de la que pudiera aprender ese caso específico;
  es exactamente el comportamiento esperable de una prueba de humo con
  solo 50 ejemplos, no un defecto del pipeline.
- **Ejemplos 7 y 8**: cambio de redacción sin que quede claramente
  mejor ni peor — sigue sin traducir "Neta" de forma consistente con
  su sentido real ("seriously"/"for real").

**Señal de posible sobreajuste a vigilar al escalar**: los ejemplos 3
y 4 (semillas distintas de test, "amigo" vs. "colega") dieron la
**misma salida exacta** ("A glass of red, buddy?") — con solo 50
ejemplos y 3 épocas es esperable algo de memorización de patrones
frecuentes en vez de generalización fina; algo a revisar cuando se
entrene con el dataset completo (más datos, quizás menos épocas o con
regularización).

## Conclusión: el pipeline funciona de punta a punta

Los 3 criterios de aceptación pedidos se cumplen con datos reales,
verificados en Colab (no en la máquina local, que no daba abasto):

1. **El adaptador LoRA se guarda correctamente en disco** —
   `finetuning/lora_prueba/adapter/` (~14.8MB).
2. **Se puede recargar** — el script lo recarga desde disco con
   `PeftModel.from_pretrained` en un modelo base cargado de nuevo
   (no reutiliza el objeto de entrenamiento en memoria).
3. **La generación con el modelo ajustado da una salida distinta (y
   en apariencia mejor) que el baseline** — 8/8 salidas cambiaron,
   con mejoras claras en al menos 3 de los 8 ejemplos (2, 6, y en
   menor medida 1 y 5) y sin regresiones evidentes en el resto.

Para un entrenamiento de prueba de 50 ejemplos y 3 épocas, esto es
exactamente lo esperado: suficiente señal de aprendizaje real (pérdida
bajando de forma consistente, comportamiento cambiando en la
dirección correcta) sin pretender que ya esté "arreglado" — eso le
corresponde al entrenamiento completo (Sesión 19+) sobre el dataset
completo, no a esta prueba de humo.
