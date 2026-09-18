"""
api/main.py

Servicio de traducción vía API REST. Expone:
  - POST /traducir: recibe texto en español (y un dialecto opcional,
    informativo), devuelve la traducción generada por el modelo
    ajustado con LoRA del Generador 1 (Sesión 19,
    `finetuning/checkpoints/generador1/adapter/`).
  - GET /salud: healthcheck simple para confirmar que el proceso está
    vivo, sin depender de que el modelo ya haya terminado de cargar.
  - GET /metricas: contadores AGREGADOS de uso (cuántas solicitudes,
    cuántas exitosas/rechazadas) — nunca el texto de ninguna
    solicitud. Ver "Privacidad y auditabilidad" más abajo.

El modelo se carga UNA SOLA VEZ al iniciar el servicio (evento
`lifespan` de FastAPI), no en cada solicitud — cargar un modelo de 3B
por request destruiría la latencia.

Cargar el modelo real requiere la pila pesada de ML (torch,
transformers, peft). Para poder probar la CAPA DE API (validación de
entrada, rate limiting, códigos de estado, forma de la respuesta) sin
esa pila instalada ni descargar el modelo de 3B, la carga real se
salta si la variable de entorno `SKIP_MODEL_LOAD=1` está presente —
así es como corre `api/test_main.py`.

**El servicio SÍ se levantó localmente con el modelo real** (Sesión
25/27) — ver BITACORA.md para los tiempos medidos (CPU local: 50-80s
por traducción; con GPU/contenedor, más rápido). La traducción en sí
es correcta y coherente.

Privacidad y auditabilidad (Sesión 28 — punto de diferenciación de
producto de CONTEXTO_PROYECTO.md: "los datos sensibles no salen a una
nube de terceros... es auditable"):
  - **Este servicio NUNCA escribe a disco ni a un log externo el
    texto de ninguna solicitud ni de ninguna traducción generada.**
    No hay ninguna llamada a `logging`/`print`/escritura de archivo en
    todo este módulo que incluya `solicitud.texto`, `dialecto`, ni la
    traducción devuelta — se puede verificar buscando esas variables
    fuera del cuerpo de la función que las procesa
    (`grep -n "texto" api/main.py` y `grep -n "traduccion" api/main.py`, ninguna aparición está
    dentro de un `print`/`logging.*`).
  - El log de acceso por default de `uvicorn` (que si esta corriendo
    con verbose logging podría imprimir en la consola del servidor)
    registra únicamente método HTTP, ruta, código de estado y latencia
    — NUNCA el cuerpo de la solicitud ni de la respuesta. No se
    modificó ni se necesitó modificar ese comportamiento.
  - Lo único que el servicio mantiene en memoria son **contadores
    agregados** (`GET /metricas`): cuántas solicitudes en total,
    cuántas exitosas, cuántas rechazadas por validación, cuántas
    rechazadas por límite de tasa. Ningún contador guarda texto, y
    todos se reinician a cero al reiniciar el proceso (no hay
    persistencia a disco de ningún tipo) — eso demuestra en la
    práctica, no solo en un comentario, que "solo métricas agregadas,
    no el texto en sí" es literalmente cierto.

Límite de tasa (rate limiting) — contra abuso, por IP de cliente:
  - `POST /traducir` está limitado a `RATE_LIMIT_MAX_SOLICITUDES`
    solicitudes cada `RATE_LIMIT_VENTANA_SEGUNDOS` segundos por IP
    (default: 10 cada 60s — configurable por variable de entorno,
    cada solicitud de traducción es cara de cómputo, así que el
    límite es conservador a propósito). Al superarlo, responde `429`
    con un mensaje claro y un header `Retry-After`.
  - `GET /salud` y `GET /metricas` NO están limitados — son
    operaciones baratas (no tocan el modelo) y un balanceador de
    carga/monitoreo externo podría necesitar llamarlas con frecuencia.
  - Implementación en memoria (una ventana deslizante por IP, con un
    `threading.Lock` porque FastAPI corre los endpoints síncronos en
    un threadpool) — suficiente para una sola instancia del servicio.
    Si el servicio se escala a varias instancias más adelante, esto
    necesitaría moverse a un almacén compartido (ej. Redis); no se
    hizo ahora porque agregar esa dependencia no tiene sentido todavía
    con una sola instancia corriendo (ver CONTEXTO_PROYECTO.md,
    arquitectura objetivo aún de un solo servicio).

Manejo de errores: cualquier excepción no prevista devuelve un `500`
con un mensaje genérico y entendible, nunca el traceback crudo (ver
`manejador_errores_no_previstos` más abajo) — además de que FastAPI ya
no expone tracebacks por default fuera de modo debug (`debug=False`
aquí), este manejador lo deja garantizado explícitamente, no
implícito.

Uso (requiere `pip install -r requirements.txt` completo, con GPU o
paciencia en CPU para la carga inicial):
    uvicorn api.main:app --reload

Prueba rápida una vez levantado:
    curl http://localhost:8000/salud
    curl http://localhost:8000/metricas
    curl -X POST http://localhost:8000/traducir \
        -H "Content-Type: application/json" \
        -d "{\"texto\": \"Que chimba, parcero!\"}"

Pruebas de la capa de API sin el modelo real (incluye rate limiting y
validación):
    SKIP_MODEL_LOAD=1 python -m pytest api/test_main.py
"""

import os
import sys
import threading
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

ADAPTER_DIR = Path(__file__).resolve().parent.parent / "finetuning" / "checkpoints" / "generador1" / "adapter"

# Estado del modelo cargado, poblado una sola vez en el lifespan de
# abajo. No es un objeto global "mágico": es explícitamente el único
# lugar del módulo que guarda el modelo entre solicitudes.
MODELO_ESTADO: dict = {"tokenizer": None, "modelo": None}

# --- Rate limiting: ventana deslizante en memoria, por IP de cliente ---
RATE_LIMIT_MAX_SOLICITUDES = int(os.environ.get("RATE_LIMIT_MAX_SOLICITUDES", "10"))
RATE_LIMIT_VENTANA_SEGUNDOS = int(os.environ.get("RATE_LIMIT_VENTANA_SEGUNDOS", "60"))

_rate_limit_lock = threading.Lock()
# IP -> lista de timestamps (time.monotonic()) de solicitudes recientes.
# Nota: no se purgan IPs que dejan de usarse (solo sus timestamps viejos
# dentro de cada solicitud nueva) -- para el tamaño de tráfico esperado
# en este proyecto no vale la pena la complejidad extra de un TTL de
# limpieza; si esto corriera con tráfico real sostenido de muchas IPs
# distintas, sería lo primero a revisar.
_rate_limit_historial: dict[str, list[float]] = defaultdict(list)

# --- Métricas: SOLO contadores agregados, nunca texto. En memoria, se
# reinician al reiniciar el proceso (sin persistencia a disco) ---
METRICAS = {
    "total_solicitudes": 0,
    "traducciones_exitosas": 0,
    "rechazadas_validacion": 0,
    "rechazadas_rate_limit": 0,
}
_metricas_lock = threading.Lock()


def _incrementar_metrica(nombre: str) -> None:
    with _metricas_lock:
        METRICAS[nombre] += 1


def _verificar_rate_limit(cliente_id: str) -> None:
    """Lanza HTTPException(429) si `cliente_id` superó el límite dentro
    de la ventana deslizante. No recibe ni guarda ningún dato del
    contenido de la solicitud -- solo la IP y el momento en que llegó."""
    ahora = time.monotonic()
    limite_inferior = ahora - RATE_LIMIT_VENTANA_SEGUNDOS
    with _rate_limit_lock:
        historial = _rate_limit_historial[cliente_id]
        while historial and historial[0] < limite_inferior:
            historial.pop(0)
        if len(historial) >= RATE_LIMIT_MAX_SOLICITUDES:
            _incrementar_metrica("rechazadas_rate_limit")
            raise HTTPException(
                status_code=429,
                detail=(
                    f"Demasiadas solicitudes. Máximo {RATE_LIMIT_MAX_SOLICITUDES} cada "
                    f"{RATE_LIMIT_VENTANA_SEGUNDOS} segundos por cliente. Espera unos "
                    "segundos y vuelve a intentar."
                ),
                headers={"Retry-After": str(RATE_LIMIT_VENTANA_SEGUNDOS)},
            )
        historial.append(ahora)


def _cargar_modelo_real():
    """Importa torch/transformers/peft solo aquí adentro -- así el
    resto del módulo (y por lo tanto las pruebas con SKIP_MODEL_LOAD=1)
    no necesitan esas dependencias instaladas para poder importarse."""
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "finetuning"))
    from probar_baseline import MODEL_ID  # mismo modelo base que el resto del pipeline

    token = os.environ.get("HF_TOKEN") or None
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=token)
    modelo_base = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        token=token,
        torch_dtype=torch.bfloat16,
        device_map="auto" if torch.cuda.is_available() else "cpu",
    )
    modelo = PeftModel.from_pretrained(modelo_base, str(ADAPTER_DIR))
    modelo.eval()
    return tokenizer, modelo


def _generar_traduccion(tokenizer, modelo, texto: str) -> str:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "finetuning"))
    from probar_baseline import traducir as _traducir_con_modelo

    return _traducir_con_modelo(tokenizer, modelo, texto)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.environ.get("SKIP_MODEL_LOAD") == "1":
        # Usado solo por api/test_main.py -- nunca en un despliegue real.
        yield
        return
    tokenizer, modelo = _cargar_modelo_real()
    MODELO_ESTADO["tokenizer"] = tokenizer
    MODELO_ESTADO["modelo"] = modelo
    yield
    MODELO_ESTADO["tokenizer"] = None
    MODELO_ESTADO["modelo"] = None


app = FastAPI(title="Traductor de jerga/dialectos del español", lifespan=lifespan)


@app.exception_handler(Exception)
async def manejador_errores_no_previstos(request: Request, exc: Exception):
    # Cualquier excepción no prevista (bug, fallo del modelo, lo que
    # sea) devuelve un mensaje genérico y entendible -- nunca el
    # traceback crudo. El detalle real queda en los logs del proceso
    # del lado del servidor (sin exponerlo al cliente), no en la
    # respuesta HTTP.
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocurrió un error inesperado procesando la solicitud. Intenta de nuevo más tarde."},
    )


@app.exception_handler(RequestValidationError)
async def manejador_error_validacion(request: Request, exc: RequestValidationError):
    # Sin este manejador, un 422 de Pydantic (longitud, campo
    # faltante) nunca pasa por el cuerpo de traducir() -- y por lo
    # tanto no quedaba contado en METRICAS["rechazadas_validacion"],
    # dejando las métricas agregadas incompletas/engañosas para
    # auditar. Este manejador solo cuenta (nunca guarda el contenido
    # que falló la validación) y reusa el mismo formato de error claro
    # que ya da FastAPI por default.
    if request.url.path == "/traducir":
        _incrementar_metrica("total_solicitudes")
        _incrementar_metrica("rechazadas_validacion")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


class SolicitudTraduccion(BaseModel):
    texto: str = Field(..., min_length=1, max_length=500, description="Texto en español a traducir")
    dialecto: str | None = Field(
        default=None,
        description="Dialecto de origen, opcional e informativo — todavía no cambia qué modelo/adaptador se usa (eso es trabajo de cuando existan los Generadores 2-3 fusionados, Fase 3).",
    )


class RespuestaTraduccion(BaseModel):
    traduccion: str
    dialecto: str | None = None


@app.get("/salud")
def salud():
    return {"estado": "ok"}


@app.get("/metricas")
def metricas():
    # Copia superficial: nunca se expone (ni existe) el diccionario
    # interno con datos de ninguna solicitud individual, solo estos
    # 4 contadores agregados.
    return dict(METRICAS)


@app.post("/traducir", response_model=RespuestaTraduccion)
def traducir(solicitud: SolicitudTraduccion, request: Request):
    _incrementar_metrica("total_solicitudes")

    cliente_id = request.client.host if request.client else "desconocido"
    _verificar_rate_limit(cliente_id)

    texto = solicitud.texto.strip()
    if not texto:
        _incrementar_metrica("rechazadas_validacion")
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío o ser solo espacios.")

    tokenizer = MODELO_ESTADO["tokenizer"]
    modelo = MODELO_ESTADO["modelo"]
    if tokenizer is None or modelo is None:
        raise HTTPException(status_code=503, detail="El modelo todavía no está cargado. Intenta de nuevo en unos segundos.")

    traduccion = _generar_traduccion(tokenizer, modelo, texto)
    _incrementar_metrica("traducciones_exitosas")
    return RespuestaTraduccion(traduccion=traduccion, dialecto=solicitud.dialecto)
