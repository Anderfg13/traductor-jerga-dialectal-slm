"""
api/main.py

Servicio de traducción vía API REST. Expone:
  - POST /traducir: recibe texto en español (y un dialecto opcional,
    informativo), devuelve la traducción generada por el modelo
    ajustado con LoRA del Generador 1 (Sesión 19,
    `finetuning/checkpoints/generador1/adapter/`).
  - GET /salud: healthcheck simple para confirmar que el proceso está
    vivo, sin depender de que el modelo ya haya terminado de cargar.

El modelo se carga UNA SOLA VEZ al iniciar el servicio (evento
`lifespan` de FastAPI), no en cada solicitud — cargar un modelo de 3B
por request destruiría la latencia.

Cargar el modelo real requiere la pila pesada de ML (torch,
transformers, peft) y el adaptador entrenado. Para poder probar la
CAPA DE API (validación de entrada, códigos de estado, forma de la
respuesta) sin esa pila instalada ni descargar el modelo de 3B, la
carga real se salta si la variable de entorno `SKIP_MODEL_LOAD=1` está
presente — así es como corre `api/test_main.py`.

**El servicio SÍ se levantó localmente con el modelo real** (Sesión
27) — a diferencia del entrenamiento (inviable en CPU, ver
`CONTEXTO_PROYECTO.md`), una sola solicitud de inferencia sí termina
en un tiempo razonable de probar, aunque no rápido: **~50-80 segundos
por traducción en CPU local**, muy por encima del objetivo de "unos
pocos segundos". La traducción en sí es correcta y coherente — el
problema es solo de latencia, no de funcionalidad. Cumplir la latencia
objetivo sí necesita GPU (Colab o el entorno de despliegue de la
Sesión 26), consistente con la política de cómputo pesado del proyecto
— para UNA sola solicitud (no cientos) la máquina local alcanza para
probar que el endpoint funciona de principio a fin, pero no para medir
la latencia real de producción.

Uso (requiere `pip install -r requirements.txt` completo, con GPU o
paciencia en CPU para la carga inicial):
    uvicorn api.main:app --reload

Prueba rápida una vez levantado:
    curl http://localhost:8000/salud
    curl -X POST http://localhost:8000/traducir \
        -H "Content-Type: application/json" \
        -d "{\"texto\": \"Que chimba, parcero!\"}"

Pruebas de la capa de API sin el modelo real:
    SKIP_MODEL_LOAD=1 python -m pytest api/test_main.py
"""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ADAPTER_DIR = Path(__file__).resolve().parent.parent / "finetuning" / "checkpoints" / "generador1" / "adapter"

# Estado del modelo cargado, poblado una sola vez en el lifespan de
# abajo. No es un objeto global "mágico": es explícitamente el único
# lugar del módulo que guarda el modelo entre solicitudes.
MODELO_ESTADO: dict = {"tokenizer": None, "modelo": None}


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


@app.post("/traducir", response_model=RespuestaTraduccion)
def traducir(solicitud: SolicitudTraduccion):
    texto = solicitud.texto.strip()
    if not texto:
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío o ser solo espacios.")

    tokenizer = MODELO_ESTADO["tokenizer"]
    modelo = MODELO_ESTADO["modelo"]
    if tokenizer is None or modelo is None:
        raise HTTPException(status_code=503, detail="El modelo todavía no está cargado.")

    traduccion = _generar_traduccion(tokenizer, modelo, texto)
    return RespuestaTraduccion(traduccion=traduccion, dialecto=solicitud.dialecto)
