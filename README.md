# Traductor de jerga y dialectos español-inglés (SLM + fusión de modelos)

Traductor especializado en jerga y dialectos del español-inglés mediante
ajuste fino de un modelo de lenguaje pequeño (SLM) sobre datos sintéticos
generados por múltiples LLMs, con fusión de modelos. Ver
[`CONTEXTO_PROYECTO.md`](./CONTEXTO_PROYECTO.md) para el detalle completo
del proyecto (preguntas de investigación, pipeline, alcance por fase,
atributos de calidad).

**Equipo:** Anderson García, Paula Lozano, Mariana Malagón.
**Curso:** TDSE — Transformación Digital y Sistemas Empresariales.

## Estructura del repositorio

```
seeds/        Banco de semillas: expresiones dialectales/jerga + traducción correcta
generation/   Generación sintética con los 3 LLMs generadores
finetuning/   Ajuste fino (LoRA) de los SLMs candidatos
merging/      Fusión de modelos (mergekit: TIES/DARE, destilación multi-maestro)
evaluation/   Métricas de calidad (BLEU, chrF, evaluación humana, kappa)
api/          Servicio de traducción expuesto como API REST
```

Cada commit relevante debe acompañarse de una entrada en
[`BITACORA.md`](./BITACORA.md).

## Generadores sintéticos

El proyecto usa tres LLMs generadores distintos, los tres con capa
gratuita:

| Proveedor | Modelo | Costo | Lista de modelos vigente |
|---|---|---|---|
| Groq | `openai/gpt-oss-20b` | Gratis (capa gratuita, con límites de tasa) | https://console.groq.com/docs/models |
| Cohere | `command-r-08-2024` | Gratis (clave "trial", 1000 llamadas/mes) | https://docs.cohere.com/docs/models |
| Google | `gemini-3.6-flash` | Gratis (capa gratuita en AI Studio) | https://ai.google.dev/gemini-api/docs/models |

> Estos proveedores retiran o renombran modelos con cierta frecuencia
> (por ejemplo `command-r` fue retirado por Cohere en sept. 2025, y
> `gemini-1.5-flash` ya no está disponible). Si `generation/test_apis.py`
> falla con un error 404 tipo "model not found" / "does not exist",
> revisa la lista vigente del proveedor en el enlace de arriba y
> actualiza el nombre del modelo en ese script.

> Notas de proveedores descartados:
> - **xAI (Grok)**: no ofrece capa gratuita permanente — solo créditos
>   cargados o un programa de créditos a cambio de compartir datos con
>   xAI, lo cual no encaja con el requisito de datos auditables del
>   proyecto.
> - **OpenCode Zen**: sus modelos Claude/GPT reempaquetados siguen
>   siendo de pago; solo sus modelos propios (no Claude) son gratis.
> - **Anthropic (Claude)**: no tiene capa gratuita continua, se dejó
>   fuera en favor de Cohere para que los 3 generadores sean gratis.

## Instalación del entorno

Requiere Python 3.10+.

1. Crea el entorno virtual (una sola vez, dentro de la carpeta del
   repositorio):
   ```bash
   python -m venv .venv
   ```
2. Actívalo — **hay que repetir este paso cada vez que abras una
   terminal nueva**, antes de instalar o correr cualquier script:
   ```bash
   # Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # Windows (cmd.exe):
   .venv\Scripts\activate.bat
   # Windows (Git Bash) / Linux / Mac:
   source .venv/bin/activate
   ```
   Sabes que quedó activo porque el prompt de la terminal empieza con
   `(.venv)`.
3. Instala las dependencias (con el entorno ya activado):
   ```bash
   pip install -r requirements.txt
   ```
4. Activa los git hooks del proyecto (una sola vez por clon — git no
   los activa solo):
   ```bash
   git config core.hooksPath .githooks
   ```
   Esto habilita [`.githooks/pre-commit`](./.githooks/pre-commit): un
   commit que modifique archivos del proyecto sin incluir una entrada
   nueva en `BITACORA.md` se rechaza (mensaje explicando qué falta).
   Para un commit genuinamente trivial que no amerite entrada de
   bitácora, usa `git commit --no-verify` a propósito.

> Si al correr `generation/test_apis.py` ves errores como
> `ModuleNotFoundError: No module named 'groq'` o
> `ImportError: cannot import name 'genai' from 'google'`, significa
> que el paso 3 no se ejecutó (o se ejecutó sin el entorno activado).
> Repite los pasos 2 y 3 en la misma terminal donde vas a correr el
> script.

## Configuración de claves de API

Las claves de API **nunca** se escriben en el código ni se suben al
repositorio (`.env` está en `.gitignore`).

1. Copia la plantilla:
   ```bash
   cp .env.example .env
   ```
2. Edita `.env` y completa cada clave (las 3 son gratuitas):
   - `GROQ_API_KEY` → https://console.groq.com/keys
   - `COHERE_API_KEY` → https://dashboard.cohere.com/api-keys
   - `GOOGLE_API_KEY` → https://aistudio.google.com/apikey

## Prueba de conectividad

Para confirmar que las tres claves funcionan sin gastar cuota de más
(una sola llamada corta por API):

```bash
python generation/test_apis.py
```

Salida esperada: para cada generador se imprime el nombre del modelo, una
respuesta corta y `estado: OK`. Si falta una clave o es inválida, el
script indica cuál falló (sin exponer el valor de la clave) y termina
con código de salida distinto de cero.

## Solución de problemas comunes

**`ModuleNotFoundError: No module named 'groq'` / `'cohere'`, o
`ImportError: cannot import name 'genai' from 'google'`**
Faltó instalar las dependencias en el entorno activo, o el entorno
virtual no estaba activado al instalar/correr el script. Ver
"Instalación del entorno" arriba: activa `.venv` y corre de nuevo
`pip install -r requirements.txt` en esa misma terminal.

**El registro en Cohere pide un método de pago (tarjeta) incluso para
la clave gratuita**
Cohere lo puede pedir como verificación de identidad al crear la
cuenta, sin que eso implique un cobro mientras uses la clave de
evaluación ("trial", gratuita y limitada a 1000 llamadas/mes) — pero
esto puede cambiar según la política vigente de Cohere. Antes de
ingresar una tarjeta:
1. Confirma en qué paso exacto aparece la solicitud (al crear la
   cuenta vs. al generar la API key en el dashboard) y si el
   formulario distingue entre "trial/evaluation key" y "production
   key".
2. Si no quieres ingresar una tarjeta, usa como alternativa gratuita
   sin tarjeta **Mistral** ("La Plateforme", tiene capa gratuita) u
   otro proveedor sin este requisito — avísale al equipo para
   actualizar `requirements.txt`, `.env.example` y
   `generation/test_apis.py` si se decide el cambio.

**Error 404 "model not found" / "does not exist" / "was removed"**
El proveedor retiró o renombró ese modelo. No es un problema de tu
clave: revisa la lista vigente de modelos en el enlace de la tabla de
"Generadores sintéticos" arriba y actualiza el nombre del modelo en
`generation/test_apis.py` (y en `README.md`).

**El script corre pero una API específica da error 401/403**
La clave en `.env` es inválida, expiró, o tiene un espacio/comilla de
más al copiarla. Regenera la clave en el dashboard del proveedor y
pégala de nuevo en `.env` sin comillas ni espacios extra.

**`estado: RESPUESTA VACIA` o `AttributeError: 'NoneType' object has no
attribute 'strip'`**
Pasa con modelos de "razonamiento" (como `openai/gpt-oss-20b` en Groq o
`gemini-3.6-flash` en Google): gastan parte del límite de tokens
pensando internamente antes de responder, y si el límite es muy bajo
no queda presupuesto para el texto final. `generation/test_apis.py` ya
maneja esto (baja el "esfuerzo de razonamiento" en Groq con
`reasoning_effort`, y en Google con `thinking_level="minimal"` — ojo,
los modelos Gemini 3.x usan `thinking_level`, no `thinking_budget`, que
da error 400 —, además de un `MAX_TOKENS` más alto). Si vuelve a pasar
con otro modelo, sube `MAX_TOKENS` en el script o revisa si ese modelo
tiene un parámetro para desactivar/reducir el razonamiento.

**Error 429 (rate limit / too many requests)**
Las capas gratuitas tienen límites de peticiones por minuto/día.
Espera unos minutos y vuelve a correr el script; no lo ejecutes en
bucle.
