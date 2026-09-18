# api/

Servicio de traducción vía API REST (FastAPI). Ver el docstring de
`main.py` para el detalle completo.

## Endpoints

- `GET /salud` — healthcheck, responde `{"estado": "ok"}`.
- `POST /traducir` — body `{"texto": "...", "dialecto": "opcional"}`,
  responde `{"traduccion": "...", "dialecto": "..."}`.

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

`api/test_main.py` prueba la capa de API (validación de entrada,
códigos de estado, forma de la respuesta) con el modelo mockeado, para
poder correrlas en cualquier máquina sin `torch`/`peft` instalados ni
descargar el modelo de 3B:

```
pip install pytest httpx  # si no están instalados ya
SKIP_MODEL_LOAD=1 python -m pytest api/test_main.py -v
```

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
