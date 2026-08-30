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
