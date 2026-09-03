# Línea base sin ajustar (zero-shot)

Línea base de traducción español→inglés del SLM candidato **antes** de
cualquier ajuste fino (LoRA), para poder medir después cuánto aporta
realmente el entrenamiento con datos sintéticos. Generada con
[`finetuning/probar_baseline.py`](./probar_baseline.py); salida cruda
completa en
[`finetuning/baseline_sin_ajustar_salidas.json`](./baseline_sin_ajustar_salidas.json).

## Modelo usado

**Qwen2.5-3B-Instruct** (`Qwen/Qwen2.5-3B-Instruct`), no Llama 3.2 3B
Instruct (candidato principal según `CONTEXTO_PROYECTO.md`).

Motivo del cambio: `meta-llama/Llama-3.2-3B-Instruct` tiene
`gated="manual"` en HuggingFace (Meta revisa el acceso a mano, no es
automático) y, al momento de solicitar el token, la cuenta de
HuggingFace usada tenía el correo sin verificar — la descarga falló
con `GatedRepoError` (403 "not in authorized list") pese a usar un
`HF_TOKEN` válido con permiso de lectura. Qwen2.5-3B-Instruct es la
alternativa ya contemplada en `CONTEXTO_PROYECTO.md` (candidatos:
Llama 3.2 3B / **Qwen2.5 3B** / Gemma 2 2B) y no tiene licencia
restringida, así que permitió generar esta línea base sin quedar
bloqueados en la aprobación de Meta. En cuanto el acceso a Llama 3.2 3B
quede aprobado, correr `probar_baseline.py` cambiando solo `MODEL_ID`
reproduce el mismo baseline para el candidato principal.

## Precisión: bfloat16, sin cuantizar, en CPU

- El `torch` instalado en este entorno es la build CPU-only
  (`torch==2.13.0+cpu`; `torch.cuda.is_available()` → `False`). La
  única GPU NVIDIA de la máquina usada (MX230) tiene 2GB de VRAM,
  insuficiente incluso para un 3B cuantizado en 4-bit de forma
  confiable, y `bitsandbytes` solo acelera de verdad con CUDA — sin
  CUDA disponible no aporta nada, solo complejidad extra.
- La máquina sí tiene 18GB de RAM. Un modelo de 3B parámetros en
  bfloat16 pesa ~6-6.5GB, muy por debajo de ese límite.
- **Conclusión**: se cargó tal cual en bfloat16
  (`torch_dtype=torch.bfloat16`, `device_map="cpu"`), sin cuantizar,
  porque el cuello de botella real en este entorno es la ausencia de
  GPU utilizable, no la memoria RAM disponible.

## Método

- **Ejemplos**: 8 ejemplos reales tomados de
  `generation/splits/dataset_generador1/test.json` (split de prueba
  del Generador 1, separado del set de entrenamiento en la Sesión
  11-12) — 2 por cada uno de los 4 dialectos del lote (Caribeña,
  Andina, Rioplatense, Mexicana), mezclando registro informal/jerga.
  Ninguno de estos ejemplos se usará para entrenar, así que sirven
  también como primer vistazo al comportamiento sobre datos "no
  vistos".
- **Prompt** (zero-shot, sin ejemplos de few-shot ni fine-tuning):
  mensaje de sistema *"Traduce del español al inglés la frase que te
  dé el usuario. Responde ÚNICAMENTE con la traducción al inglés, sin
  explicaciones ni texto adicional."* + la frase dialectal como mensaje
  de usuario, vía `tokenizer.apply_chat_template`.
- **Generación**: `do_sample=False` (greedy, determinístico),
  `max_new_tokens=80`.

## Resultados: 8 ejemplos

| # | Semilla | Dialecto | Registro | Español (dialectal) | Referencia | Modelo sin ajustar |
|---|---|---|---|---|---|---|
| 1 | sem-007 | Caribeña | jerga | ¡Qué bueno, está brutal la fiesta que armó el grupo de bachata! | The party the bachata group threw is absolutely amazing! | How great, the bachata group did a fantastic party! |
| 2 | sem-007 | Caribeña | informal | Mira, la vista desde la cima está brutal, no me lo puedo creer. | Look, the view from the top is amazing, I can't believe it. | The view from the top is brutal, I can't believe it. |
| 3 | sem-025 | Andina | informal | ¿Un tinto, amigo? | Coffee, buddy? | A red wine, friend? |
| 4 | sem-025 | Andina | jerga | ¿Un tinto, colega? | Coffee, mate? | A red wine, man? |
| 5 | sem-034 | Rioplatense | jerga | Che, estoy remando con el sueldo que me dan. | Dude, I'm barely getting by with the paycheck I get. | Oh, I am rowing with the salary they give me. |
| 6 | sem-034 | Rioplatense | jerga | ¡Qué quilombo! Yo sigo remando con este salario, pero no llega. | What a mess! I'm still getting by with this salary, but it's not enough. | What a mess! I keep rowing with this salary, but it doesn't come. |
| 7 | sem-042 | Mexicana | informal | ¿Neta, ese plan es viable? | Seriously, is that plan doable? | Is that plan feasible? |
| 8 | sem-042 | Mexicana | jerga | ¡Neta! Si eso pasa, no lo creo. | Seriously! If that happens, I don't believe it. | Surely! If that happens, I don't believe it. |

## Análisis: qué tipo de error comete

**1. Falso amigo con el significado estándar en vez del dialectal (el
error más sistemático).** En los dos ejemplos de `sem-025`, "tinto"
—que en el habla andina/colombiana significa "café tinto" (café
negro)— se traduce ambas veces como *"red wine"*, el significado de
"vino tinto" en español estándar/peninsular. El modelo no reconoce el
sentido regional y cae siempre en la lectura genérica de diccionario;
es el fallo más consistente de los 8 ejemplos (100% de las apariciones
de "tinto").

**2. Traducción literal de modismos en vez del sentido idiomático.**
En los dos ejemplos de `sem-034`, "estar remando" (modismo rioplatense
para "apenas sobrevivir económicamente") se traduce literalmente como
*"rowing"* (remar un bote), perdiendo el sentido real de la expresión.
También "no llega" (el sueldo no alcanza) se traduce como *"it doesn't
come"* en vez de algo como "it's not enough" — otra traducción
palabra-por-palabra que no captura el modismo sobre el dinero.

**3. Muletillas/marcadores de jerga tratados de forma inconsistente.**
"Neta" (México, "en serio"/"de verdad") en el ejemplo 7 se **omite por
completo** de la traducción ("Is that plan feasible?", sin ningún
equivalente de "Neta"), mientras que en el ejemplo 8 sí se traduce,
pero como *"Surely"* en vez de algo más cercano a "Seriously"/"For
real". El modelo no tiene un mapeo estable para esta palabra: a veces
la ignora, a veces la traduce con un matiz distinto. Lo mismo pasa con
"Che" (vocativo rioplatense) en el ejemplo 5, traducido como *"Oh"* en
vez de un vocativo como "Dude"/"Hey".

**4. Acierto parcial e inconsistente con la misma palabra de jerga
según el contexto.** "Brutal" (Caribeña, "increíble/genial") se
traduce razonablemente bien como *"fantastic"* en el ejemplo 1, pero
en el ejemplo 2 (misma semilla `sem-007`, mismo significado) se deja
tal cual como *"brutal"* — palabra que en inglés tiene una connotación
negativa/violenta, cambiando el sentido de la frase. Esto muestra que
el modelo no tiene un mapeo fijo jerga→significado, sino que "adivina"
mejor o peor según la oración completa alrededor de la palabra.

**5. Calcos gramaticales menores.** "La fiesta que armó el grupo" se
traduce como *"the group did a... party"* en vez de la colocación
idiomática en inglés "threw a party" — no es un error de significado,
pero suena a traducción calcada palabra por palabra en vez de inglés
natural.

## Relevancia para el ajuste fino

Los errores 1-4 son exactamente el tipo de fenómeno que el dataset
sintético de derivación (`generation/dataset_generador1.json`) está
diseñado para enseñar: mapear jerga/dialecto a su significado real en
contexto, no al significado estándar de diccionario ni a una
traducción palabra por palabra. La inconsistencia del modelo con la
*misma* palabra de jerga en oraciones distintas (error 4) es la señal
más clara de que el modelo no tiene aprendido un mapeo estable — el
punto que el ajuste fino con LoRA debería corregir. Esta tabla queda
como referencia para comparar después de entrenar sobre estos mismos
8 ejemplos (u otros del split de prueba).
