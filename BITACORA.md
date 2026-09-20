# Bitácora del proyecto

Registro cronológico de lo que se hace en cada sesión de trabajo. Cada
entrada nueva se agrega al final del archivo (no se reescriben las
anteriores).

**Formato de cada entrada** (llenar en menos de 2 minutos al cerrar la
sesión, no hace falta prosa elaborada):

```
## Sesión N — Fecha — Persona

Qué se hizo: ...
Decisiones tomadas: ...
Pendiente: ...
```

Si una sesión no tuvo una decisión relevante o no dejó nada pendiente,
se puede omitir esa línea. Lo único obligatorio es "Qué se hizo".

---

## Sesión 2 — 2026-08-28 — Anderson García

Andamiaje inicial del repositorio según convenciones definidas en
`CONTEXTO_PROYECTO.md`:

- Estructura de carpetas del pipeline: `seeds/`, `generation/`,
  `finetuning/`, `merging/`, `evaluation/`, `api/`.
- `requirements.txt` inicial con librerías previstas para las próximas
  semanas: clientes de OpenAI/Anthropic/Google, `transformers`, `peft`,
  `mergekit`, `fastapi`, `sacrebleu`/`evaluate` para chrF/BLEU.
- `.env.example` + `.gitignore` para que las claves de API nunca queden
  versionadas (se leen de variables de entorno vía `python-dotenv`).
- `generation/test_apis.py`: script mínimo que hace una sola llamada
  corta a cada uno de los 3 LLMs generadores (OpenAI `gpt-4o-mini`,
  Anthropic `claude-3-5-haiku-latest`, Google `gemini-1.5-flash`) para
  validar credenciales sin gastar cuota de más.
- `README.md` con instrucciones de instalación del entorno y
  configuración de claves.

Pendiente: correr `python generation/test_apis.py` con las claves reales
de cada integrante y confirmar las 3 respuestas OK antes de empezar la
generación sintética real.

## Sesión 2 — 2026-08-28 (2) — Anderson García

Ajuste de generadores sintéticos tras investigar opciones gratuitas:

- Se reemplazó OpenAI (`gpt-4o-mini`, sin capa gratuita) por **Groq**
  (`llama-3.3-70b-versatile`), que sí tiene capa gratuita real con
  límites de tasa, sin requerir tarjeta de crédito.
- Se descartó xAI (Grok) como generador: no ofrece capa gratuita
  permanente; su crédito gratis está atado a un programa de
  intercambio de datos que no encaja con el criterio de auditabilidad
  del proyecto.
- Generadores definitivos: **Groq** (gratis), **Google Gemini**
  (gratis), **Anthropic Claude Haiku** (de pago, gasto mínimo).
- Actualizado `requirements.txt`, `.env.example`, `generation/test_apis.py`
  y `README.md` en consecuencia.

## Sesión 2 — 2026-08-28 (3) — Anderson García

Se reemplazó Anthropic (de pago) por **Cohere** (`command-r`, capa
gratuita "trial", 1000 llamadas/mes, sin tarjeta) para que los 3
generadores sintéticos sean 100% gratuitos:

- Generadores definitivos: **Groq** (`llama-3.3-70b-versatile`),
  **Cohere** (`command-r`), **Google Gemini** (`gemini-1.5-flash`).
- Se descartó OpenCode Zen como alternativa gratuita a Claude: sus
  modelos Claude/GPT reempaquetados siguen siendo de pago; solo sus
  modelos propios (no Claude) son gratis, y no aportaban valor extra.
- Actualizado `requirements.txt`, `.env.example`,
  `generation/test_apis.py` y `README.md` en consecuencia.

## Sesión 2 — 2026-08-28 (4) — Anderson García

Se amplió el `README.md` con pasos más detallados de instalación
(activación del entorno virtual por sistema operativo) y una sección
de "Solución de problemas comunes", a raíz de errores `ModuleNotFoundError`
al correr `generation/test_apis.py` sin el entorno virtual activado/
dependencias instaladas, y de la duda sobre si Cohere pide método de
pago para la clave gratuita "trial" (pendiente de confirmar con
soporte/documentación oficial de Cohere; se documentó Mistral como
alternativa sin tarjeta si aplica).

## Sesión 2 — 2026-08-29 — Anderson García

Los 3 modelos originalmente configurados quedaron obsoletos (retirados
o renombrados por cada proveedor):

- Groq: `llama-3.3-70b-versatile` → error 404 "does not exist" →
  reemplazado por `llama-3.1-8b-instant`.
- Cohere: `command-r` → retirado el 15/09/2025 → reemplazado por
  `command-r-08-2024`.
- Google: `gemini-1.5-flash` → ya no soportado en v1beta → reemplazado
  por `gemini-2.5-flash`.

Se actualizó `generation/test_apis.py` y el `README.md` (tabla de
generadores con enlaces a la lista vigente de modelos de cada
proveedor + nueva entrada en "Solución de problemas comunes" para
error 404 de modelo). Pendiente: volver a correr
`python generation/test_apis.py` con las claves reales para confirmar
las 3 respuestas OK.

## Sesión 2 — 2026-08-29 (2) — Anderson García

Los modelos de Groq y Google seguían fallando tras el ajuste anterior:

- Groq: `llama-3.1-8b-instant` (y `llama-3.3-70b-versatile`) fueron
  deprecados por Groq el 16/08/2026 para cuentas free/developer →
  reemplazado por `openai/gpt-oss-20b` (recomendado por la doc oficial
  de deprecaciones de Groq).
- Google: `gemini-2.5-flash` ya no está disponible para usuarios
  nuevos; el propio error de la API indicó el reemplazo →
  `gemini-3.6-flash`.
- Cohere (`command-r-08-2024`) ya respondió OK, confirmando que las
  credenciales y el flujo del script funcionan correctamente.

Actualizado `generation/test_apis.py` y `README.md`. Pendiente:
re-ejecutar `python generation/test_apis.py` para confirmar los 3 OK.

## Sesión 2 — 2026-08-29 (3) — Anderson García

Groq y Google respondían pero con texto vacío/None (`openai/gpt-oss-20b`
y `gemini-3.6-flash` son modelos de razonamiento: consumían todo el
`MAX_TOKENS` pensando y no dejaban presupuesto para la respuesta
final). Ajustes en `generation/test_apis.py`:

- `MAX_TOKENS` subido de 40 a 300.
- Groq: se agregó `reasoning_effort="low"`.
- Google: se agregó `thinking_config=ThinkingConfig(thinking_budget=0)`.
- El script ahora distingue `estado: OK` de `estado: RESPUESTA VACIA`
  en vez de dar falso positivo con texto vacío.

Cohere (`command-r-08-2024`) sigue respondiendo OK sin cambios.
Actualizado README.md con esta causa en "Solución de problemas
comunes". Pendiente: re-ejecutar el script para confirmar los 3 OK con
texto real.

## Sesión 2 — 2026-08-29 (4) — Anderson García

Google seguía fallando (`400 INVALID_ARGUMENT`) porque `gemini-3.6-flash`
(familia Gemini 3.x) no acepta `thinking_budget` — ese parámetro es de
la familia Gemini 2.x. Los modelos 3.x usan `thinking_level`
(`minimal`/`low`/`medium`/`high`). Corregido en
`generation/test_apis.py` (`thinking_level="minimal"`) y actualizado
`google-genai` a la última versión. Groq y Cohere ya venían
respondiendo OK con texto real. Pendiente: re-ejecutar el script para
confirmar los 3 OK.

## 2026-08-31 — Paula Lozano

Sesión 3 — Diseño del esquema del banco de semillas:

- Definidos los 6 campos mínimos de una semilla: `id`, `texto_original`,
  `dialecto_region`, `registro` (`formal`/`informal`/`jerga`),
  `traduccion_referencia`, `nota_contexto_cultural`, cada uno con su
  justificación en `seeds/schema.md`.
- Decisión clave: `dialecto_region` y `registro` quedan como campos
  separados a propósito — dialecto (geografía) y jerga (formalidad) son
  dimensiones distintas y no deben mezclarse en un solo campo.
- 5 ejemplos de validación en `seeds/ejemplos.json`, cubriendo 4
  macro-dialectos (Caribeña, Andina, Rioplatense, Mexicana). JSON válido,
  los 6 campos llenos en cada uno.

Pendiente: ninguno — esquema listo para curar el lote real (Sesión 4).

## 2026-08-31 (2) — Paula Lozano

Sesión 4 — Primer lote de semillas (`seeds/lote_01.json`):

- 40 semillas curadas siguiendo `seeds/schema.md`, cubriendo 4
  macro-dialectos: Caribeña, Andina, Rioplatense y Mexicana, 10 cada uno
  (25% cada uno — muy por debajo del límite de 60/40).
- Mezcla de registro: 18 `informal` (dialecto regional sin ser jerga
  cerrada) y 22 `jerga`, sin mezclar ambas nociones en el mismo campo.
- Verificado: sin duplicados exactos dentro del lote ni contra los 5
  ejemplos de `seeds/ejemplos.json` (se corrigió un cruce inicial en
  "Estar camellando"); ninguna semilla quedó con la traducción de
  referencia vacía.

Conteo final por dialecto: Caribeña 10, Andina 10, Rioplatense 10,
Mexicana 10 (banco total incluyendo ejemplos.json: 45 semillas).

Pendiente: ampliar cobertura dialectal en un segundo lote (Sesión 9) y
priorizar los dialectos que queden subrepresentados frente al resto del
banco de semillas del equipo.

## Sesión 5 — 2026-08-30 — Mariana Malagón

Estructurar el repositorio + `CONTEXTO_PROYECTO.md`:

Qué se hizo:
- Verificado que `CONTEXTO_PROYECTO.md` contiene las 6 secciones
  esperadas (proyecto, PI1-3, pipeline, alcance por fase, arquitectura,
  atributos de calidad) — ya estaba completo, no necesitó cambios.
- Revisada la estructura de carpetas creada por Anderson en la Sesión 2
  (`seeds/`, `generation/`, `finetuning/`, `merging/`, `evaluation/`,
  `api/`) y completada con `docs/` (con `docs/README.md` explicando qué
  documentos van a vivir ahí, según el calendario de 10 semanas).
- Evaluado el formato de `BITACORA.md`: la prosa libre (fecha, autor,
  resumen) ya venía funcionando, pero le faltaba número de sesión y una
  estructura mínima de "qué se hizo / decisiones / pendiente". Se agregó
  una plantilla explícita al inicio del archivo y se etiquetaron las
  entradas existentes de Anderson con su número de sesión (Sesión 2).

Decisiones tomadas:
- No se creó carpeta `tests/` todavía — la primera prueba automatizada
  del calendario (`tests/test_integracion_e2e.py`) es de la Sesión 31
  (Semana 6); crearla ahora quedaría vacía sin propósito claro.
- No se reescribió el contenido narrativo de las entradas ya existentes
  de Anderson, solo se les agregó el número de sesión — evita el riesgo
  de alterar el registro histórico real.

Pendiente: ninguno para esta sesión. La plantilla de `BITACORA.md` queda
lista para que el resto del equipo la use desde la Sesión 6 en adelante.

## Sesión 6 — 2026-08-31 — Mariana Malagón

Diseñar el prompt de "derivación":

Qué se hizo:
- Diseñada la plantilla de derivación en `generation/prompt_derivacion.md`,
  cumpliendo los 4 requisitos pedidos: (1) conservar el significado real
  de la expresión, (2) generar 5-8 variantes por semilla variando
  contexto/registro/tono (no solo sinónimos), (3) salida en JSON
  estructurado y parseable, (4) prohibir inventar dialectos o mezclar el
  dialecto original con otro.
- Escrito `generation/probar_prompt_derivacion.py`: reutiliza el patrón
  de clientes de `generation/test_apis.py` (Groq/Cohere/Google) para
  mandar la plantilla a cualquiera de los 3 generadores sobre semillas
  reales de `seeds/lote_01.json`, y valida automáticamente que la salida
  sea JSON válido con 5-8 variantes.
- Probadas las funciones de construcción de prompt y de validación con
  datos reales (semilla `sem-007` del lote de Paula) de forma unitaria
  (sin llamar a ninguna API): el prompt se arma correctamente con los
  campos de la semilla, `limpiar_json` quita bloques ```json``` si el
  modelo los agrega pese a la instrucción, y `validar_salida` rechaza
  correctamente una respuesta con menos de 5 variantes.
- Confirmado que el manejo de errores del script es limpio: si falta
  una dependencia o una variable de entorno, reporta el error por
  semilla y sigue, en vez de tumbar todo el script.

Decisiones tomadas:
- La plantilla vive en `generation/prompt_derivacion.md` (documentación,
  como pide la Sesión 6) y también como constante en
  `probar_prompt_derivacion.py` (para poder ejecutarla) — ambas deben
  mantenerse en sync manualmente; para un prompt de este tamaño no vale
  la pena montar un mecanismo de sincronización automática.
- Elegidas `sem-007` ("Está brutal", Caribeña) y `sem-018` ("Hacer una
  vaca", Andina) del lote de Paula como semillas de prueba, por cubrir
  dos dialectos y registros distintos.

Pendiente: ninguno.

## Sesión 6 — 2026-08-31 (2) — Mariana Malagón

Cierre de la Sesión 6: prueba en vivo de la plantilla de derivación.

Qué se hizo:
- Configurado `.env` local con `COHERE_API_KEY` (trial key gratuita de
  Cohere).
- Instalado `cohere` de forma aislada (`pip install cohere`) en vez de
  `pip install -r requirements.txt` completo, porque este último
  intenta compilar `mergekit`/`pydantic-core`/`immutables` desde
  código fuente (necesitan Rust/Visual C++ Build Tools, no instalados,
  y sin wheels precompilados para Python 3.14 en Windows) — instalar
  solo la librería que hacía falta evitó ese problema por completo.
- Corrido `python generation/probar_prompt_derivacion.py --generador
  cohere --ids sem-007 sem-018` contra la API real de Cohere
  (`command-r-08-2024`).
- Resultado: **las 2 semillas pasaron la validación** — 7 variantes
  cada una, JSON válido, dialecto (Caribeña/Andina) conservado sin
  mezclar ni inventar otro, significado conservado, variando
  contexto/tono como se pedía.
- Pegada la salida real de `sem-007` en la sección "Ejemplo de salida"
  de `generation/prompt_derivacion.md`, reemplazando el placeholder de
  "pendiente".

Decisiones tomadas:
- Instalar dependencias de a una (no `-r requirements.txt` completo)
  cuando solo se necesita probar una parte pequeña del pipeline —
  evita arrastrar el problema de compilación de `mergekit` en máquinas
  sin toolchain de C++/Rust. Vale la pena que el equipo lo tenga en
  cuenta antes de la Sesión 44 (fusión con `mergekit`), donde sí van a
  necesitar ese toolchain instalado.

Pendiente: ninguno — Sesión 6 cerrada, los 3 criterios de aceptación
(plantilla diseñada, JSON válido, 5-8 variantes) están cumplidos con
evidencia real.

## Sesión 7 — 2026-08-31 — Anderson García

Automatizar la generación sintética del Generador 1 (Groq).

Qué se hizo:
- Escrito `generation/generar_sintetico.py`: lee todas las semillas de
  `seeds/lote_01.json`, arma el prompt de derivación
  (`generation/prompt_derivacion.md`) para cada una y lo manda a la API
  de Groq (`openai/gpt-oss-20b`, Generador 1 según `.env.example`).
- Manejo de errores transitorios (429 rate limit, timeouts, 5xx) con
  reintentos y backoff exponencial, respetando el header `Retry-After`
  de la API cuando está presente; errores no transitorios (ej. clave
  inválida) se reportan y detienen esa semilla sin tumbar el script.
- La salida cruda de cada semilla (texto tal cual lo devuelve el
  modelo, sin parsear como JSON, junto con el prompt enviado y
  metadatos) se guarda en `generation/raw/generador1/{seed_id}.json`
  **antes** de cualquier procesamiento posterior.
- Reanudable: si el archivo de salida de una semilla ya existe, el
  script la salta en vez de volver a llamar a la API — permite
  interrumpir y retomar sin gastar cuota de más ni duplicar llamadas.
- Docstring inicial con modo de uso y variable de entorno requerida
  (`GROQ_API_KEY`).

Prueba de aceptación: corrido
`python generation/generar_sintetico.py --ids sem-007 sem-018 sem-006`
contra la API real de Groq. Resultado: 3 archivos generados en
`generation/raw/generador1/`, cada uno con 5-8 variantes en JSON válido
(sem-006: 6, sem-007: 5, sem-018: 6), sin errores. Se volvió a correr
el mismo comando y las 3 semillas se saltaron correctamente (0
llamadas nuevas a la API), confirmando la reanudación sin duplicar
trabajo.

Decisiones tomadas:
- La plantilla de derivación se mantiene copiada manualmente en este
  script (igual que en `probar_prompt_derivacion.py`), siguiendo la
  decisión ya tomada en la Sesión 6 de no montar un mecanismo de sync
  automático para un prompt de este tamaño.
- La salida cruda incluye el prompt enviado y metadatos (modelo,
  timestamp) además de la respuesta, no solo el texto — facilita
  auditar/depurar sin tener que re-derivar qué se le mandó al modelo
  en cada llamada.

Pendiente: correr el script sobre las 40 semillas completas de
`seeds/lote_01.json` cuando el equipo esté listo para la generación
sintética real (no solo de prueba), y replicar este mismo patrón para
los Generadores 2 (Cohere) y 3 (Google) más adelante en el calendario.

## Sesión 8 — 2026-08-31 — Anderson García

Generación sintética completa del Generador 1 (Groq) + consolidación.

Qué se hizo:
- Corrido `python generation/generar_sintetico.py` sobre las 40
  semillas de `seeds/lote_01.json` (las 3 de la Sesión 7 se saltaron
  por ya existir, se generaron las 37 restantes). **40/40 semillas
  procesadas con éxito, 0 fallidas.**
- Consumo de cuota vigilado durante la corrida: solo **1 error 429**
  (rate limit) en toda la corrida, en `sem-012` — el reintento con
  backoff exponencial ya implementado en la Sesión 7 esperó 6s y la
  semilla se completó normalmente en el segundo intento. El resto (39
  semillas) no tuvo ningún reintento.
- Escrito `generation/consolidar.py`: junta las 40 salidas crudas de
  `generation/raw/generador1/` en `generation/dataset_generador1.json`,
  parseando cada `respuesta_cruda` como JSON, descartando variantes
  con `texto_dialectal` o `traduccion` vacíos, y deduplicando
  variantes exactas (mismo `texto_dialectal` recortado y en
  minúsculas) antes de agregarlas al dataset final.
- Corrido `python generation/consolidar.py`: **40/40 semillas con al
  menos 1 variante en el dataset final, 0 semillas falladas, 0
  variantes vacías descartadas, 0 variantes duplicadas exactas
  descartadas.**

**Totales:**
- Semillas procesadas: 40/40 (100%).
- Variantes totales en `generation/dataset_generador1.json`: **238**.
- Distribución por dialecto: Caribeña 59, Andina 60, Rioplatense 59,
  Mexicana 60 (balanceada, sin sesgo hacia un dialecto).
- Semillas fallidas: ninguna.

Decisiones tomadas:
- El dedupe de `consolidar.py` es global sobre todo el dataset (no por
  semilla), comparando `texto_dialectal` normalizado (recortado +
  minúsculas) — criterio pedido explícitamente ("dedupe por texto");
  no hizo falta en esta corrida porque no hubo duplicados exactos,
  pero queda listo para lotes futuros donde el modelo sí repita una
  variante.
- Cada fila del dataset consolidado conserva metadatos de trazabilidad
  (`seed_id`, `dialecto_region`, `registro_original_semilla`,
  `generador`, `modelo`) además de la variante en sí, siguiendo el
  mismo criterio de auditabilidad usado en `generar_sintetico.py`.

Pendiente: repetir generación + consolidación con los Generadores 2
(Cohere) y 3 (Google) para poder comparar entre generadores (PI1), y
ampliar el lote de semillas (Sesión 9, ya pendiente desde la Sesión 4)
antes de la comparación completa de la Fase 3.

## Sesión 9 — 2026-09-02 — Paula Lozano

Ampliar el banco de semillas (segundo lote).

Qué se hizo:
- Leídos `CONTEXTO_PROYECTO.md`, `seeds/schema.md` y `seeds/lote_01.json`
  para confirmar cobertura previa: 4 dialectos (Caribeña, Andina,
  Rioplatense, Mexicana) parejos en 10 semillas cada uno.
- Curadas 60 semillas nuevas en `seeds/lote_02.json`: 21 Caribeña,
  21 Andina, 22 Rioplatense, 21 Mexicana, y **15 de un dialecto nuevo:
  Chilena** (no cubierto en el lote 1), cumpliendo el mínimo de 60 y de
  sumar al menos un dialecto nuevo.
- Verificado por script que no hay duplicados exactos de
  `texto_original` entre `lote_02.json`, `lote_01.json` y
  `ejemplos.json`.

Decisiones tomadas:
- Como los 4 dialectos del lote 1 ya estaban perfectamente balanceados
  (10/10/10/10), no había ninguno "subrepresentado" al que priorizar;
  se repartió el nuevo material casi parejo entre los 4 (21/21/22/21) y
  se usó el resto del cupo para darle a Chilena una base sólida de 15
  semillas propias desde el arranque.
- No se modificó `seeds/schema.md`: `dialecto_region` ya era un campo
  de texto libre (no un enum cerrado), así que agregar "Chilena" no
  requirió ningún cambio de esquema.

Conteo final por dialecto (lote 1 + lote 2 combinados, 100 semillas):
Caribeña 21, Andina 21, Rioplatense 22, Mexicana 21, Chilena 15 —
ningún dialecto por debajo de 15.

Pendiente: seguir ampliando Chilena en lotes futuros si se quiere llegar
a una base tan grande como la de los otros 4 dialectos.

## Sesión 10 — 2026-09-02 — Paula Lozano

Muestreo humano de validación del dataset sintético.

Qué se hizo:
- Confirmado que `generation/dataset_generador1.json` existe (Sesión 8,
  Anderson): 238 variantes, Caribeña 59, Andina 60, Rioplatense 59,
  Mexicana 60.
- Escrito `evaluation/muestreo.py`: toma una muestra aleatoria del 15%
  (semilla fija `random.seed(42)` para reproducibilidad) **proporcional
  a la cantidad de variantes por dialecto** (no una muestra global
  ciega), y escribe `evaluation/muestreo_manual.csv` con columnas
  `id_muestra, seed_id, dialecto_region, texto_dialectal, traduccion,
  contexto_uso, calificacion, comentario`.
- Muestra resultante: 36 de 238 variantes (~15.1%) — Caribeña 9, Andina
  9, Rioplatense 9, Mexicana 9.
- Piloto de calificación de 10 ejemplos de la muestra (elegidos a
  propósito repartidos entre los 4 dialectos, no solo los primeros 10
  de la hoja, que habrían caído casi todos en Caribeña por el orden de
  las semillas), para probar que el formato de la hoja funciona:
  calificados como `correcta`, `parcial` o `incorrecta` con comentario
  de por qué.

Resultado del piloto (10/10 calificados): **8 correctas, 1 parcial,
1 incorrecta (80% de aciertos)**. Hallazgo concreto en la variante
incorrecta (`sem-016`, Andina): el Generador 1 metió "Che" —marcador
claramente Rioplatense— dentro de una variante etiquetada como Andina
("Che, ¡qué chimba tu nuevo look!"), **violando directamente la regla
de no mezclar dialectos** que exige `generation/prompt_derivacion.md`
(Sesión 6). La parcial (`sem-007`) tiene un desvío de sentido menor
("no me creías" → "I know you didn't believe it") aunque el núcleo de
jerga sí se tradujo bien. Vale la pena revisar si el Generador 1 mezcla
dialectos en más casos del dataset completo, no solo en este piloto.

Decisiones tomadas:
- El piloto de 10 ejemplos lo calificó el asistente de IA leyendo cada
  par español-inglés con criterio real (no cifras inventadas de
  antemano), como prueba del formato — no reemplaza a un hablante
  nativo real. Queda marcado explícitamente como provisional en el
  propio CSV (columna `comentario` con nota "[piloto IA]"); los 26
  restantes de la muestra quedan con `calificacion` vacía para que
  evaluadores humanos nativos (Sesión 22) los califiquen de verdad más
  adelante.
- El campo `contexto_uso` de cada variante se incluyó en la hoja además
  de lo mínimo pedido, porque sin él es difícil para un evaluador saber
  si el registro/tono de la traducción es apropiado.

Pendiente: que evaluadores humanos nativos confirmen o corrijan las 10
calificaciones piloto y completen las 26 filas restantes una vez estén
reclutados (Sesión 22); este muestreo del Generador 1 sirve como
plantilla reutilizable para los Generadores 2 y 3 más adelante.

## Sesión 11 — 2026-09-02 — Mariana Malagón

Validación automática de datos sintéticos (filtros).

Qué se hizo:
- Escrito `generation/validar.py` con 4 reglas: (1) longitud fuera de
  rango (<3 o >40 palabras — el máximo se calibró mirando la
  distribución real del dataset, que no pasa de 26 palabras), (2)
  casi idéntica a la semilla original sin variación real (similitud
  >= 0.8 con `difflib`, calibrado contra los datos reales: separa los
  2 casos genuinamente problemáticos de los que sí agregan contexto
  real), (3) idioma inesperado (heurística de palabras frecuentes
  es/en, exige >=2 coincidencias para evitar falsos positivos con
  frases cortas — probado explícitamente contra el dataset completo
  antes de fijar el umbral), (4) duplicada exacta dentro del dataset.
- Decisión de diseño explicada en el docstring: reglas 1, 2 y 4
  DESCARTAN (no hay ambigüedad); la regla 3 solo MARCA COMO SOSPECHOSA
  porque es una heurística aproximada, no un detector de idioma real.
- Corrido sobre `generation/dataset_generador1.json` (238 variantes):
  **236 aprobadas, 0 sospechosas, 2 descartadas (0.8%)** — muy por
  debajo del límite de 20%, no hizo falta ajustar la plantilla de
  derivación. Las 2 descartadas fueron variantes que solo le pegaban
  una palabra suelta a la semilla ("Che, ¿todo bien, che?" y "Ahorita
  te marco, ¿vale?").
- Generados `generation/dataset_generador1_limpio.json` (236
  variantes) y `generation/reporte_filtrado.md` con el desglose y
  ejemplos concretos de lo descartado.
- **Hallazgo importante, no cubierto por estas 4 reglas:** el caso de
  mezcla de dialecto que Paula encontró en su muestreo piloto (Sesión
  10, semilla `sem-016` Andina con un "Che" Rioplatense) sigue
  presente en el dataset limpio — ninguna de las 4 reglas de
  `validar.py` busca marcadores de otro dialecto, solo longitud,
  parecido a la semilla, idioma y duplicados. Queda documentado
  explícitamente en `generation/data_card_generador1.md` como
  limitación conocida y candidato a una futura Regla 5.

Decisiones tomadas:
- No se implementó una Regla 5 de detección de mezcla de dialectos en
  esta sesión — no estaba en el alcance pedido (las 4 reglas del
  prompt), y una heurística confiable para eso (lista de marcadores
  por dialecto) merece su propia sesión de diseño y calibración, no
  un agregado apurado.

Pendiente: evaluar si vale la pena agregar la Regla 5 (mezcla de
dialectos) antes del entrenamiento completo (Sesión 19), a la luz de
que ya hay evidencia real de que ocurre.

## Sesión 12 — 2026-09-02 (2) — Mariana Malagón

Splits train/val/test + data card.

Qué se hizo:
- Confirmado que `generation/dataset_generador1_limpio.json` existe
  (Sesión 11): 236 variantes, 40 semillas, 10 por cada uno de los 4
  dialectos.
- Escrito `generation/split_dataset.py`: reparte 80/10/10 **por
  semilla** (todas las variantes de una semilla van al mismo split,
  para no filtrar la respuesta correcta de entrenamiento a test) y
  **estratificado por dialecto** (el reparto 80/10/10 se hace dentro
  de cada dialecto por separado, no sobre el total mezclado), con
  semilla aleatoria fija (42) para reproducibilidad.
- El propio script verifica automáticamente, antes de escribir nada:
  que ninguna semilla quede en más de un split, y que la suma de
  variantes de los tres splits coincida con el total del dataset
  limpio. Si algo no cuadra, el script no escribe los archivos y
  reporta el error explícitamente (falla con código de salida 1).
- Resultado: train 32 semillas/189 variantes, val 4 semillas/24
  variantes, test 4 semillas/23 variantes (suma 236, correcto).
  Guardado en `generation/splits/dataset_generador1/{train,val,test}.json`.
- Escrita la data card `generation/data_card_generador1.md`: tamaño,
  cobertura por dialecto, cómo se generó, filtros aplicados (Sesión
  11), splits, y limitaciones conocidas — incluyendo explícitamente el
  hueco de la Regla 5 (mezcla de dialectos) de la sesión anterior, y
  que este dataset solo cubre `seeds/lote_01.json` (no el lote 2 de
  Paula, que llegó después de que Anderson generara este dataset).

Decisiones tomadas:
- Los splits quedan en `generation/splits/<nombre_dataset>/` (no
  sueltos en `generation/`) para que cuando se generen los splits de
  los Generadores 2 y 3 (Sesión 41-42) no se sobrescriban entre sí —
  cada uno en su propia subcarpeta con el mismo nombre de archivo
  (`train.json`, `val.json`, `test.json`) que pide la Sesión 12.
- Split estratificado por dialecto en vez de aleatorio simple sobre
  las 40 semillas, porque con solo 40 semillas un split aleatorio
  simple podía dejar algún dialecto fuera de val o test por pura
  casualidad; estratificar lo evita de raíz.

Pendiente: ninguno — Sesión 12 cerrada, los tres criterios de
aceptación (splits existen, tamaños suman el total, sin semillas
repetidas entre splits) verificados automáticamente por el propio
script.

## Sesión 13 — 2026-09-02 — Anderson García

Línea base del SLM candidato sin ajustar.

Qué se hizo:
- Bloqueo inicial: `meta-llama/Llama-3.2-3B-Instruct` (candidato
  principal) tiene `gated="manual"` en HuggingFace — Meta revisa el
  acceso a mano, no automático — y la cuenta usada para pedir el
  token tenía el correo sin verificar. La descarga falló con
  `GatedRepoError` (403 "not in authorized list") pese a tener
  `HF_TOKEN` válido con permiso de lectura, aunque `HfApi.model_info`
  sí funcionaba (esa llamada solo lee metadata pública, no exige
  acceso aprobado). Consultado con el equipo: se decidió usar
  **Qwen2.5-3B-Instruct** para esta línea base — es la alternativa ya
  listada en `CONTEXTO_PROYECTO.md`, sin licencia restringida, y
  desbloqueaba la tarea sin esperar la revisión de Meta.
- Escrito `finetuning/probar_baseline.py`: carga el modelo en
  `bfloat16` sin cuantizar, en CPU, y prueba traducción zero-shot
  sobre 8 ejemplos reales de `generation/splits/dataset_generador1/test.json`
  (2 por cada uno de los 4 dialectos).
- **Decisión de precisión, justificada en el código**: bfloat16 sin
  cuantizar. El `torch` de este entorno es la build CPU-only
  (`torch==2.13.0+cpu`, sin CUDA), y la única GPU NVIDIA de la máquina
  (MX230) tiene solo 2GB de VRAM — insuficiente incluso para un 3B en
  4-bit, y `bitsandbytes` no acelera nada sin CUDA. La máquina sí
  tiene 18GB de RAM, y un 3B en bfloat16 pesa ~6-6.5GB: entra sin
  problema sin necesidad de cuantizar. El cuello de botella real es la
  ausencia de GPU, no la memoria.
- Bug encontrado y corregido: con `transformers==5.12.1`,
  `tokenizer.apply_chat_template(..., return_tensors="pt")` sin
  `return_dict=True` devuelve un `BatchEncoding` en vez de un tensor
  plano, y `modelo.generate()` fallaba con `AttributeError` al pedir
  `.shape`. Arreglado pasando `return_dict=True` y desempacando con
  `**entrada` en `generate()`.
- Corrido el script: **las 8 generaciones terminaron sin errores de
  memoria** (descarga ~6GB del modelo la primera vez, ~18 min por
  ancho de banda; la generación en sí tardó menos de 1 minuto una vez
  cargado el modelo).
- Guardadas las salidas crudas en
  `finetuning/baseline_sin_ajustar_salidas.json` y el análisis
  narrado en `finetuning/baseline_sin_ajustar.md`, con los 8 ejemplos
  reales (español dialectal, referencia, salida del modelo) y 5 tipos
  de error identificados: (1) falso amigo con el significado estándar
  en vez del dialectal ("tinto" → "red wine" en vez de "coffee", en
  el 100% de sus apariciones), (2) traducción literal de modismos
  ("estar remando" → "rowing" en vez de "barely getting by"), (3)
  muletillas de jerga tratadas de forma inconsistente ("neta" omitida
  una vez, traducida como "Surely" otra vez), (4) la misma palabra de
  jerga traducida bien en una oración y literal en otra ("brutal" →
  "fantastic" vs. "brutal", ambas de la semilla `sem-007`), (5) calcos
  gramaticales menores ("armó la fiesta" → "did a... party").

Decisiones tomadas:
- Sustituir Llama 3.2 3B por Qwen2.5-3B-Instruct SOLO para esta línea
  base, documentado explícitamente en el docstring de
  `probar_baseline.py` y en `baseline_sin_ajustar.md`, con el motivo
  exacto — para no perder trazabilidad de por qué el candidato
  principal no es el que aparece en esta línea base. El script queda
  listo para reproducir el mismo baseline con Llama 3.2 3B cambiando
  solo `MODEL_ID` en cuanto el acceso quede aprobado.
- Agregado `HF_TOKEN` a `.env.example`, documentado (necesario para
  modelos con licencia restringida como Llama 3.2, aunque Qwen2.5 no
  lo necesite).

Pendiente: reintentar con Llama 3.2 3B Instruct cuando el equipo
verifique el correo de la cuenta de HuggingFace y Meta apruebe el
acceso; comparar este baseline contra las salidas del modelo ya
ajustado con LoRA cuando esté listo (Fase 2, Semana 4-5).

## Sesión 14 — 2026-09-02/03 — Anderson García

Prueba de humo del pipeline de fine-tuning con LoRA (EN CURSO — se
movió a Google Colab a mitad de sesión, resultados finales pendientes).

Qué se hizo:
- Confirmado en BITACORA.md que Paula no había dejado listo el script
  de LoRA (solo estaban los archivos del baseline de la Sesión 13).
  Sin script que coordinar, se escribió `finetuning/entrenar_lora.py`
  desde cero esta sesión: carga el subconjunto de prueba de
  `generation/splits/dataset_generador1/train.json` (50 ejemplos,
  límite inferior del rango 50-100 pedido), tokeniza cada ejemplo con
  el MISMO prompt de sistema que `probar_baseline.py` (mismo formato
  en entrenamiento y evaluación), enmascara con `label=-100` los
  tokens del prompt para que la pérdida solo se calcule sobre la
  traducción, entrena un adaptador LoRA (`r=8`, `alpha=16`, sobre
  `q_proj/k_proj/v_proj/o_proj`) con `peft` + `transformers.Trainer`,
  guarda el adaptador en disco, y luego lo **recarga desde disco**
  (no reutiliza el objeto en memoria) para probar inferencia sobre los
  mismos 8 ejemplos de `test.json` que usa el baseline — así se puede
  comparar "antes" vs. "después" sobre exactamente los mismos casos.
- **Bloqueo real, no cubierto por el plan original**: se intentó
  correr el entrenamiento de prueba en la máquina local (sin GPU
  CUDA, la misma usada para la Sesión 13). Encontrado y corregido en
  el camino un bug de compatibilidad (`tokenizer.apply_chat_template`
  sin `return_tensors` devuelve un `BatchEncoding`, no una lista de
  ids — hacía falta `["input_ids"]` explícito). Una vez corregido el
  código, el entrenamiento sí arrancó y la pérdida sí se calculaba
  correctamente paso a paso, pero **cada paso tardaba 80-95 minutos en
  CPU pura** — a las 10 horas de correr solo se había completado el
  5% (8 de 150 pasos) y se interrumpió manualmente. CPU pura NO es
  viable ni para una prueba de humo de 150 pasos con un modelo de 3B,
  aunque sea con LoRA (los pesos base congelados igual participan del
  forward/backward, así que LoRA no evita el costo de cómputo del
  backprop a través del modelo completo, solo reduce cuántos
  parámetros se actualizan).
- **Decisión del equipo**: mover el entrenamiento a Google Colab (GPU
  gratuita T4/L4). Se actualizó `probar_baseline.py` para detectar el
  dispositivo automáticamente (`device_map="auto"` si hay CUDA, si no
  `"cpu"`) y mover los tensores de entrada al dispositivo del modelo
  en `traducir()` — así el mismo código sirve para la máquina local
  (CPU) y para Colab (GPU) sin cuantizar en ningún caso, porque un 3B
  en bfloat16 (~6-6.5GB) cabe cómodo tanto en 18GB de RAM local como
  en la VRAM libre de una GPU gratuita de Colab (~15GB) — cuantizar no
  habría resuelto el problema real, que era la falta de GPU, no de
  memoria.
- Creado `finetuning/entrenar_lora_colab.ipynb`: notebook listo para
  correr en Colab (clona el repo público desde GitHub, instala solo
  las dependencias necesarias sin tocar el `torch`+CUDA que ya trae
  Colab preinstalado, corre `entrenar_lora.py`, y empaqueta/descarga
  el adaptador + la curva de pérdida + las traducciones de prueba al
  final).
- Ajustado `.gitignore`: la regla genérica de "no versionar modelos
  pesados" (`*.safetensors`, `*.bin`) bloqueaba también los
  adaptadores LoRA (solo unos MB, no un modelo completo) — agregada
  una excepción explícita para `finetuning/**/adapter/`.
- **Aparte, a pedido del equipo**: agregado `.githooks/pre-commit`,
  que bloquea cualquier commit que modifique archivos del proyecto sin
  incluir una entrada nueva en `BITACORA.md` (documentado en
  README.md, sección "Instalación del entorno", paso 4 — hay que
  activarlo a mano una vez por clon con
  `git config core.hooksPath .githooks`, git no lo activa solo).
  Mencionado también en `CONTEXTO_PROYECTO.md` para que quede claro
  que la regla de "todo commit relevante lleva entrada en BITACORA.md"
  ya no es solo una convención escrita.

**Lo que falta (bloqueado en traer los resultados de Colab, no en
código)**: correr `entrenar_lora_colab.ipynb`, confirmar que la
pérdida baja de forma consistente, y traer de vuelta al repo el
adaptador entrenado (`finetuning/lora_prueba/adapter/`), la curva de
pérdida real (`finetuning/lora_prueba/loss_log.json`) y las
traducciones de prueba con el adaptador
(`finetuning/lora_prueba/salidas_con_adapter.json`) para escribir
`finetuning/prueba_loss.md` con datos reales y comparar contra
`finetuning/baseline_sin_ajustar_salidas.json`. No se inventan estos
resultados en esta entrada — se documentan en una sesión de
continuación en cuanto estén disponibles.

Decisiones tomadas:
- Escribir el script de LoRA en esta sesión en vez de esperar a Paula,
  documentado explícitamente como tal, para no bloquear la prueba
  end-to-end (decisión tomada con el equipo).
- No inventar una curva de pérdida ni resultados de comparación —
  aunque el prompt pedía documentarlos en esta sesión, el
  entrenamiento real todavía no ha terminado en ningún entorno; se
  prefiere dejarlo pendiente y honesto en vez de rellenar
  `finetuning/prueba_loss.md` con datos ficticios.

Pendiente: correr `finetuning/entrenar_lora_colab.ipynb` en Colab con
GPU, traer los resultados al repo, y completar
`finetuning/prueba_loss.md` + esta entrada de bitácora con los números
reales (pérdida por paso, confirmación de que baja de forma
consistente, comparación de las salidas del adaptador contra el
baseline sin ajustar).

## Sesión 14 — 2026-09-03 (2) — Anderson García

Bug encontrado al correr `entrenar_lora_colab.ipynb` por primera vez
en Colab: la celda 2 (clonar + `%cd`) usaba una ruta relativa
(`%cd traductor-jerga-dialectal-slm`); al volver a correrla (sin
reiniciar el entorno) el `%cd` partía de dentro del repo ya clonado,
dejando un clon anidado dentro de sí mismo
(`/content/traductor-jerga-dialectal-slm/traductor-jerga-dialectal-slm`),
y la celda 4 fallaba con `python3: can't open file
'.../finetuning/entrenar_lora.py'` porque el archivo real quedaba un
nivel más arriba. Corregido en el notebook: ahora usa `%cd /content`
al inicio, solo clona si el repo no existe todavía, y hace `%cd` con
ruta absoluta al final — así queda seguro volver a correr la celda
cualquier número de veces.

Con ese fix, la celda 4 sí llegó a descargar y cargar el modelo
(6.17GB en ~1 min, gracias al ancho de banda de Colab), pero falló en
`get_peft_model()` con `ImportError: Found an incompatible version of
torchao. Found version 0.10.0, but only versions above 0.16.0 are
supported`. Causa: Colab trae `torchao` preinstalado en una versión
vieja, y la versión más reciente de `peft` (instalada sin pin de
versión en la celda 3) revisa esa versión al despachar el módulo LoRA
aunque no se use cuantización con `torchao` para nada en este
entrenamiento. Arreglado agregando `!pip uninstall -y -q torchao` a la
celda 3 — sin el paquete, `peft` simplemente se salta esa revisión y
sigue por el camino normal (sin cuantizar). De paso, corregido un
mensaje de log engañoso en `entrenar_lora.py` y `probar_baseline.py`
que decía "(CPU, sin cuantizar)" siempre, sin reflejar el dispositivo
real detectado.

## Sesión 14 — 2026-09-03 (3) — Anderson García

Cierre: entrenamiento completo en Colab, resultados reales.

Qué se hizo:
- Con el fix del `torchao`, el entrenamiento completo (150 pasos, 3
  épocas, 50 ejemplos) corrió sin errores en Colab (GPU T4) en pocos
  minutos — nada que ver con las 10h+ que llevaba en CPU local.
- **Pérdida: baja de forma consistente.** Promedio por época: 1.011
  (época 1) → 0.458 (época 2) → 0.263 (época 3) — ~4x menor entre la
  primera y la última época, pese al ruido normal de correr con batch
  size 1. Se cumple el criterio de calidad pedido sin necesitar tocar
  la tasa de aprendizaje ni el formato de los datos.
- **Adaptador guardado y recargado desde disco, verificado de
  verdad**: el script libera de memoria el modelo de entrenamiento
  (`del trainer, modelo, modelo_base; gc.collect()`) y vuelve a
  cargarlo desde cero + el adaptador (`PeftModel.from_pretrained`)
  antes de generar las traducciones de prueba — no reutiliza el
  objeto que quedó en memoria tras entrenar.
- **Comparación contra el baseline sin ajustar (Sesión 13), mismos 8
  ejemplos de `test.json`**: las 8 salidas cambiaron respecto al
  baseline (100%). Mejoras claras en 2-3 de los 8 (el error de
  "brutal" → "brutal" literal del baseline se corrige a "insane"; el
  modismo "estar remando" se traduce como "struggling" en vez de
  "rowing" en uno de los dos casos, parcialmente en el otro). El
  error más sistemático del baseline ("tinto" → vino en vez de café)
  **no se corrigió** — la semilla `sem-025` cayó en el split de test,
  no en los 50 ejemplos de entrenamiento, así que no había señal de la
  que aprender ese caso puntual; comportamiento esperado de una
  prueba de humo con tan pocos datos, no un defecto del pipeline.
- **Hallazgo a vigilar**: dos ejemplos distintos de test (`sem-025`,
  "amigo" vs. "colega") dieron exactamente la misma salida — posible
  señal de memorización/sobreajuste con tan pocos ejemplos y épocas,
  a revisar cuando se entrene con el dataset completo.
- Escrito `finetuning/prueba_loss.md` con la curva de pérdida completa,
  la tabla comparativa baseline-vs-adaptador de los 8 ejemplos, y el
  análisis de qué mejoró y qué no.
- Traídos al repo desde Colab: `finetuning/lora_prueba/adapter/`
  (~14.8MB, adaptador LoRA), `finetuning/lora_prueba/loss_log.json`
  (150 valores de pérdida) y
  `finetuning/lora_prueba/salidas_con_adapter.json` (las 8
  traducciones de prueba).

Decisiones tomadas:
- No reentrenar con más datos/épocas en esta sesión para "arreglar" el
  caso de "tinto" — esta sesión era una prueba de humo del pipeline,
  no el entrenamiento final; ese caso queda documentado como pendiente
  natural para el entrenamiento completo (Sesión 19+), que sí cubre
  todas las semillas.

Pendiente: entrenamiento completo con el dataset completo (Sesión
19+); vigilar el indicio de sobreajuste (misma salida para dos
ejemplos distintos) al escalar — considerar más datos, más
variedad por paso (batch size > 1), o menos épocas si se repite con
un dataset más grande.

## Sesión 14 — 2026-09-03 (4) — Anderson García

Mejoras de proceso (no calendario oficial — pedido aparte del equipo,
motivado directamente por lo aprendido en esta sesión): reforzar la
exigencia de documentación en cada commit y dejar por escrito la
política de "cómputo pesado siempre en Colab".

Qué se hizo:
- Reforzado `.githooks/pre-commit`: ya no basta con que `BITACORA.md`
  esté en el commit (Sesión 14 (1)) — ahora también revisa que el
  diff agregue contenido real (no un `git add` vacío) y que ese
  contenido siga el formato mínimo de la plantilla (busca la línea
  "Qué se hizo"). Bloquea el commit si falta cualquiera de las dos
  cosas. Agregado también un aviso NO bloqueante: si el commit crea
  archivos fuera de las carpetas que ya describe `README.md` y el
  README no está en el commit, recuerda considerar actualizarlo.
- Probado a mano (`sh .githooks/pre-commit` sobre un archivo de
  prueba) que la regla bloqueante 1 sigue funcionando igual que en la
  Sesión 14 (1).
- Agregada a `CONTEXTO_PROYECTO.md` la sección "CÓMPUTO PESADO:
  SIEMPRE EN GOOGLE COLAB, NUNCA EN LA MÁQUINA LOCAL": paso a paso
  genérico (no específico de LoRA) para correr cualquier script pesado
  futuro en Colab — cómo evitar el bug de clon anidado, instalar solo
  dependencias puntuales (no `requirements.txt` completo), el fix de
  `torchao` con `peft`, detección automática de dispositivo sin
  cuantizar de más, y cómo traer los resultados de vuelta al repo.
  Referencia cruzada agregada en `README.md`.
- Creado `CLAUDE.md` en la raíz del repo: instrucciones persistentes
  para que Claude Code, en cualquier sesión futura en este
  repositorio, (1) **nunca agregue coautoría de Claude en los
  commits** salvo que se le pida explícitamente para un commit
  puntual, (2) siga Conventional Commits, (3) respete la regla de
  entrada real en `BITACORA.md` por commit, y (4) use siempre Google
  Colab para cómputo pesado, nunca la máquina local.

Decisiones tomadas:
- Poner el paso a paso de Colab en `CONTEXTO_PROYECTO.md` (no en
  `BITACORA.md`) porque `BITACORA.md` es un registro cronológico de
  solo-agregar por convención propia del archivo ("no se reescriben
  las anteriores") — no es el lugar para una guía de referencia
  permanente que se vaya a consultar y actualizar con el tiempo;
  `CONTEXTO_PROYECTO.md` sí es ese documento vivo.
- Esta entrada usa "Sesión 14 (4)" en vez de un número nuevo: no
  corresponde a ningún número del calendario oficial del curso (la
  Sesión 15 ya está asignada a otra persona del equipo para otra
  tarea) — es trabajo de proceso/tooling motivado por el cierre de la
  Sesión 14, no una sesión nueva del calendario.

Pendiente: ninguno para esta entrada — el resto de pendientes sigue
siendo el mismo que el cierre de la Sesión 14 de arriba.

## Sesión 15 — 2026-09-10 — Paula Lozano

Configurar LoRA + script de fine-tuning.

Contexto: `finetuning/entrenar_lora.py` ya existía — Anderson lo escribió
en la Sesión 14 para no bloquear la prueba end-to-end, documentado
explícitamente ahí como una desviación (Paula no lo había dejado listo
todavía). Esta sesión no repite ese trabajo: cierra los dos requisitos
concretos del prompt original de la Sesión 15 que ese script no
cumplía.

Qué se hizo:
- **Justificación de hiperparámetros**: agregado un comentario por cada
  valor de `LoraConfig` en `entrenar_lora.py` (antes no tenían
  ninguno) — por qué `r=8` (capacidad modesta apropiada para ~3B con
  dataset chico, adaptador liviano acorde a portabilidad), por qué
  `lora_alpha=16` (heurística estándar `alpha=2*r`, para que siga
  siendo válida si `r` cambia al escalar en la Sesión 19+), por qué
  `lora_dropout=0.05` (regularización barata; se deja igual porque ya
  hay indicio de sobreajuste documentado en la Sesión 14 con este mismo
  valor), por qué `bias="none"` (default estándar de LoRA para LLMs
  causales) y por qué `target_modules` son solo las proyecciones de
  atención Q/K/V/O (mayor impacto en adaptar el modelo a la tarea,
  adaptador más chico que si se incluyeran las capas MLP).
- **Dataset configurable por parámetro**: agregado `--dataset-dir` (CLI,
  `argparse`) para poder reutilizar el mismo script con los Generadores
  2 y 3 en la Semana 7, tal como pedía el prompt original. Refactor de
  `entrenar()` y `probar_adapter_recargado()` para recibir las rutas
  como parámetros en vez de constantes de módulo fijas.
- Para no pisar los resultados de la Sesión 14 (`finetuning/lora_prueba/`,
  ya committeados: adaptador, curva de pérdida, salidas), el default de
  `--dataset-dir` sigue siendo `dataset_generador1` y sigue escribiendo
  en `finetuning/lora_prueba/` igual que antes; cualquier otro dataset
  escribe en `finetuning/lora_prueba_<generadorN>/` en vez de
  sobrescribir.
- Actualizado el docstring del script con el nuevo uso (`--dataset-dir`)
  y la nota de que la Sesión 15 completó lo que la Sesión 14 dejó
  pendiente.

Decisiones tomadas:
- No se volvió a correr el entrenamiento completo en Colab: el cambio
  es de refactor (parametrizar rutas ya usadas) + comentarios (no toca
  lógica de entrenamiento), así que no había necesidad de repetir el
  cómputo pesado que Anderson ya corrió y documentó en la Sesión 14.
  Verificado en su lugar, sin GPU, que (a) el script sigue compilando
  (`python -m py_compile`) y (b) la lógica de resolución de rutas
  (`--dataset-dir` por default vs. uno nuevo) produce exactamente las
  rutas esperadas, probada de forma aislada sin importar `torch`/`peft`
  (no instalados en esta máquina — ver política de Colab en
  `CLAUDE.md`).
- No se creó un script nuevo (`finetuning/entrenar.py`) separado del ya
  existente `entrenar_lora.py` — habría duplicado exactamente el mismo
  pipeline ya probado end-to-end; se prefirió completar el que ya
  funciona.

Pendiente: correr `entrenar_lora.py --dataset-dir
generation/splits/dataset_generadorN` de verdad en Colab cuando existan
los splits de los Generadores 2 y 3 (Semana 7) para confirmar que el
parámetro nuevo funciona en la práctica, no solo en la prueba aislada
de rutas.

## Sesión 16 — 2026-09-10 — Paula Lozano

Depurar el primer entrenamiento.

Contexto: el objetivo de esta sesión (que el entrenamiento de prueba
converja de forma estable, con los problemas encontrados documentados)
**ya quedó cumplido en la Sesión 14**, hecho por Anderson junto con el
script de LoRA. No se repite el entrenamiento para no duplicar cómputo
ya hecho y documentado.

Qué se hizo (verificación, no repetición):
- Revisados `BITACORA.md` (Sesión 14, entradas 2 y 3) y
  `finetuning/prueba_loss.md`: se depuraron 3 problemas reales antes de
  llegar a una corrida estable — bug de clon anidado en el notebook de
  Colab, incompatibilidad de `torchao` con la versión de `peft` sin
  pin, y un bug de formato en `apply_chat_template` (devuelve un
  `BatchEncoding`, no una lista de ids directamente).
- Confirmado que, con esos tres fixes, la pérdida **converge de forma
  estable y sin picos erráticos**: 1.011 (época 1) → 0.458 (época 2) →
  0.263 (época 3), ~4x de mejora entre la primera y la última época.
- Confirmado que cada cambio respecto a la configuración anterior está
  explicado con su causa en la Sesión 14 (no un genérico "probé varias
  cosas"), cumpliendo el criterio de calidad pedido en el prompt
  original de esta sesión.

Decisiones tomadas:
- No volver a correr el entrenamiento de prueba: repetirlo en Colab
  solo para generar una "Sesión 16" separada habría sido cómputo
  redundante sobre exactamente el mismo script, mismo dataset y misma
  configuración que la Sesión 14 ya corrió y dejó documentada con
  evidencia real (curva de pérdida, comparación baseline-vs-adaptador).
- El único cambio de código tocado en esta sesión que afecta a
  `entrenar_lora.py` es el de la Sesión 15 (arriba) — ninguno de los
  dos cambios (comentarios, `--dataset-dir`) altera la lógica de
  entrenamiento en sí, así que la curva de pérdida ya documentada en
  `finetuning/prueba_loss.md` sigue siendo válida sin necesidad de
  volver a correrla.

Pendiente: ninguno específico de esta sesión — el pendiente real (vigilar
el indicio de sobreajuste al escalar a más datos) ya quedó registrado en
la Sesión 14 para la Sesión 19+.

## Sesión 17 — 2026-09-10 — Mariana Malagón

Preparar tokenizador/formato de instrucción.

Contexto: igual que las Sesiones 15-16, el formato de instrucción
(`SYSTEM_PROMPT` + `apply_chat_template`, turnos system/user/assistant)
ya estaba implementado desde la Sesión 13-14 (`probar_baseline.py`,
`entrenar_lora.py`), y ya es idéntico en entrenamiento e inferencia
porque ambos scripts importan el mismo `SYSTEM_PROMPT` de un solo
lugar. Esta sesión no repite ese trabajo: documenta el formato
formalmente y corre la verificación de round-trip que pedía el prompt
original, que todavía no existía como prueba explícita.

Qué se hizo:
- Instalado `transformers` de forma aislada (no `-r requirements.txt`
  completo, mismo criterio que la Sesión 6) solo para cargar el
  tokenizador de `Qwen/Qwen2.5-3B-Instruct` — **sin PyTorch ni pesos
  del modelo**, confirmado explícitamente que esto no es "cómputo
  pesado" según la política de Colab de `CONTEXTO_PROYECTO.md`
  (fine-tuning, fusión, evaluación masiva o inferencia sobre muchos
  ejemplos): es una sola operación de tokenización/decodificación,
  instantánea, sin necesidad de GPU.
- Tomado un ejemplo real de `generation/splits/dataset_generador1/train.json`
  (`sem-013`), armado el prompt con el mismo código que usa
  `entrenar_lora.py` (`DatasetTraduccion.__getitem__`), y verificado:
  (1) el texto decodificado de los ids tokenizados coincide EXACTO,
  carácter por carácter, con el texto de la plantilla de chat antes de
  tokenizar; (2) decodificando solo los tokens no enmascarados con
  `-100` (la parte que de verdad aprende el modelo) se reconstruye
  exactamente la traducción de referencia del ejemplo.
- Escrito `finetuning/formato_instruccion.md`: explica el formato (3
  turnos, por qué es el mismo en entrenamiento/inferencia, cómo
  funciona el enmascarado de la pérdida) con el ejemplo real completo
  (antes de tokenizar, después de tokenizar, y el resultado de las dos
  verificaciones de round-trip).

Decisiones tomadas:
- Inicialmente no se tocó `entrenar_lora.py` — se pensó que el formato
  ya estaba completo porque el round-trip con un ejemplo normal daba
  bien. Al revisar el prompt original de la Sesión 17 otra vez punto
  por punto (a raíz de que el usuario preguntó explícitamente "¿ya
  cumplimos esto?"), se encontró que faltaba un requisito real: "el
  truncamiento de secuencias largas". `entrenar_lora.py` no tenía
  ninguna lógica de truncamiento (verificado: cero menciones de
  `truncat`/`max_length` en el archivo) — no rompía nada hoy porque la
  secuencia más larga del dataset actual son 125 tokens contra un
  contexto de 131,072 del tokenizador, pero el código no lo manejaba
  explícitamente. Corregido: agregado `MAX_LENGTH = 512` con
  truncamiento desde la izquierda (nunca desde la derecha, para no
  cortar la traducción de referencia), verificado con un ejemplo
  sintético de 703 tokens (queda en exactamente 512, la respuesta
  sobrevive intacta) y sin regresión en el ejemplo normal de 89
  tokens. Documentado en `finetuning/formato_instruccion.md`.

Pendiente: ninguno — Sesión 17 cerrada. Los dos requisitos del prompt
original quedaron cubiertos con evidencia real: manejo de tokens
especiales (ya existía) y truncamiento de secuencias largas (agregado
y verificado en esta revisión).

## Sesión 18 — 2026-09-10 (2) — Mariana Malagón

Actualizar paper: Arquitectura (Fase 2).

Qué se hizo:
- Leído el paper de Fase 1 completo (compartido por el usuario como
  PDF, no estaba en este repo) para poder mantener el mismo tono y voz
  en el borrador nuevo — primera persona plural, honestidad explícita
  sobre limitaciones, sin sonar a lista genérica.
- Releídas todas las entradas de `BITACORA.md` de las Sesiones 1-17
  para extraer únicamente decisiones técnicas ya tomadas, sin rellenar
  con nada no verificado.
- Escrito `docs/fase2_arquitectura_borrador.md`, continuando la
  numeración del paper como Sección 8, con 4 subsecciones: 8.1
  arquitectura de datos (banco de semillas → derivación → generación
  → validación → splits, con las cifras reales de cada etapa), 8.2
  arquitectura de aplicación (lo que existe: scripts de línea de
  comandos; lo que falta: API/despliegue/Docker/seguridad/
  observabilidad, Semanas 5-6), 8.3 arquitectura de tecnología (Qwen2.5-3B-Instruct
  y por qué no Llama, configuración de LoRA con su justificación,
  formato de instrucción, resultados reales de la prueba de humo), y
  8.4 un resumen consolidado de pendientes.
- **Encontrado y corregido un error propio antes de entregar el
  borrador**: había escrito que `generar_sintetico.py` ya estaba
  parametrizado para cualquier generador, igual que `validar.py` y
  `split_dataset.py`. Al verificar contra el código real (no contra la
  memoria de la sesión), confirmé que `generar_sintetico.py` sigue
  fijo a Groq (cliente, carpeta de salida y el campo `"generador"`
  hardcodeados) — la parametrización real solo existe en
  `validar.py`/`split_dataset.py` (reciben la ruta del dataset como
  parámetro) y en `entrenar_lora.py` (`--dataset-dir`, Sesión 15).
  Corregido antes de que quedara una afirmación falsa en el
  documento del equipo.

Decisiones tomadas:
- Dejar la fusión de modelos fuera de esta sección de arquitectura sin
  comprometerme con un número de semana específico: noté que
  `CONTEXTO_PROYECTO.md` dice que la fusión simple entra en el alcance
  de la Fase 2, pero el calendario de sesiones la ubica en la Semana 8
  (dentro del rango que el propio `CONTEXTO_PROYECTO.md` llama Fase
  3) — es una inconsistencia real entre los documentos de planeación
  del equipo, no algo que me corresponda resolver unilateralmente en
  un borrador de arquitectura. La dejé mencionada como "pendiente,
  fuera del alcance de esta fase por decisión explícita" sin fijar una
  fecha, y avisé de la inconsistencia en esta misma entrada para que
  el equipo la resuelva.

Pendiente: que el equipo revise el borrador contra esta bitácora
(criterio de aceptación de la Sesión 18) y decida cómo resolver la
inconsistencia de alcance de la fusión de modelos entre
`CONTEXTO_PROYECTO.md` y el calendario de sesiones antes de integrar
esta sección al `.tex` final (Sesión 32).

## Sesión 19 — 2026-09-11 — Anderson García

Entrenamiento completo de LoRA del Generador 1, con validación (EN
CURSO — código listo, corrida real pendiente en Colab).

Contexto: la configuración de LoRA (`r=8`, `alpha=16`, `dropout=0.05`,
`bias="none"`, Q/K/V/O) quedó validada y justificada en las Sesiones
15-16 y no cambia aquí. Esta sesión extiende `entrenar_lora.py` (no
crea un script nuevo, mismo criterio de la Sesión 15) para agregar lo
que le faltaba: entrenar sobre TODOS los ejemplos (no solo la muestra
de 50 de la prueba de humo) y validar durante el entrenamiento.

Qué se hizo:
- Agregado el modo `--todos` a `entrenar_lora.py`: usa el `train.json`
  completo (189 ejemplos para el Generador 1) en vez de la muestra de
  50, valida sobre `val.json` (24 ejemplos) al final de cada época
  (`eval_strategy="epoch"`), y usa `load_best_model_at_end=True` +
  `EarlyStoppingCallback(patience=2)` de `transformers` para detectar
  sobreajuste automáticamente: si la pérdida de validación no mejora
  durante 2 épocas seguidas mientras la de entrenamiento sigue
  bajando, el entrenamiento se detiene ahí y el adaptador que se
  guarda es el del MEJOR checkpoint según validación, no el de la
  última época — cumple el criterio de calidad pedido sin necesitar
  vigilancia manual de la curva.
- Límite superior de épocas generoso (`EPOCAS_COMPLETO_MAX = 10`, no
  un número "adivinado" como el real) porque el early stopping corta
  antes si hace falta; documentado en el código por qué no se fija un
  número exacto de antemano.
- `RegistrarPerdida` ahora registra también la pérdida de validación
  (antes solo entrenamiento) — el log queda como `{"train": [...],
  "eval": [...]}` cuando hay validación; se mantiene el formato plano
  de antes (lista simple) cuando no la hay, para no romper
  `finetuning/lora_prueba/loss_log.json` ya committeado (Sesión 14).
- Salida del modo `--todos` en `finetuning/checkpoints/<generadorN>/`
  (para el Generador 1: `finetuning/checkpoints/generador1/`), NO en
  `finetuning/lora_prueba/` — esa carpeta sigue siendo solo de la
  prueba de humo. Los checkpoints INTERMEDIOS del Trainer (uno por
  época, con estado del optimizador — mucho más pesados que el
  adaptador final y sin valor una vez elegido el mejor) se guardan en
  un directorio temporal FUERA del repo (`tempfile.mkdtemp()`), nunca
  dentro de `finetuning/checkpoints/` — solo el adaptador ya elegido
  se trae de vuelta.
- Ajustado `.gitignore`: `finetuning/checkpoints/` chocaba con la
  regla genérica que ignora cualquier carpeta llamada "checkpoints"
  (pensada para checkpoints intermedios, no para este adaptador final
  que sí se quiere versionar) — agregada la excepción de directorio
  correspondiente, verificada con archivos de prueba reales
  (`git add -n`) antes de confiar en ella.
- Actualizado `finetuning/entrenar_lora_colab.ipynb`: dividido en
  Parte A (prueba de humo, sin cambios) y Parte B nueva (entrenamiento
  completo — reutiliza las celdas 1-3 de setup de la Parte A, corre
  `--todos`, y empaqueta/descarga `finetuning/checkpoints/generador1/`).
- **Validación local antes de gastar cómputo de Colab**: corrido
  `entrenar_lora.py --todos --epocas 1` en la máquina local (sin GPU,
  sabiendo que NO se dejaría terminar) solo para confirmar que la
  configuración nueva no tiene errores de arranque — carga del modelo,
  `LoraConfig`, construcción de los datasets de train (189) y val (24),
  y construcción del `Trainer` con `eval_strategy`/`save_strategy`/
  `load_best_model_at_end`/`EarlyStoppingCallback` todo correcto.
  Llegó sin errores hasta el primer paso de entrenamiento (confirmado
  por el log: tamaños de datasets correctos, sin excepciones) antes de
  matarlo manualmente — no tenía sentido dejarlo avanzar en CPU
  (~80-95 min/paso ya documentado en la Sesión 14).

Decisiones tomadas:
- Extender `entrenar_lora.py` en vez de crear `finetuning/entrenar.py`
  (nombre que usaba el prompt original de esta sesión) — mismo
  criterio que la Sesión 15: habría duplicado un pipeline ya probado
  end-to-end en vez de reutilizarlo.
- No intentar completar el entrenamiento real en la máquina local ni
  siquiera parcialmente — la política de `CONTEXTO_PROYECTO.md`
  ("CÓMPUTO PESADO") y la evidencia ya documentada (Sesión 14) son
  concluyentes: esto tiene que correr en Colab.

Pendiente (bloquea el cierre de esta sesión): correr la Parte B de
`finetuning/entrenar_lora_colab.ipynb` en Colab de verdad, traer
`finetuning/checkpoints/generador1/` (adaptador, `loss_log.json`,
`salidas_con_adapter.json`) al repo, confirmar con los datos reales que
la pérdida de validación no sube mientras la de entrenamiento baja (o
documentar en qué época se detuvo si sí pasó), escribir
`finetuning/curva_final_generador1.md`, y completar esta entrada con
cuánto tardó el entrenamiento real y en qué hardware (GPU de Colab
asignada).

## Sesión 19 — 2026-09-11 (2) — Anderson García

Cierre: entrenamiento completo corrido en Colab, con sobreajuste real
detectado y manejado automáticamente.

Qué se hizo:
- **Bug real encontrado al ejecutar**: la celda 2 del notebook clona
  el repo desde GitHub sin especificar rama, así que Colab traía
  `main` — y todo el trabajo de esta sesión (y de varias anteriores)
  vive en `develop`, nunca fusionado a `main`. El primer intento de
  correr `--todos` corrió en silencio la versión vieja del script (sin
  ese flag reconocido de verdad, ejecutó el comportamiento por
  default) porque además la celda 2 solo clona si la carpeta no existe
  — un clon viejo de una corrida anterior en la misma VM de Colab
  nunca se actualiza. Resuelto por el usuario actualizando `main` con
  el contenido de `develop`; pendiente evaluar si conviene que la
  celda de clonado especifique rama explícitamente para no depender de
  que `main` esté al día (queda para una sesión de mejora del
  notebook, no bloqueaba esta).
- Corrido `finetuning/entrenar_lora.py --todos` en Colab (GPU **Tesla
  T4**, 15360MiB VRAM): **189 ejemplos de entrenamiento, 24 de
  validación, ~9 minutos en total**.
- **Sobreajuste real, detectado y manejado automáticamente**: pérdida
  de validación 1.0972 (época 1, mejor) → 1.5414 (época 2, sube) →
  1.5243 (época 3, sigue peor que la época 1) — mientras la pérdida de
  ENTRENAMIENTO siguió bajando sin parar (promedio 0.72 → 0.36 → 0.19
  por época). `EarlyStoppingCallback(patience=2)` agotó la paciencia
  después de la época 3 y detuvo el entrenamiento ahí (no llegó a las
  10 épocas del límite superior); `load_best_model_at_end=True` dejó
  guardado el adaptador de la **época 1** (el de mejor validación), no
  el de la última época entrenada — exactamente el comportamiento
  pedido por el criterio de calidad de esta sesión, sin intervención
  manual.
- **Checkpoint verificado en disco, dos veces**: (1) dentro del propio
  Colab, recargado desde disco justo después de guardarlo, generando
  las 8 traducciones de prueba de siempre; (2) de forma INDEPENDIENTE
  en la máquina local, después de copiar el adaptador al repo —
  `PeftModel.from_pretrained(...)` cargó sin errores, y se probaron 3
  frases dialectales nuevas (fuera de cualquier split) además de las 8
  de `test.json`, las 11 con salidas coherentes, sin texto corrupto ni
  repetido.
- Escrito `finetuning/curva_final_generador1.md`: hardware y tiempo
  real, tabla de pérdida entrenamiento/validación por época, análisis
  del sobreajuste, confirmación de selección del mejor checkpoint, y
  las 11 traducciones de prueba (8 del test set + 3 nuevas) comparadas
  contra la referencia.
- Traídos al repo `finetuning/checkpoints/generador1/` (adaptador
  ~15MB, `loss_log.json` con 567 pasos de entrenamiento + 3 de
  validación, `salidas_con_adapter.json`).

Decisiones tomadas:
- No reentrenar con un `patience` más alto para "forzar" que llegue
  más lejos — el objetivo de esta sesión era confirmar que el
  mecanismo de detección de sobreajuste funciona, y funcionó
  exactamente como se diseñó; forzarlo a entrenar más solo habría
  empeorado la validación sin ganar nada.
- El hallazgo de que el modelo sobreajusta ya desde la época 2 con
  solo 189 ejemplos queda registrado como señal real para priorizar
  ampliar el dataset (más semillas, o los Generadores 2/3) antes de
  seguir ajustando hiperparámetros de LoRA sobre este mismo tamaño.

Pendiente: ninguno específico de esta sesión — los 3 criterios de
aceptación (checkpoint en disco, carga sin errores, traducciones
coherentes en ≥5 ejemplos) y el criterio de calidad (detener en el
mejor checkpoint ante sobreajuste) quedaron cumplidos con evidencia
real. Aparte, queda como mejora futura del notebook de Colab: que la
celda de clonado especifique rama explícitamente en vez de depender
del branch por default del repo.

## Sesión 20 — 2026-09-11 — Anderson García

Comparación honesta: modelo sin ajustar vs. modelo ajustado con LoRA.

Qué se hizo:
- Confirmado que `finetuning/checkpoints/generador1/` existe (Sesión
  19) y que `finetuning/baseline_sin_ajustar.md` (Sesión 13) documenta
  8 ejemplos de línea base — no hizo falta correr nada de nuevo: el
  checkpoint final ya genera sus traducciones de prueba sobre los
  MISMOS 8 ejemplos de `test.json` (`INDICES_MUESTRA`, importado de
  `probar_baseline.py` por ambos scripts), guardadas en
  `finetuning/checkpoints/generador1/salidas_con_adapter.json` desde
  la Sesión 19 — solo faltaba compararlas lado a lado con las del
  baseline, no volver a generarlas.
- Escrito `evaluation/comparacion_base_vs_ajustado.md`: tabla de los 8
  ejemplos (español, referencia, sin ajustar, ajustado) + análisis
  honesto categorizado en 3 grupos, sin maquillar nada:
  - **4 de 8 mejoraron claramente**: los dos casos de "estar remando"
    (modismo de apuro económico, antes traducido literal como
    "rowing", ahora correcto), el caso de "brutal" con connotación
    negativa en inglés (corregido a "awesome"), y una mejora de
    fluidez menor.
  - **2 de 8 NO mejoraron en nada**: el error de "tinto" (café en
    habla andina, mal traducido como vino) persiste exactamente igual
    — la semilla correspondiente está en el split de test, nunca la
    vio el modelo durante el entrenamiento. Dicho explícitamente en el
    documento, sin suavizarlo.
  - **2 de 8 en mejora parcial/ambigua**, uno de ellos con un **error
    NUEVO que el baseline no tenía**: la traducción de "¡Neta! Si eso
    pasa, no lo creo" quedó envuelta en comillas literales en la
    salida (`"Hey, really! ..."`), un artefacto de formato que no
    aparece en ningún otro ejemplo ni en el baseline.
- **Confirmación adicional del sobreajuste** (ya detectado por la
  curva de pérdida en la Sesión 19): los ejemplos #3 y #4 de la tabla
  son dos semillas DISTINTAS ("¿Un tinto, amigo?" vs. "¿Un tinto,
  colega?") y el modelo ajustado dio la MISMA salida exacta para
  ambas — visible aquí como comportamiento concreto, no solo como un
  número de pérdida.

Decisiones tomadas:
- No presentar el resultado como "el modelo mejoró" de forma genérica
  — el prompt pedía explícitamente honestidad si no mejoraba en
  algunos casos, así que el documento cuenta los 8 casos uno por uno
  (4 mejoran, 2 no, 2 ambiguos) en vez de un resumen optimista.
  Reportado también el error nuevo de formato (comillas) sin
  minimizarlo, aunque no afecta la inteligibilidad de esa traducción.
- No se generaron traducciones nuevas ni se corrió el modelo de nuevo
  — reutilizar las salidas ya generadas y guardadas en la Sesión 19
  evita cómputo redundante y usa exactamente los mismos ejemplos que
  pedía el prompt para la comparación directa.

Pendiente: ninguno específico de esta sesión — los criterios de
aceptación (tabla existe, cubre los mismos ejemplos del baseline,
permite comparación directa antes/después) están cumplidos. El
pendiente de fondo (ampliar el dataset antes de seguir ajustando
hiperparámetros) sigue siendo el mismo de la Sesión 19, reforzado aquí
con evidencia concreta de sobreajuste (dos semillas colapsando a la
misma salida).

## Sesión extra — 2026-09-17 — Paula Lozano

Respuesta directa a la retroalimentación del profesor sobre la Fase 1
+ requisito de "governance model" del syllabus para el Project Advance
2 (entrega en ~15 días, coincide con el cierre de nuestra Fase 2,
Sesión 36). No corresponde a ningún número del calendario de 60
sesiones — es trabajo nuevo motivado por una entrega externa, igual
que la Sesión 14 (4) de Anderson.

Qué se hizo:
- Auditoría completa del repo contra los 4 puntos de la
  retroalimentación del profesor: presupuesto de tiempo/cómputo
  (pendiente desde la Sesión 1, que nunca se ejecutó — no existe
  ningún `.tex` en este repositorio, el paper vive en Overleaf),
  alcance dialectal declarado desde el inicio (creció de forma
  incidental, nunca se declaró como decisión de alcance), validación
  de datos sintéticos (ya bien cubierta, Sesiones 10-11) y conjunto de
  prueba independiente (ya bien resuelto por diseño, Sesión 12).
- Detectado que "governance model", que el syllabus pide
  explícitamente para el Project Advance 2, no tenía ninguna sesión
  asignada en el calendario interno de 60 sesiones — se trata como
  trabajo nuevo, no como algo ya en curso que se retrasó.
- Escrito `docs/presupuesto_tiempo_computo.md`: 5-8h/semana por
  integrante (dato real dado por el equipo, no inventado), ninguna
  máquina del equipo con GPU utilizable (ya confirmado en la práctica,
  Sesión 13-14), todo el cómputo pesado en Colab gratuito, costo total
  de cómputo del proyecto a la fecha: $0.
- Escrito `docs/alcance_banco_semillas.md`: declara formalmente los 5
  dialectos cubiertos (Caribeña, Andina, Rioplatense, Mexicana,
  Chilena) y los tipos de expresión, con la justificación de por qué
  esos 5 y no otros, y declarando explícitamente como limitación
  conocida los dialectos NO cubiertos (español peninsular, Caribe
  insular) — honesto sobre que la cobertura creció de forma
  incremental (Sesiones 4 y 9) en vez de decidirse toda de una vez.
- Escrito `docs/modelo_gobernanza.md`: roles y decisiones del equipo
  (quién es dueño de qué área), gobernanza de datos (qué se versiona,
  qué nunca se persiste en producción), gobernanza de modelos
  (versionado de adaptadores, criterio de checkpoint final, cuándo
  re-entrenar), gobernanza de proceso/código (git hook, Conventional
  Commits, política de Colab, `CLAUDE.md`) y riesgos éticos.
- Actualizado `docs/fase2_arquitectura_borrador.md` (que se había
  quedado en la Sesión 18, antes del entrenamiento completo): agregada
  la sección de resultados del entrenamiento completo con validación
  (Sesión 19), el sobreajuste real detectado y manejado, la
  comparación honesta contra la línea base (Sesión 20), una
  explicación explícita de por qué el split de prueba es
  genuinamente independiente (con el caso de "tinto" como evidencia
  empírica de que no hay fuga de datos), una hoja de ruta a 15 días, y
  referencias cruzadas a los 3 documentos nuevos de arriba.
- Actualizado `docs/README.md` para listar los 3 documentos nuevos.

Decisiones tomadas:
- No se inventó el número de horas/semana ni se asumió acceso a GPU
  paga — se preguntó directamente al equipo antes de escribir
  `presupuesto_tiempo_computo.md`, siguiendo la misma política de no
  inventar datos que rige el resto del proyecto.
- El alcance dialectal se declara "cerrado" de aquí en adelante
  (`docs/alcance_banco_semillas.md`): ampliarlo requiere una decisión
  explícita documentada en `BITACORA.md`, no debe volver a crecer de
  forma incidental dentro de otra sesión.
- Se prioriza, con acuerdo del equipo, enfocar los próximos 15 días en
  lo que exige la entrega (API mínima, containerización, seguridad,
  observabilidad, evaluación automática/humana, compilación del paper)
  por encima de seguir al pie de la letra cada prompt del calendario
  original si el tiempo aprieta — ver hoja de ruta en
  `docs/fase2_arquitectura_borrador.md` §8.5.

Pendiente: integrar estos 4 documentos nuevos al `.tex` real en
Overleaf (pendiente de acceso — el link compartido pedía login y la
extensión de navegador del equipo no estaba disponible en esta
máquina; se le pidió al equipo exportar el `.zip` del proyecto como
alternativa). Seguir con las Sesiones 21 en adelante (evaluación
automática) priorizando lo que exige la entrega, según la hoja de ruta
de arriba.

## Sesión 1 (por fin) — 2026-09-17 — Paula Lozano

El equipo compartió el `.tex` real del paper de Fase 1 (vivía solo en
Overleaf, nunca en este repositorio) para poder avanzar en la entrega
de Fase 2. Al revisarlo, los 5 problemas que la Sesión 1 original
(Anderson, Semana 1) debía corregir **seguían ahí, intactos** — esa
sesión nunca se ejecutó de verdad. Se corrige ahora, con los datos
reales que faltaban.

Qué se hizo:
- Traído el `.tex` al repositorio (`paper/main.tex` +
  `paper/README.md`) — antes era el único artefacto del proyecto sin
  control de versiones ni trazabilidad en `BITACORA.md`.
- **Presupuesto de tiempo/cómputo**: reemplazado el placeholder
  `[completar: ...]` con las cifras reales confirmadas con el equipo
  (5-8h/semana por integrante, ninguna máquina con GPU utilizable,
  todo el cómputo pesado en Colab gratuito) — mismos datos que
  `docs/presupuesto_tiempo_computo.md`.
- **Las 4 oraciones que perdieron los guiones largos**: corregidas,
  restaurando los incisos con `—` donde se habían vuelto oraciones
  corridas (Sección 1.2 "Tampoco faltan herramientas de nicho...",
  Sección 1.2 "Ninguno de los dos extremos...", Sección 1.3 "Es un
  problema de otra naturaleza...", Sección 3.1 "...ninguno de estos
  trabajos propone una solución de fine-tuning...").
- **Etiqueta "(Path A)"/"(Path B)"**: revisado el documento completo —
  esa etiqueta no existe en ninguna parte del `.tex` real, la sección
  de preguntas de investigación nunca la tuvo. No se inventó ni se
  forzó su inserción donde no encaja con el contenido real; se deja
  constancia aquí de que este punto específico de la Sesión 1 original
  no aplica a este documento tal como existe.
- **Resumen (abstract)**: agregada una oración que anticipa la
  distinción entre pregunta de investigación y propuesta de producto,
  antes de que el cuerpo del documento la desarrolle en la Sección 4.2.
- **Sección de Contribuciones**: no reflejaba ni la extensión a
  lenguas indígenas (sí mencionada en el cuerpo, Sección 2.3) ni la
  propuesta de producto (Tabla 2, Sección 4.2) — agregados dos puntos
  nuevos a la lista de contribuciones cubriendo ambos.
- Verificado que ninguna cita nueva se agregó sin existir ya en la
  bibliografía (no se tocaron citas, solo prosa).

Decisiones tomadas:
- El `.tex` pasa a vivir en `paper/main.tex` dentro del repositorio,
  no solo en Overleaf — la sincronización entre ambos por ahora es
  manual (copiar/pegar); se deja anotado en `paper/README.md` que
  integrar Overleaf con Git eliminaría esta fricción, sin hacerlo
  todavía por no ser parte de esta entrega.
- Se versiona `main.pdf` (no solo `main.tex`) como evidencia de
  compilación limpia en el momento del commit; los artefactos
  intermedios (`.aux`, `.log`, `.out`) se ignoran vía `.gitignore`.

Pendiente: sincronizar estos cambios de vuelta a Overleaf (pegar el
contenido corregido de `paper/main.tex`) para que el resto del equipo
seguir editando ahí no sobrescriba estas correcciones sin darse cuenta.
Falta también integrar al `.tex` los documentos nuevos de Fase 2
(`docs/fase2_arquitectura_borrador.md`, `docs/alcance_banco_semillas.md`,
`docs/modelo_gobernanza.md`, `docs/presupuesto_tiempo_computo.md` ya
integrado en el cuerpo) como nuevas secciones, planeado para más
adelante en esta misma fase, no en esta sesión puntual.

Pruebas de aceptación verificadas:
- `pdflatex -interaction=nonstopmode main.tex` corrido dos veces
  seguidas, exit code 0 ambas veces, 0 "Overfull hbox" (`grep -ic
  overfull` = 0), 13 páginas.
- Búsqueda de `[completar` en el archivo: sin resultados.
- Búsqueda de "Path A"/"Path B": sin resultados en el documento real
  (ver nota arriba, no aplica a este `.tex`).
- Lectura del resumen: menciona explícitamente la distinción
  investigación/producto.

## Sesión 21 — 2026-09-17 — Paula Lozano

Implementar métricas automáticas (BLEU, chrF).

Qué se hizo:
- Escrito `evaluation/metricas_automaticas.py`: recibe un archivo de
  predicciones y uno de referencias (mismo formato que `test.json`)
  por parámetro de línea de comandos (`--predicciones`,
  `--referencias`, `--campo-prediccion` configurable, `--salida`
  opcional) — nada hardcodeado, reutilizable con cualquier generador o
  checkpoint futuro sin tocar el código. Empareja predicción con
  referencia por `texto_dialectal` exacto (no por `seed_id`, que no es
  único porque cada semilla tiene varias variantes), reportando
  cuántas predicciones quedaron sin referencia en vez de fallar en
  silencio. Calcula BLEU y chrF (`sacrebleu`) global y desglosado por
  dialecto.
- Instalado `sacrebleu` de forma aislada (ya estaba en
  `requirements.txt`) — es cómputo de texto puro, sin GPU, así que no
  aplica la política de Colab-únicamente (esa es para entrenamiento/
  inferencia con el modelo, no para calcular una métrica de texto).
- Corrido sobre las predicciones reales del modelo ajustado con LoRA
  (`finetuning/checkpoints/generador1/salidas_con_adapter.json`,
  Sesión 19-20) contra `generation/splits/dataset_generador1/test.json`:
  reporte generado sin errores, BLEU 47.21 / chrF 59.71 global, con
  desglose por dialecto (`evaluation/reporte_metricas_generador1.md`).
- Aprovechando que el script es genérico, corrido también sobre las
  predicciones de la línea base sin ajustar
  (`finetuning/baseline_sin_ajustar_salidas.json`, campo distinto vía
  `--campo-prediccion traduccion_modelo_sin_ajustar`): BLEU 38.18 /
  chrF 48.33 global (`evaluation/reporte_metricas_baseline.md`) — la
  primera comparación **cuantitativa** entre ambos modelos del
  proyecto (antes solo había comparación cualitativa, Sesión 20).
- Agregada esta comparación a `evaluation/comparacion_base_vs_ajustado.md`
  (que ya tenía la comparación cualitativa) en vez de crear un
  documento aparte, para que quede una sola fuente de verdad sobre
  "cómo le fue al modelo ajustado frente al base".

Hallazgo que no se maquilla: la mejora global es clara (+9.03 BLEU,
+11.38 chrF), pero el desglose por dialecto no es parejo — Andina y
Rioplatense mejoran mucho, pero **Mexicana empeora en BLEU** (63.66 →
55.12) pese a mejorar levemente en chrF. Con solo 2 ejemplos por
dialecto en esta muestra, es más probable que sea ruido estadístico
que una señal real de que el ajuste perjudica ese dialecto, pero se
documenta la cifra tal cual, sin la conclusión de "es solo ruido" sin
evidencia que la respalde.

Decisiones tomadas:
- El emparejamiento es por `texto_dialectal`, no por `seed_id` —
  decisión de diseño necesaria porque el prompt original solo mencionó
  "mismo formato que test.json" sin especificar la llave, y `seed_id`
  no identifica una variante única.
- No se generaron predicciones nuevas para cerrar la cobertura del
  `test.json` completo (23 ejemplos) — estas métricas corren solo
  sobre los 8 ejemplos que ya tenían predicción de antes (35% del
  test set). Generar las 15 restantes es solo inferencia (mucho más
  barato que entrenar), pero de todas formas requiere cargar el modelo
  de 3B con el adaptador, así que sigue la política de Colab del
  proyecto — no se hizo en esta sesión para no bloquear el resto del
  flujo, queda documentado como pendiente explícito, no oculto.

Pruebas de aceptación verificadas: el script corrió sobre el `test.json`
del Generador 1 usando las predicciones del modelo ajustado, produjo
un reporte con BLEU y chrF global y por dialecto, sin errores.

Pendiente: generar predicciones del modelo ajustado sobre los 15
ejemplos restantes de `test.json` (inferencia en Colab) para tener
BLEU/chrF representativos del test set completo antes de reportar
estas cifras como definitivas en el paper. Seguir con la Sesión 22
(reclutar hablantes nativos evaluadores).

## Sesión 22 — 2026-09-17 — Paula Lozano

Reclutar hablantes nativos evaluadores. Creados
`evaluation/reclutamiento_evaluadores.md` (mensaje de reclutamiento +
formulario de filtro que evita "¿de dónde eres?" ambiguo, preguntando
específicamente dónde creció y qué variante habla a diario) y
`evaluation/evaluadores.csv` (plantilla de seguimiento, objetivo 3 por
cada uno de los 5 dialectos = 15 mínimo).

**No se pobló el CSV con contactos reales ni de ejemplo** — contactar
gente de verdad es una acción humana que el equipo tiene que hacer
fuera del repositorio; inventar filas ahí rompería la trazabilidad real
de quién evaluó qué en la Sesión 24. Pendiente: que el equipo contacte
gente real y llene el CSV a medida que confirmen.

## Sesión 23 — 2026-09-17 — Mariana Malagón

Diseñar rúbrica de evaluación humana. Creado
`evaluation/rubrica_humana.md`: escala 1-5 de retención de matices con
definición explícita de cada punto, instrucciones para el evaluador, y
3 ejemplos de calibración tomados de datos reales del proyecto
(`evaluation/comparacion_base_vs_ajustado.md`), incluyendo el caso ya
conocido de "tinto" (calificado 1, significado invertido).

Pendiente: la calibración cruzada entre dos personas del equipo
(criterio de aceptación del prompt original) todavía no se hizo —
requiere que dos personas califiquen los mismos 5 ejemplos por
separado, algo que no puedo simular yo solo sin inventar una segunda
opinión falsa. Queda para el equipo antes de la Sesión 24.

## Sesión 25 — 2026-09-17 — Anderson García

Construir wrapper de API REST (FastAPI).

Qué se hizo:
- Escrito `api/main.py`: `POST /traducir` (texto + dialecto opcional
  → traducción) y `GET /salud`. El modelo se carga una sola vez al
  iniciar el servicio (`lifespan` de FastAPI), no por solicitud.
  Reutiliza `cargar_modelo`/`traducir` de `finetuning/probar_baseline.py`
  (ya validadas en las Sesiones 13/19-20) más el adaptador LoRA del
  Generador 1 (`finetuning/checkpoints/generador1/adapter/`) vía
  `PeftModel.from_pretrained`.
- Los imports pesados (`torch`, `transformers`, `peft`) quedan
  DENTRO de la función de carga, no al inicio del módulo — así el
  archivo se puede importar y probar sin esas dependencias instaladas.
  Con `SKIP_MODEL_LOAD=1` el servicio arranca sin cargar el modelo
  real, exclusivamente para pruebas de la capa de API.
- Escrito `api/test_main.py` (7 pruebas, con `TestClient` y el modelo
  mockeado): `/salud` responde 200; `/traducir` sin modelo cargado
  responde 503; con el modelo mockeado responde 200 con la forma
  correcta; texto vacío o solo espacios se rechaza (400); texto de más
  de 500 caracteres o sin el campo `texto` se rechaza (422). **Las 7
  pasan.**
- `api/README.md` con ambos flujos (levantar con modelo real vs.
  correr las pruebas sin él). Agregados `pytest` y `httpx` a
  `requirements.txt` (no estaban).

Decisiones tomadas:
- **No se pudo cumplir el criterio de aceptación completo del prompt
  original** ("hacer una solicitud real con curl... confirmar que
  devuelve una traducción coherente en pocos segundos") — esta máquina
  no tiene `torch`/`peft` instalados ni GPU, y descargar+cargar el
  modelo de 3B contradice la política de cómputo del proyecto
  (Colab/despliegue, no local). Se optó por probar exhaustivamente la
  CAPA de API con el modelo mockeado (que sí es 100% real y pasa), y
  dejar la prueba con el modelo real explícitamente pendiente para
  Colab o el entorno de despliegue (Sesión 26) — no se fingió una
  traducción de ejemplo para simular que sí se probó.
- Se agregó validación básica de longitud (500 caracteres) y de texto
  vacío ya en esta sesión, adelantando una porción pequeña de la
  Sesión 28 (seguridad), porque era prácticamente gratis con Pydantic
  y evita que la Sesión 28 tenga que tocar el modelo de datos desde
  cero. El resto de la Sesión 28 (rate limiting, garantías de no
  persistencia) sigue sin hacer.

Pruebas de aceptación: `SKIP_MODEL_LOAD=1 python -m pytest api/test_main.py -v`
→ 7 passed. Pendiente (no cumplido en esta sesión): levantar el
servicio con el modelo real y confirmar con `curl` una traducción
coherente — requiere Colab o el entorno de despliegue.

Pendiente: Sesión 26 (despliegue en la nube — requiere que alguien del
equipo cree una cuenta en la plataforma elegida, no es algo que se
pueda hacer sin esa decisión/acceso humano) y completar la Sesión 28
(rate limiting, garantía de no persistencia).

## Sesión 25 — 2026-09-17 (2) — Anderson García

Cierre de la prueba de aceptación pendiente: sí se pudo levantar el
servicio localmente con el modelo real.

Contexto: la Sesión 25 (arriba) asumió que esta máquina "no tiene
`torch`/`peft` instalados ni GPU" y difirió la prueba completa a
Colab/despliegue. Al retomar la tarea, confirmado que `torch`,
`transformers`, `peft`, `fastapi` y `uvicorn` **sí están instalados**
en el entorno local (mismo `.venv` usado en las Sesiones 13-20 para
probar el baseline y el LoRA) — la premisa de la Sesión 25 era
incorrecta, o el entorno cambió desde entonces. Con eso, sí se pudo
correr la prueba real pendiente.

Qué se hizo:
- Levantado `uvicorn api.main:app` localmente con el modelo real (sin
  `SKIP_MODEL_LOAD`) — el adaptador de `finetuning/checkpoints/generador1/`
  cargó sin errores.
- `GET /salud` → `200 {"estado":"ok"}` en ~7ms.
- `POST /traducir` con `"Que chimba, parcero!"` (dialecto "Andina") →
  `200 {"traduccion":"That's awesome, buddy!","dialecto":"Andina"}`
  en **79.4s**. Traducción correcta y coherente.
- Segunda solicitud (`"No manches, esta bien bacano."`) → `200
  {"traduccion":"No way, this is really cool."}` en **49.8s** — más
  rápida que la primera (sin costo de arranque en frío) pero
  igualmente lejos del objetivo.
- Corridas también las 7 pruebas de la capa de API
  (`SKIP_MODEL_LOAD=1 python -m pytest api/test_main.py -v`): siguen
  pasando las 7, sin cambios de comportamiento.
- Actualizados `api/main.py` (docstring) y `api/README.md` con los
  números reales medidos, reemplazando la afirmación de que la prueba
  "no se pudo hacer en esta máquina".

**Resultado honesto — funciona pero NO cumple el criterio de
latencia**: las traducciones son correctas y coherentes en las dos
solicitudes probadas, y `/salud` responde 200 casi instantáneo. Pero
`/traducir` tardó 50-80 segundos por solicitud en CPU local, muy por
encima de "unos pocos segundos" que pedía el criterio de aceptación
original. No se maquilla este resultado como un éxito completo: es un
**éxito funcional, no de latencia**. Cumplir la latencia objetivo
necesita GPU — consistente con la política de cómputo pesado del
proyecto y con todo lo ya documentado sobre esta misma máquina
(Sesiones 13/14/19).

Decisiones tomadas:
- No declarar cumplido el criterio de "unos pocos segundos" solo
  porque la solicitud sí terminó — el criterio es explícito sobre el
  tiempo, y 50-80s no lo cumple bajo ningún criterio razonable. Se deja
  registrado como hallazgo real, no como un pendiente sin evidencia.
- No repetir esta misma prueba en Colab en esta sesión — el objetivo
  era cerrar la prueba LOCAL que había quedado pendiente (eso ya se
  hizo, con resultado real). Medir la latencia real en GPU queda para
  cuando se levante el servicio de verdad en el entorno de despliegue
  (Sesión 26), que es además el número donde ya se documentó este
  pendiente.

Pruebas de aceptación (revisadas): el checkpoint carga sin errores
✅; `/salud` responde 200 ✅; `/traducir` devuelve una traducción
coherente ✅; "en menos de unos pocos segundos" ❌ en CPU local (50-80s)
— cumplido functionalmente, no en latencia.

Pendiente: medir la latencia real de `/traducir` con GPU (Colab o el
entorno de despliegue de la Sesión 26) para confirmar si ahí sí se
cumple el objetivo de "unos pocos segundos" — probablemente sí, dado
que las generaciones individuales en Colab durante las Sesiones 14/19
fueron notablemente más rápidas que en CPU, pero no se midió un
número exacto todavía.

## Sesión 26 — 2026-09-17 — Anderson García

Elegir plataforma de despliegue y preparar el servicio (EN CURSO —
falta que alguien del equipo cree el Space de verdad y se corra la
prueba de aceptación desde otra máquina).

Qué se hizo:
- **Investigadas las 3 plataformas sugeridas contra el tamaño real
  del modelo (~6.5GB en memoria)**, con búsquedas web para confirmar
  límites vigentes en 2026 (no de memoria):
  - **Render**: free tier de 512MB RAM — descartado, ni de cerca
    alcanza.
  - **Railway**: ya no tiene free tier permanente — trial único de $5
    (30 días, 1GB RAM), después baja a 0.5GB RAM — descartado, no
    alcanza y no es sostenible.
  - **Hugging Face Spaces con SDK Docker** (lo que habría hospedado
    `api/main.py`/FastAPI tal cual): el hardware "CPU Basic" (16GB
    RAM) sigue siendo gratis, pero **crear un Space con SDK Docker
    pasó a requerir plan PRO de pago en 2026** (cambio de política de
    HF, confirmado en la documentación oficial) — descartado para
    mantenerse gratis.
  - **Hugging Face Spaces con SDK Gradio + hardware ZeroGPU**: cuentas
    personales gratuitas (correo verificado, +30 días de antigüedad)
    pueden alojar hasta 2 Spaces gratis, con GPU real asignada solo
    durante cada generación. Cuota diaria: 5 min/día autenticado, 2
    min/día sin autenticar — de sobra para pruebas puntuales, sin
    ningún cobro si se agota (solo cola hasta el otro día). **Elegida**
    — de paso resuelve la latencia de 50-80s en CPU (Sesión 25).
  - **También evaluado, a pedido del usuario: AWS Academy Learner
    Lab** (ya tiene acceso). Descartado tras confirmar dos datos
    reales con el usuario: la sesión del lab se apaga sola a los **40
    minutos** (necesitaría reactivación manual constante, incompatible
    con "servicio disponible para probar en cualquier momento desde
    otra máquina"), y los **$48 de crédito restantes se comparten con
    el resto de la materia** (no conviene arriesgarlos en esto).
- Escrito `api/space/app.py`: reescritura del mismo servicio como app
  de Gradio (no FastAPI) — reutiliza el mismo `SYSTEM_PROMPT` y formato
  de prompt que `probar_baseline.py`/`api/main.py`, sin reinventar
  nada. Requisito técnico de ZeroGPU cumplido: el modelo se carga a
  nivel de módulo (no dentro de una función), y solo la función de
  generación lleva `@spaces.GPU`. Expone `traducir(texto, dialecto)` y
  `salud()` como funciones de la API de Gradio (`api_name`).
- Copiado el adaptador (`finetuning/checkpoints/generador1/adapter/`)
  a `api/space/adapter/` para que la carpeta del Space sea
  autocontenida (lo que se sube a HF es exactamente `api/space/`, sin
  arrastrar el resto del proyecto).
- **Verificado localmente antes de desplegar** (sin GPU real — el
  decorador `@spaces.GPU` es un no-op fuera de un Space, documentado
  así oficialmente): levantada la app con `python api/space/app.py`,
  probados ambos endpoints con `gradio_client` Y con `curl` puro
  (confirmado el patrón de dos pasos que usa la API HTTP de Gradio:
  `POST /gradio_api/call/<nombre>` devuelve un `event_id`, y
  `GET /gradio_api/call/<nombre>/<event_id>` da el resultado). `salud`
  → `"ok"` en ~1.6s; `traducir("Que chimba, parcero!")` →
  `"That's awesome, buddy!"` en 68s (consistente con los 50-80s ya
  medidos para el FastAPI en CPU local — confirma que corre en CPU
  sin GPU real, como se esperaba fuera de un Space de verdad).
- No se encontró ninguna clave/credencial escrita en el código de
  `api/space/` — el modelo base es público, no hace falta `HF_TOKEN`
  para que funcione. Documentado en `docs/despliegue.md` cómo se
  configuraría un secreto vía la UI de Settings de HF si hiciera falta
  en el futuro (ej. al cambiar a Llama 3.2, que sí lo necesita).
- Escrito `docs/despliegue.md`: paso a paso completo (crear el Space,
  subir el código por UI o por git, activar ZeroGPU, variables de
  entorno, esperar el build, comandos exactos de `curl` para probar
  ambos endpoints, cómo redesplegar si algo falla).

Decisiones tomadas:
- Reescribir como Gradio en vez de pagar HF PRO para mantener FastAPI
  — el objetivo explícito era una plataforma accesible con capa
  gratuita para un equipo de estudiantes; pagar contradice eso.
  `api/main.py` (FastAPI) se deja intacto en el repo como el servicio
  de referencia/desarrollo local; `api/space/app.py` es la variante de
  despliegue.
- Duplicar el adaptador (~15MB) en vez de referenciarlo por ruta
  relativa cruzada — simplicidad: lo que se sube al Space es
  exactamente esa carpeta autocontenida, sin depender de la estructura
  del resto del repo.
- No crear el Space real en esta sesión — requiere la cuenta de HF de
  un integrante del equipo (con correo verificado y +30 días de
  antigüedad) y es una acción que le corresponde a una persona, no
  algo que se deba automatizar sin su decisión explícita.

Pruebas de aceptación (parcial): el código funciona de punta a punta
localmente (probado con `curl` real, no solo unitarios) ✅; sin claves
en el código ✅; documentación paso a paso completa ✅. **Falta la
prueba real** (crear el Space con una cuenta del equipo, y correr
`curl` contra la URL pública desde una máquina distinta a la que
despliega) — no se puede simular sin ese acceso humano.

Pendiente: crear el Space en Hugging Face con la cuenta de un
integrante del equipo, confirmar que ZeroGPU está activo, correr la
prueba de aceptación real desde otra máquina, y completar
`docs/despliegue.md` con la URL pública y el resultado medido
(traducción + tiempo de respuesta real en GPU).

## Sesión 26 — 2026-09-17 (2) — Anderson García

Qué se hizo: bug encontrado inmediatamente después del commit
anterior: la
excepción de `.gitignore` para adaptadores LoRA
(`!finetuning/**/adapter/*.safetensors`) estaba acotada a la carpeta
`finetuning/` — `api/space/adapter/adapter_model.safetensors` (los
pesos reales del adaptador que se sube al Space) quedó **fuera del
commit** sin que `git commit` avisara nada raro (el archivo
simplemente nunca se agregó a `git add`, sin error visible).
Descubierto al revisar el resumen del commit y notar que
`adapter_model.safetensors` no aparecía en la lista de archivos
creados. Corregido generalizando el patrón a `!**/adapter/*.safetensors`
/ `!**/adapter/*.bin` (sin acotar a una carpeta), y confirmado con
`git status` que el archivo ahora sí queda staged.

Pendiente (sin cambios): el mismo de la entrada anterior.

## Sesión 26 — 2026-09-18 — Anderson García

Bloqueo real encontrado al intentar crear el Space de verdad: la
elegibilidad de la excepción gratuita de ZeroGPU es más estricta en la
práctica que lo que sugería la documentación de HF (que hablaba de
"cuentas personales gratuitas en buen estado" sin más detalle
visible). En la pantalla real de creación de Space
(`huggingface.co/new-space`), tanto Gradio como Docker aparecen
bloqueados de una con un badge "Paid" — no hay ninguna opción de
elegir ZeroGPU específicamente en ese paso para evitar el bloqueo,
contrario a lo que se esperaba tras leer la documentación.

Qué se hizo:
- Verificado en la práctica (captura de pantalla real del usuario en
  `huggingface.co/new-space`): SDK Gradio y Docker muestran "Paid" de
  entrada; el mensaje exacto es *"Gradio and Docker Spaces require a
  paid plan / Static Spaces stay free for everyone. To create a Space
  that runs on compute, subscribe to PRO."* — sin mención de la
  excepción de ZeroGPU en esa pantalla.
- Investigado un hilo de la comunidad de HF
  (discuss.huggingface.co) que confirma que el mensaje real dice
  específicamente *"hosting Gradio and Docker Spaces on free
  **cpu-basic** requires a PRO subscription"* — no hay confirmación
  pública de un flujo alternativo para activar la excepción de
  ZeroGPU directamente desde el asistente de creación.
- Descartada la hipótesis de que el bloqueo fuera por el SDK en sí:
  confirmado con el usuario que su cuenta de HF **sí tiene el correo
  verificado** (`huggingface.co/settings/account`) — un requisito
  cumplido.
- **Causa real confirmada**: la cuenta se creó el **2026-09-02**
  (Sesión 13, para el intento de acceso a Llama 3.2) — a fecha de hoy
  (2026-09-18) tiene **16 días**, por debajo del requisito de **+30
  días** que pide Hugging Face para la excepción gratuita de ZeroGPU
  en cuentas personales. Es la causa más probable del bloqueo (aunque
  no se pudo confirmar 100% que desaparezca automáticamente al cumplir
  los 30 días, dado que la pantalla de creación tampoco mostró la
  excepción explícitamente en ningún punto).

Decisiones tomadas (con el usuario):
- **No usar la cuenta de otro integrante del equipo** para saltarse la
  espera — se prefirió esperar con la cuenta propia.
- **No bloquear el resto del proyecto por esto**: seguir avanzando en
  otras sesiones mientras se cumple la antigüedad de cuenta, y retomar
  el despliegue real cuando la cuenta cumpla 30 días
  (**~2026-10-02**).
- Todo el código y la documentación de despliegue (`api/space/`,
  `docs/despliegue.md`) ya están listos y no necesitan ningún cambio
  para cuando se retome — el único bloqueo es la elegibilidad de la
  cuenta, no el trabajo técnico.

Pendiente: retomar el despliegue real a partir de **2026-10-02**
(cuando la cuenta de HF cumpla 30 días) — crear el Space, confirmar
que ya no aparece el bloqueo de "Paid" con ZeroGPU seleccionado,
subir `api/space/`, y correr la prueba de aceptación real desde otra
máquina. Si para entonces sigue bloqueado pese a los 30 días,
contactar soporte de HF o usar la cuenta de otro integrante del equipo
como plan B.

## Sesión 27 — 2026-09-18 — Anderson García

Contenerizar el servicio de la API (Docker/Podman) — cerrada con
evidencia real, tras un diagnóstico largo de un crash reproducible.

Contexto: Docker Desktop no se pudo instalar en esta máquina (error de
instalación); se usó **Podman** como alternativa, con `podman machine`
corriendo una VM Linux sobre WSL2 en Windows.

Qué se hizo:
- Escrito `Dockerfile` (imagen `python:3.11-slim`, sin dependencias
  del sistema operativo — todo instala desde wheels precompilados),
  `docker-compose.yml`, `.dockerignore`, y `api/requirements.txt`
  (dependencias puntuales del servicio, no el `requirements.txt`
  completo del proyecto — mismo criterio ya usado en
  `entrenar_lora_colab.ipynb` y `api/space/requirements.txt`).
  `COPY` explícito y puntual (no `COPY . .`) de solo lo que el
  servicio necesita: `api/main.py`, `finetuning/probar_baseline.py`,
  y el adaptador de `finetuning/checkpoints/generador1/adapter/`.
- **Bug real #1 — `podman-compose` en Windows ignora el campo
  `dockerfile:`**: con `Dockerfile`/`docker-compose.yml` dentro de
  `api/` y `context: ..` + `dockerfile: api/Dockerfile`, `podman-compose
  --verbose` mostró que el comando de build generado ni siquiera
  incluía el flag `-f` — construía buscando un Dockerfile en la raíz
  del contexto (donde no está) y fallaba. Confirmado que es un bug de
  la herramienta (no de la config: `podman-compose config` sí
  mostraba la ruta resuelta correctamente, solo el build real la
  ignoraba). Resuelto moviendo `Dockerfile` y `docker-compose.yml` a
  la **raíz del repo** (contexto = mismo directorio, sin necesitar ese
  campo).
- **Bug real #2 — reenvío de puertos de Podman/gvproxy en Windows**:
  con el contenedor corriendo y `podman port` mostrando
  `0.0.0.0:8000->8000/tcp` correctamente, `curl http://127.0.0.1:8000/...`
  y `curl http://localhost:8000/...` fallaban con conexión rechazada.
  Diagnosticado con `netstat`: Windows solo tenía el puerto escuchando
  en `[::1]:8000` (IPv6 loopback), no en IPv4; probar directo por
  `[::1]` tampoco respondió de forma confiable. **Workaround real que
  sí funcionó siempre**: pegarle a la IP propia de la VM de Podman
  (`podman machine ssh podman-machine-default "ip -4 addr show eth0"`),
  no a `localhost`.
- **Bug real #3 (el más largo de diagnosticar) — crash de glibc**:
  el primer `build` + `run` funcionó perfecto (confirmado con `curl`
  real: `/salud` 200, `/traducir` con traducción correcta). Los
  intentos siguientes (probar `docker-compose`, y luego varios
  reintentos) empezaron a fallar con
  `Fatal glibc error: malloc.c:2601 (sysmalloc): assertion failed`,
  el proceso terminando con código 139 (SIGSEGV). Descartadas, en
  orden, con evidencia real antes de encontrar la causa real:
  - Corrupción del volumen de caché por haberlo copiado entre
    volúmenes con un contenedor `alpine` intermedio — descartado: un
    volumen **nunca antes usado**, con una descarga 100% limpia,
    también crasheó.
  - Memoria insuficiente en la VM de Podman/Windows — descartado:
    cerrar aplicaciones para liberar RAM (de ~8GB a ~9.5GB libres) no
    cambió nada; la VM siempre reportó suficiente memoria disponible
    (`free -h`) al momento del crash.
  - Inestabilidad acumulada de la VM tras varias horas de uso —
    parcialmente cierto (se encontró un error real de `binfmt_misc` en
    el filesystem de la VM), pero un `podman machine stop`+`start` no
    lo resolvió por sí solo.
  - Espacio en disco — descartado: 948GB libres de 1TB en la VM en
    todo momento.
  - **Causa real, aislada con un contenedor mínimo** (`python -c
    "import torch"`, sin nuestro código ni el modelo): el crash
    ocurre en el simple `import torch`. `api/requirements.txt` tenía
    `torch>=2.3.0` (sin techo), que resolvía a la versión más nueva
    disponible al momento de esta sesión, **2.14.0+cpu** — esa versión
    específica crashea con este error de glibc en esta imagen base
    (`python:3.11-slim`) sobre Podman/WSL2/Windows. **Fijado
    `torch==2.13.0`** en `api/requirements.txt` (la misma versión ya
    usada con éxito en toda la máquina local durante el resto del
    proyecto, no una versión elegida al azar) — el `import torch`
    mínimo pasó a funcionar de inmediato.
  - Para descartar cualquier duda de inestabilidad remanente de la VM,
    se recreó por completo (`podman machine rm` + `init` + `start`,
    decisión tomada con el usuario tras explicarle que esto borra
    todas las imágenes/volúmenes de Podman, no los archivos del
    proyecto) antes de la corrida final.
- **Prueba de aceptación real, con el fix aplicado y la VM recreada**:
  `podman build` sin errores; contenedor levantado con `podman run`
  → `GET /salud` → `200 {"estado":"ok"}` en ~36ms; `POST /traducir`
  con `"Que nota, marica, quedo bacano!"` → `200 {"traduccion":"What a
  note, dude, it turned out cool!",...}` en 33.8s, coherente, sin
  texto corrupto ni repetido. Repetido con `docker-compose up` (vía
  `python -m podman_compose`, ya que `podman compose` nativo no
  encontró proveedor instalado en esta máquina) → mismo resultado,
  `/salud` 200.
- Documentado todo en `api/README.md` (sección nueva "Contenedor
  (Docker / Podman)": build, run, compose, y los 3 problemas reales
  con sus soluciones) y corregida una referencia de sesión mal
  etiquetada que había quedado de la Sesión 25 (decía "Sesión 27" por
  error).

Decisiones tomadas:
- Mover `Dockerfile`/`docker-compose.yml` a la raíz del repo en vez de
  dentro de `api/` — cambio de plan respecto al diseño inicial, pero
  necesario para sortear el bug real de `podman-compose` (no una
  preferencia estética).
- No declarar terminada la tarea con el primer `build`+`run` exitoso
  sin más — cuando `docker-compose` empezó a fallar de forma
  reproducible, se investigó hasta encontrar la causa real (versión de
  `torch`) en vez de descartarlo como "problema de la máquina" sin
  evidencia. El diagnóstico documentado aquí (aislar con un contenedor
  mínimo, descartar memoria/disco/volumen con evidencia real antes de
  llegar a la causa) queda como referencia para el equipo si algo así
  vuelve a pasar.
- Recrear la VM de Podman entera (no solo reiniciarla) fue una
  decisión consultada con el usuario antes de ejecutarla, por ser una
  acción más invasiva (borra imágenes/volúmenes existentes de Podman).

Pruebas de aceptación: `docker build`/`podman build` termina sin
errores ✅; `docker run`/`podman run` (y `docker-compose up`/
`podman-compose up`) levanta el servicio ✅; `/salud` responde 200
desde dentro del contenedor corriendo ✅ — los 3 criterios cumplidos
con evidencia real, no simulada.

Pendiente: cuando el equipo tenga Docker Desktop funcionando en alguna
máquina, confirmar si el bug #1 (`dockerfile:` ignorado por
`podman-compose`) también ocurre con `docker compose` nativo, o es
exclusivo de `podman-compose` en Windows — de ser exclusivo, se podría
volver a separar `Dockerfile` dentro de `api/` para quien use Docker
real.

## Sesión 28 — 2026-09-18 — Anderson García

Rate limiting, validación de entrada, y confirmación de privacidad
(NO persistencia de texto) en el servicio de la API.

Contexto: `api/main.py` ya tenía validación básica de longitud/vacío
desde la Sesión 25 (adelantada como "porción pequeña de la Sesión
28"). Esta sesión completa lo que faltaba: rate limiting, y sobre todo
convertir la promesa de privacidad de `CONTEXTO_PROYECTO.md` ("los
datos sensibles no salen a una nube de terceros", "es auditable") en
algo verificable en el código, no solo en un comentario.

Qué se hizo:
- **Rate limiting**: `_verificar_rate_limit()` — ventana deslizante en
  memoria, por IP de cliente (`request.client.host`), con
  `threading.Lock` (los endpoints corren en el threadpool de FastAPI,
  así que sí hacía falta para seguridad entre hilos, no es solo
  cosmético). Default 10 solicitudes/60s, configurable por
  `RATE_LIMIT_MAX_SOLICITUDES`/`RATE_LIMIT_VENTANA_SEGUNDOS`. Al
  superarse, `429` con mensaje claro y header `Retry-After`. Aplica
  solo a `POST /traducir` (la operación cara) — `GET /salud` y el
  `/metricas` nuevo quedan sin límite, a propósito.
- **Validación de entrada**: la de la Sesión 25 ya cubría vacío/solo-
  espacios (400) y longitud máxima 500 (422 vía Pydantic) — se dejó
  igual, ya era correcta.
- **Errores claros, nunca un stack trace crudo**: agregado
  `manejador_errores_no_previstos` (captura cualquier `Exception` no
  prevista → `500` con mensaje genérico entendible, el detalle real
  solo queda en los logs del servidor) — FastAPI ya no exponía
  tracebacks por default (`debug=False`), pero ahora queda garantizado
  explícitamente en el código, no implícito en una configuración que
  alguien podría cambiar sin darse cuenta de esta consecuencia.
- **Confirmación de privacidad, hecha verificable, no solo dicha**:
  agregado `GET /metricas` — SOLO 4 contadores agregados
  (`total_solicitudes`, `traducciones_exitosas`,
  `rechazadas_validacion`, `rechazadas_rate_limit`), nunca texto de
  ninguna solicitud, sin persistencia a disco (se reinician en ceros
  si el proceso reinicia). Agregado también
  `manejador_error_validacion` para que los rechazos 422 de Pydantic
  (que antes no pasaban por el cuerpo de `traducir()`) sí queden
  contados en `rechazadas_validacion` — sin esto, las métricas
  quedaban incompletas/engañosas para alguien auditando.
- Prueba explícita de que la promesa se cumple, no solo se afirma:
  `api/test_main.py::test_metricas_solo_expone_contadores_agregados`
  manda un texto de prueba y confirma que NO aparece en la respuesta
  de `/metricas` (ni el texto de entrada ni la traducción simulada).
- 4 pruebas nuevas en `api/test_main.py` (11 en total, antes 7):
  rate limit → 429 tras exceder el límite (con `Retry-After` y mensaje
  claro), `/salud`/`/metricas` sin límite, métricas solo agregadas, y
  error no previsto sin traceback expuesto. Agregado un fixture
  `autouse` que limpia el estado de rate limiting y métricas entre
  cada prueba — sin esto, las pruebas se habrían contaminado entre sí
  (todas comparten la misma IP de `TestClient`).
- **Prueba de aceptación real, con `curl` contra el servicio real
  corriendo** (no solo `pytest`): 13 solicitudes seguidas a
  `/traducir` contra el límite de 10/60s → las primeras 10 pasan el
  rate limit, las 3 siguientes responden `429` con
  `Retry-After: 60` y mensaje claro. Texto vacío y texto de 600
  caracteres (límite 500) → ambos `422` con mensaje entendible en
  `detail`, ningún `500`.
- Sección nueva "Seguridad y privacidad" en `api/README.md`: qué SÍ
  hace el servicio (rate limiting, validación, errores claros) y qué
  NO hace (no persiste ni loguea texto, `/metricas` solo agregados,
  sin persistencia de ningún tipo) — con cómo verificarlo cada punto,
  no solo la afirmación.

Decisiones tomadas:
- Rate limiting en memoria (no Redis/almacén externo) — correcto para
  una sola instancia del servicio (el estado actual del proyecto,
  `CONTEXTO_PROYECTO.md`); agregar esa dependencia ahora habría sido
  complejidad sin beneficio real todavía. Documentado explícitamente
  como limitación a revisar si el servicio se escala a varias
  instancias.
- Agregar `GET /metricas` no lo pedía el prompt explícitamente, pero
  la frase "confirma explícitamente... (solo métricas agregadas, no el
  texto en sí)" pedía que la promesa de privacidad fuera verificable,
  no solo un comentario — un endpoint real con una prueba que
  confirma que no filtra texto es más convincente para "auditable" que
  solo decirlo en la documentación.
- Agregado el manejador de `RequestValidationError` (para contar los
  422 de Pydantic en las métricas) tras notar, probando en vivo, que
  `/metricas` mostraba `rechazadas_validacion: 0` pese a haber
  rechazado texto vacío y texto largo — una métrica "agregada" que no
  cuenta todo lo que dice contar no sirve para auditar nada.

Pruebas de aceptación: `api/test_main.py` 11/11 pasan ✅; rate limiting
real con `curl` → `429` en la solicitud 11 en adelante, con
`Retry-After` y mensaje claro ✅; texto vacío/demasiado largo → `422`
con mensaje entendible, nunca `500` ✅.

Pendiente: ninguno específico de esta sesión — los 3 puntos pedidos
(rate limiting, validación, confirmación de privacidad) y el criterio
de calidad (errores claros, no stack traces) quedaron cumplidos con
evidencia real, tanto en `pytest` como contra el servicio real
corriendo.

## Sesión 29 — 2026-09-20 — Mariana Malagón

Logging/observabilidad (calidad por dialecto, latencia).

Qué se hizo:
- Extendido `api/main.py`: `POST /traducir` ahora mide la latencia real
  de `_generar_traduccion` (`time.monotonic()` antes/después) y la
  registra en `METRICAS_POR_DIALECTO[dialecto]`, y devuelve un
  `solicitud_id` aleatorio (no reversible al texto) además de la
  traducción.
- Nuevo `POST /retroalimentacion`: recibe `{solicitud_id, es_correcta}`,
  busca el dialecto asociado a ese `solicitud_id` (guardado solo como
  `id -> dialecto`, nunca texto) y actualiza el conteo de
  retroalimentación positiva/total de ese dialecto. `404` si el
  `solicitud_id` no existe o ya se usó (evita votar dos veces con el
  mismo id).
- `GET /metricas` ahora agrega `por_dialecto`: por cada dialecto,
  `solicitudes`, `latencia_promedio_seg` y `tasa_retroalimentacion_positiva`
  — todo agregado, nunca texto.
- 8 pruebas nuevas en `api/test_main.py` (15 en total): latencia
  promedio correcta, retroalimentación positiva reflejada en métricas,
  `solicitud_id` inválido rechazado, un mismo `solicitud_id` no se
  puede usar dos veces. Actualizado el fixture de aislamiento para
  limpiar también `METRICAS_POR_DIALECTO` y las solicitudes pendientes
  de feedback entre pruebas.
- `api/README.md`: nueva sección "Observabilidad" con el formato real
  de `/metricas` y cómo se enlaza retroalimentación↔dialecto sin
  guardar texto.

Bug real encontrado y corregido en el camino: el primer intento de
probar la latencia mockeaba `time.monotonic` globalmente — pero
`_verificar_rate_limit` (Sesión 28) también usa `time.monotonic()`
para su ventana deslizante, así que parcharlo de forma global
descuadró el rate limiter y **colgó la corrida de `pytest`** (sin
error, sin salida, el proceso quedó vivo indefinidamente). Diagnosticado
matando el proceso colgado y revisando qué más usaba esa misma
función. Corregido sin tocar el reloj global: la prueba de latencia
ahora hace que la traducción mockeada tarde un `time.sleep(0.05)` real
y mide sobre eso, en vez de simular el reloj.

Decisiones tomadas:
- No se agregó límite de tasa a `/retroalimentacion` — es una
  operación barata (no toca el modelo) y limitarla no protege nada que
  ya no proteja el hecho de que un `solicitud_id` solo se puede usar
  una vez.
- El mapa `solicitud_id -> dialecto` no tiene TTL/limpieza automática
  (igual que el historial de rate limiting) — aceptable al tamaño de
  este proyecto, documentado como lo primero a revisar si el tráfico
  creciera.

Pruebas de aceptación: `SKIP_MODEL_LOAD=1 python -m pytest api/test_main.py -v`
→ **15/15 passed**. Solicitudes de prueba con distintos dialectos y
latencias reales (via `time.sleep`), luego `GET /metricas` refleja
correctamente los promedios y conteos esperados por dialecto — tal
como pedía la prueba de aceptación original.

Pendiente: probar `GET /metricas` contra el servicio real (con el
modelo cargado de verdad, no mockeado) para confirmar que las
latencias reportadas coinciden con lo medido manualmente en las
Sesiones 25/27 (~50-80s) — no se hizo en esta sesión por la misma
razón de siempre (sin GPU local).
