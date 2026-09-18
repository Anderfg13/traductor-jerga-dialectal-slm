# api/

Servicio de traducción vía API REST (FastAPI). Ver el docstring de
`main.py` para el detalle completo.

## Endpoints

- `GET /salud` — healthcheck, responde `{"estado": "ok"}`.
- `POST /traducir` — body `{"texto": "...", "dialecto": "opcional"}`,
  responde `{"traduccion": "...", "dialecto": "..."}`.

## Levantar el servicio con el modelo real

Requiere la pila de ML completa (`torch`, `transformers`, `peft`) y el
adaptador entrenado en `finetuning/checkpoints/generador1/adapter/`.
Por la política de cómputo del proyecto (`CONTEXTO_PROYECTO.md`, sin
GPU utilizable en las máquinas del equipo), esto se corre en Colab o en
el entorno de despliegue final (Sesión 26), no en local para desarrollo
diario:

```
uvicorn api.main:app --reload
```

Prueba manual una vez levantado:

```
curl http://localhost:8000/salud
curl -X POST http://localhost:8000/traducir -H "Content-Type: application/json" -d "{\"texto\": \"Que chimba, parcero!\"}"
```

## Correr las pruebas SIN el modelo real

`api/test_main.py` prueba la capa de API (validación de entrada,
códigos de estado, forma de la respuesta) con el modelo mockeado, para
poder correrlas en cualquier máquina sin `torch`/`peft` instalados ni
descargar el modelo de 3B:

```
SKIP_MODEL_LOAD=1 python -m pytest api/test_main.py -v
```

**Esto NO reemplaza probar el endpoint con el modelo real** (que sí
devuelve una traducción coherente) — esa prueba manual con `curl`
contra el modelo cargado de verdad queda pendiente para cuando el
servicio se levante en Colab o en el entorno de despliegue (Sesión 26),
no se pudo hacer en esta máquina por la misma razón de siempre: no hay
GPU utilizable localmente.
