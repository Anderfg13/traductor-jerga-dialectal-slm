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
