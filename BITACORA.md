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
