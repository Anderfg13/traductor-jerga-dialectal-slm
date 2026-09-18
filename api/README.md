# api/

Servicio de traducción vía API REST (FastAPI). Ver el docstring de
`main.py` para el detalle completo.

## Endpoints

- `GET /salud` — healthcheck, responde `{"estado": "ok"}`. Sin límite
  de tasa.
- `GET /metricas` — contadores agregados de uso (`total_solicitudes`,
  `traducciones_exitosas`, `rechazadas_validacion`,
  `rechazadas_rate_limit`) — nunca el texto de ninguna solicitud. Sin
  límite de tasa. Ver "Seguridad y privacidad" abajo.
- `POST /traducir` — body `{"texto": "...", "dialecto": "opcional"}`,
  responde `{"traduccion": "...", "dialecto": "..."}`. Limitado a 10
  solicitudes/minuto por IP (configurable, ver abajo).

## Seguridad y privacidad (Sesión 28)

Punto de diferenciación de producto de `CONTEXTO_PROYECTO.md`: "los
datos sensibles no salen a una nube de terceros" y "es auditable".
Esto es lo que el servicio SÍ hace y lo que explícitamente NO hace:

**Qué SÍ hace:**

- **Límite de tasa (rate limiting)**: `POST /traducir` está limitado a
  `RATE_LIMIT_MAX_SOLICITUDES` solicitudes cada
  `RATE_LIMIT_VENTANA_SEGUNDOS` segundos, por IP de cliente (default:
  **10 cada 60 segundos** — configurable por variable de entorno). Al
  superarlo, responde `429 Too Many Requests` con un mensaje claro y
  un header `Retry-After`. Implementado en memoria (ventana deslizante
  por IP, con `threading.Lock` para ser seguro entre hilos) — pensado
  para una sola instancia del servicio; si se escala a varias
  instancias, esto necesitaría moverse a un almacén compartido (ej.
  Redis).
- **Validación de entrada**: `texto` es obligatorio, no puede estar
  vacío ni ser solo espacios, y tiene un máximo de 500 caracteres.
  Cualquier solicitud mal formada (campo faltante, tipo incorrecto,
  fuera de esos límites) se rechaza con `422` (o `400` para el caso de
  solo-espacios, que Pydantic no detecta por sí solo) y un mensaje
  entendible en `detail` — nunca con un `500` genérico.
- **Errores claros, nunca un stack trace crudo**: cualquier excepción
  no prevista (un bug, un fallo del modelo) devuelve `500` con un
  mensaje genérico entendible. El traceback real, si existe, queda
  solo en los logs del proceso del servidor — nunca en la respuesta
  HTTP que recibe quien llama a la API.

**Qué NO hace (y por qué se puede confiar en eso):**

- **Nunca escribe a disco ni a un log externo el texto de ninguna
  solicitud ni de ninguna traducción generada.** Se puede verificar
  leyendo `api/main.py`: no hay ninguna llamada a
  `logging`/`print`/escritura de archivo que incluya el texto de
  entrada, el dialecto, ni la traducción devuelta. El log de acceso
  por default de `uvicorn` registra únicamente método HTTP, ruta,
  código de estado y latencia — nunca el cuerpo de la solicitud ni de
  la respuesta.
- **`GET /metricas` solo expone 4 contadores agregados**, nunca datos
  de ninguna solicitud individual. Probado explícitamente en
  `api/test_main.py::test_metricas_solo_expone_contadores_agregados`:
  se manda un texto de prueba, se confirma que NO aparece en la
  respuesta de `/metricas`.
- **No hay persistencia de ningún tipo**: ni las métricas ni el
  historial de rate limiting se guardan en disco — todo vive en
  memoria del proceso y se reinicia en ceros si el servicio se
  reinicia. Eso demuestra en la práctica (no solo en un comentario)
  que "solo métricas agregadas, no el texto en sí" es literalmente
  cierto: no hay ningún lugar donde el texto podría haber quedado
  guardado.

**Configuración del límite de tasa** (variables de entorno, opcionales):

```bash
export RATE_LIMIT_MAX_SOLICITUDES=10      # default: 10
export RATE_LIMIT_VENTANA_SEGUNDOS=60     # default: 60
```

## Levantar el servicio con el modelo real

Requiere la pila de ML completa (`torch`, `transformers`, `peft`) y el
adaptador entrenado en `finetuning/checkpoints/generador1/adapter/`:

```
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

La primera solicitud a `/salud` no responde hasta que el modelo
termina de cargar (el `lifespan` de FastAPI carga el modelo ANTES de
que el servidor empiece a aceptar conexiones) — en CPU local, contar
uno o dos minutos.

Prueba manual una vez levantado:

```
curl http://localhost:8000/salud
curl -X POST http://localhost:8000/traducir -H "Content-Type: application/json" -d "{\"texto\": \"Que chimba, parcero!\"}"
```

**Resultado real de correr esto en la máquina local (Sesión 25,
continuación, CPU, sin GPU)**:
- `GET /salud` → `200 {"estado":"ok"}` en ~7ms.
- `POST /traducir` con `"Que chimba, parcero!"` → `200
  {"traduccion":"That's awesome, buddy!","dialecto":"Andina"}` en
  **79.4s**.
- Una segunda solicitud (`"No manches, esta bien bacano."`) → `200
  {"traduccion":"No way, this is really cool."}` en **49.8s** — más
  rápida que la primera (sin el costo de arranque en frío), pero
  igual muy lejos de "unos pocos segundos".

**Las traducciones son correctas y coherentes — el problema es
latencia, no funcionalidad.** El endpoint funciona de principio a fin
en local, pero 50-80s por solicitud no sirve para producción ni para
demostrar el objetivo de latencia del proyecto. Cumplir ese objetivo
necesita GPU (Colab, o el entorno de despliegue de la Sesión 26) —
consistente con la política de cómputo pesado de
`CONTEXTO_PROYECTO.md`. Para desarrollo diario y para confirmar que el
endpoint funciona correctamente, la máquina local alcanza; para medir
la latencia real, no.

## Correr las pruebas SIN el modelo real

`api/test_main.py` (11 pruebas) prueba la capa de API — validación de
entrada, rate limiting, métricas agregadas, códigos de estado, forma
de la respuesta — con el modelo mockeado, para poder correrlas en
cualquier máquina sin `torch`/`peft` instalados ni descargar el modelo
de 3B:

```
pip install pytest httpx  # si no están instalados ya
SKIP_MODEL_LOAD=1 python -m pytest api/test_main.py -v
```

### Prueba de aceptación real: rate limiting y validación (Sesión 28)

Corrido contra el servicio real levantado en local (no solo `pytest`),
con `curl`, tal como pedía la prueba de aceptación:

**13 solicitudes seguidas a `/traducir` contra el límite default de
10/60s** — las primeras 10 pasan el rate limit (503 porque el modelo
no estaba cargado en esta prueba puntual, sin relación al límite de
tasa), las siguientes 3 responden `429`:

```
solicitud 1  -> HTTP 503
...
solicitud 10 -> HTTP 503
solicitud 11 -> HTTP 429
solicitud 12 -> HTTP 429
solicitud 13 -> HTTP 429
```

Respuesta completa de una de las rechazadas:

```
HTTP/1.1 429 Too Many Requests
retry-after: 60
content-type: application/json

{"detail":"Demasiadas solicitudes. Máximo 10 cada 60 segundos por cliente. Espera unos segundos y vuelve a intentar."}
```

**Texto vacío** (`{"texto": ""}`) → `422`, mensaje claro:
`{"detail":[{"type":"string_too_short","loc":["body","texto"],"msg":"String should have at least 1 character",...}]}`

**Texto de 600 caracteres** (límite 500) → `422`, mensaje claro:
`{"detail":[{"type":"string_too_long","loc":["body","texto"],"msg":"String should have at most 500 characters",...}]}`

Ninguno de los dos casos devuelve `500` ni expone un stack trace.

## Contenedor (Docker / Podman)

`Dockerfile`, `docker-compose.yml` y `.dockerignore` viven en la
**raíz del repositorio** (no dentro de `api/`) a propósito — ver el
encabezado de `Dockerfile` para por qué. El `Dockerfile` copia
explícitamente solo lo que el servicio necesita (`api/main.py`,
`finetuning/probar_baseline.py`, el adaptador de
`finetuning/checkpoints/generador1/adapter/`) — nada de datos crudos,
otros checkpoints, ni el resto del pipeline.

### Build

Desde la raíz del repo:

```bash
docker build -t traductor-api .
# o con Podman:
podman build -t traductor-api .
```

### Run

```bash
docker run -d -p 8000:8000 -v hf-cache:/root/.cache/huggingface traductor-api
# o con Podman:
podman run -d -p 8000:8000 -v hf-cache:/root/.cache/huggingface traductor-api
```

El volumen `hf-cache` guarda el modelo base descargado (~6GB) entre
reinicios del contenedor — sin él, cada `run` nuevo lo volvería a
descargar desde cero. La primera vez, contar varios minutos (descarga
+ carga del modelo) antes de que `/salud` responda.

### docker-compose (un solo comando)

```bash
docker compose up --build
# o con Podman:
podman compose up --build
# si "podman compose" no encuentra proveedor de compose (pasó en
# Windows en esta sesión, ver BITACORA.md Sesión 27):
python -m pip install --user podman-compose
python -m podman_compose up --build
```

### Prueba de aceptación real (Sesión 27, con Podman en Windows)

Corrido `build` + `run` (y por separado, `docker-compose up`) de
verdad, con el modelo real cargado dentro del contenedor:

- `docker build` / `podman build` → **termina sin errores**.
- Contenedor arriba → `GET /salud` → `200 {"estado":"ok"}` en ~36ms.
- `POST /traducir` con `"Que nota, marica, quedo bacano!"` (dialecto
  Caribeña) → `200 {"traduccion":"What a note, dude, it turned out
  cool!","dialecto":"Caribena"}` en **33.8s** — coherente, sin texto
  corrupto ni repetido (más rápido que los 50-80s medidos con
  `uvicorn` directo en la Sesión 25, probablemente por variación
  normal de carga de la máquina, no por el contenedor en sí).
- `docker-compose up` (vía `podman-compose`) → mismo resultado,
  `/salud` responde 200.

### Notas de la máquina donde se probó esto (Windows + Podman)

Docker Desktop no se pudo instalar en esta máquina (error de
instalación); se usó **Podman** como alternativa — mismo formato de
`Dockerfile`, comandos casi idénticos. Tres problemas reales
encontrados y resueltos en el camino, documentados aquí por si el
equipo usa Podman en Windows para esto:

1. **`podman-compose` en Windows ignora el campo `dockerfile:`** del
   `build:` en `docker-compose.yml` cuando el Dockerfile no está en la
   raíz del contexto — genera el comando de build sin el flag `-f` en
   absoluto (confirmado con `--verbose`), fallando con "no
   Containerfile or Dockerfile found". Por eso `Dockerfile` y
   `docker-compose.yml` quedaron en la raíz del repo (contexto =
   mismo directorio del Dockerfile, sin necesitar ese campo). Con
   `docker compose` nativo esto probablemente no pasa — no se pudo
   confirmar en esta máquina por no tener Docker Desktop instalado.
2. **`curl http://localhost:8000/...` (o `127.0.0.1`) no conecta**
   contra un contenedor de Podman en Windows, aunque
   `podman ps`/`podman port` muestren el mapeo `0.0.0.0:8000->8000`
   correcto — el reenvío de puertos de `gvproxy` (Podman sobre WSL2)
   solo quedó escuchando en `[::1]:8000` (loopback IPv6), no en la
   IPv4 que `curl 127.0.0.1` necesita, y tampoco respondía de forma
   confiable por IPv6 directo. **Workaround que sí funcionó siempre**:
   pegarle directo a la IP de la VM de Podman, no a `localhost`:
   ```bash
   podman machine ssh podman-machine-default "ip -4 addr show eth0 | grep inet"
   curl http://<esa-ip>:8000/salud
   ```
3. **`torch` sin fijar versión (`torch>=2.3.0`) resuelve a la más
   reciente disponible (2.14.0+cpu al momento de esta sesión), que
   crashea con un error de glibc** (`malloc.c: assertion failed`) en
   el simple `import torch`, dentro de la imagen `python:3.11-slim`
   en este entorno (Podman sobre WSL2 en Windows) — confirmado
   aislando el problema con un contenedor mínimo que solo hacía
   `import torch`, sin tocar nada de nuestro código. Se descartaron
   antes, con evidencia real, memoria insuficiente, espacio en disco y
   corrupción del volumen de caché como causas (ver BITACORA.md Sesión
   27 para el diagnóstico completo paso a paso). **Fijado
   `torch==2.13.0`** en `api/requirements.txt` — la misma versión ya
   usada con éxito en el resto del proyecto — y el problema no volvió
   a aparecer en ninguna corrida posterior.
