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

**Resultado real de correr esto en la máquina local (Sesión 27, CPU,
sin GPU)**:
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
