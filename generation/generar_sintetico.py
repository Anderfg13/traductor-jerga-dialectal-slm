"""
generation/generar_sintetico.py

Automatiza la generacion sintetica (Semana 2 del calendario) para el
**Generador 1** (Groq, `openai/gpt-oss-20b`, capa gratuita — ver
`.env.example` y `README.md`): aplica la plantilla de derivacion
(`generation/prompt_derivacion.md`, probada manualmente en la Sesion 6)
a cada semilla de `seeds/lote_01.json`.

Que hace:
  1. Lee TODAS las semillas de seeds/lote_01.json (o solo las indicadas
     con --ids, para pruebas).
  2. Para cada semilla que todavia no tenga salida guardada, arma el
     prompt de derivacion y lo manda a la API de Groq.
  3. Si Groq responde con error de limite de tasa (429) u otro error
     transitorio (conexion, timeout, error 5xx del servidor), reintenta
     con backoff exponencial (respeta el header `Retry-After` si la API
     lo manda) antes de darse por vencido con esa semilla.
  4. Guarda la respuesta CRUDA de la API (el texto tal cual lo devolvio
     el modelo, sin parsear ni validar como JSON) en
     generation/raw/generador1/{seed_id}.json, junto con el prompt
     enviado y metadatos basicos — antes de cualquier procesamiento
     posterior, para no perder nada si el script se cae a mitad de
     camino.

Reanudable: si generation/raw/generador1/{seed_id}.json ya existe, esa
semilla se salta (no se vuelve a llamar a la API). Correr el script de
nuevo tras una interrupcion retoma solo las semillas pendientes. Para
forzar regenerar una semilla ya procesada, borra su archivo de salida.

Uso (--generador 1=Groq por defecto, 2=Cohere, 3=Google; --lotes 1 2
usa las semillas de lote_01 y lote_02; las salidas van a
generation/raw/generadorN/):
    python generation/generar_sintetico.py
    python generation/generar_sintetico.py --generador 2 --lotes 1 2
    python generation/generar_sintetico.py --ids sem-007 sem-018 sem-006
    python generation/generar_sintetico.py --max-reintentos 5 --espera-base 2

Variables de entorno (definidas en .env, ver .env.example):
    GROQ_API_KEY / COHERE_API_KEY / GOOGLE_API_KEY -- según --generador
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds"
GENERATION_DIR = Path(__file__).resolve().parent

# Los 3 generadores del proyecto (CONTEXTO_PROYECTO.md). El número es el
# usado en los nombres de carpeta/archivo (raw/generadorN, dataset_generadorN).
GENERADORES = {
    1: {"nombre": "groq", "modelo": "openai/gpt-oss-20b", "env": "GROQ_API_KEY", "max_tokens": 1500},
    2: {"nombre": "cohere", "modelo": "command-r-08-2024", "env": "COHERE_API_KEY", "max_tokens": 2500},
    3: {"nombre": "google", "modelo": "gemini-3.5-flash-lite", "env": "GOOGLE_API_KEY", "max_tokens": 3000},
}

# Misma plantilla que generation/prompt_derivacion.md y
# generation/probar_prompt_derivacion.py (Sesion 6) — se mantiene en
# sync manualmente entre los 3 archivos, decision documentada en
# BITACORA.md.
PLANTILLA = """Eres un lingüista que ayuda a construir un dataset de traducción
español-inglés para jerga y dialectos regionales del español.

Se te da UNA semilla: una expresión real de un dialecto del español,
su traducción de referencia al inglés, y una nota de contexto cultural.

SEMILLA:
- id: {id}
- Expresión original: "{texto_original}"
- Dialecto/región: {dialecto_region}
- Registro original: {registro}
- Traducción de referencia: "{traduccion_referencia}"
- Contexto cultural: {nota_contexto_cultural}

TAREA: genera entre 5 y 8 variantes de esta semilla. Cada variante debe:

1. Conservar el significado real de la expresión. No cambies lo que
   quiere decir, solo cómo y en qué situación se dice.
2. Usar la expresión (o una forma natural muy cercana) dentro de una
   oración de uso real distinta cada vez: varía el CONTEXTO (quién
   habla, a quién, en qué situación), el REGISTRO (formal/informal/
   jerga) y el TONO (serio, en broma, molesto, etc.). No generes solo
   sinónimos de la traducción: cada variante es una oración distinta.
3. Mantener el MISMO dialecto/región que la semilla: {dialecto_region}.
   No inventes un dialecto nuevo ni mezcles esta expresión con
   expresiones de otra región.
4. Incluir su propia traducción correcta al inglés, en el mismo
   registro y tono que la variante en español (no traducción literal
   palabra por palabra).

FORMATO DE SALIDA: responde ÚNICAMENTE con JSON válido, sin texto antes
ni después, sin bloques de código (```), exactamente con esta forma:

{{
  "seed_id": "{id}",
  "variantes": [
    {{
      "texto_dialectal": "...",
      "traduccion": "...",
      "registro": "formal | informal | jerga",
      "contexto_uso": "quién lo dice, a quién, y en qué situación/tono"
    }}
  ]
}}

El arreglo "variantes" debe tener entre 5 y 8 elementos. No agregues
campos ni comentarios fuera del JSON."""


def construir_prompt(semilla: dict) -> str:
    return PLANTILLA.format(**semilla)


def crear_cliente(num_generador: int):
    cfg = GENERADORES[num_generador]
    api_key = os.environ[cfg["env"]]
    if num_generador == 1:
        from groq import Groq

        return Groq(api_key=api_key)
    if num_generador == 2:
        import cohere

        return cohere.ClientV2(api_key=api_key)
    from google import genai

    return genai.Client(api_key=api_key)


def _llamar_una_vez(num_generador: int, client, prompt: str) -> str:
    cfg = GENERADORES[num_generador]
    if num_generador == 1:
        resp = client.chat.completions.create(
            model=cfg["modelo"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=cfg["max_tokens"],
            reasoning_effort="low",
        )
        return resp.choices[0].message.content or ""
    if num_generador == 2:
        resp = client.chat(
            model=cfg["modelo"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=cfg["max_tokens"],
        )
        return resp.message.content[0].text or ""
    from google.genai import types

    resp = client.models.generate_content(
        model=cfg["modelo"],
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=cfg["max_tokens"],
            thinking_config=types.ThinkingConfig(thinking_level="minimal"),
        ),
    )
    return resp.text or ""


def _es_transitorio(e: Exception) -> bool:
    """429, 5xx, timeouts y errores de conexión se reintentan; el resto
    (clave inválida, prompt rechazado) no."""
    codigo = getattr(e, "status_code", None) or getattr(e, "code", None)
    if isinstance(codigo, int) and (codigo == 429 or 500 <= codigo < 600):
        return True
    nombre = type(e).__name__
    return any(k in nombre for k in ("RateLimit", "TooManyRequests", "Timeout", "Connection", "InternalServer", "ServiceUnavailable"))


def llamar_con_reintentos(num_generador: int, client, prompt: str, max_reintentos: int, espera_base: float) -> str:
    """Backoff exponencial ante errores transitorios; respeta el header
    Retry-After si la API lo manda. Relanza tras agotar los reintentos,
    o de inmediato ante errores no transitorios."""
    for intento in range(max_reintentos + 1):
        try:
            return _llamar_una_vez(num_generador, client, prompt)
        except Exception as e:  # noqa: BLE001
            if not _es_transitorio(e) or intento == max_reintentos:
                raise
            espera = espera_base * (2 ** intento)
            headers = getattr(getattr(e, "response", None), "headers", None)
            retry_after = headers.get("retry-after") if hasattr(headers, "get") else None
            if retry_after:
                try:
                    espera = max(espera, float(retry_after))
                except ValueError:
                    pass
            print(f"    {type(e).__name__}, reintento {intento + 1}/{max_reintentos} en {espera:.0f}s...")
            time.sleep(espera)

    raise RuntimeError("no debería llegar aquí")  # pragma: no cover


def cargar_semillas(lotes: list[int]) -> list[dict]:
    semillas = []
    for n in lotes:
        semillas.extend(json.loads((SEEDS_DIR / f"lote_{n:02d}.json").read_text(encoding="utf-8")))
    return semillas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--generador", type=int, choices=sorted(GENERADORES), default=1, help="1=Groq (default), 2=Cohere, 3=Google")
    parser.add_argument("--lotes", type=int, nargs="+", default=[1], help="lotes de semillas a usar, p. ej. 1 2 (default: 1)")
    parser.add_argument("--ids", nargs="+", help="procesar solo estos ids de semilla (por defecto: todas)")
    parser.add_argument("--max-reintentos", type=int, default=5, help="reintentos ante error transitorio (default: 5)")
    parser.add_argument("--espera-base", type=float, default=2.0, help="segundos base del backoff exponencial (default: 2.0)")
    args = parser.parse_args()

    cfg = GENERADORES[args.generador]
    raw_dir = GENERATION_DIR / "raw" / f"generador{args.generador}"

    semillas = cargar_semillas(args.lotes)
    if args.ids:
        semillas_por_id = {s["id"]: s for s in semillas}
        faltantes = [i for i in args.ids if i not in semillas_por_id]
        if faltantes:
            print(f"ERROR: ids no encontrados en los lotes {args.lotes}: {faltantes}")
            return 1
        semillas = [semillas_por_id[i] for i in args.ids]

    try:
        client = crear_cliente(args.generador)
    except KeyError:
        print(f"ERROR: falta la variable de entorno {cfg['env']} (ver .env.example)")
        return 1

    raw_dir.mkdir(parents=True, exist_ok=True)

    ok = True
    procesadas = 0
    saltadas = 0
    for semilla in semillas:
        seed_id = semilla["id"]
        salida_path = raw_dir / f"{seed_id}.json"

        if salida_path.exists():
            print(f"--- {seed_id}: ya existe, se salta ---")
            saltadas += 1
            continue

        print(f"--- {seed_id} ({semilla['texto_original']!r}, {semilla['dialecto_region']}) ---")
        prompt = construir_prompt(semilla)
        try:
            texto = llamar_con_reintentos(args.generador, client, prompt, args.max_reintentos, args.espera_base)
        except Exception as e:  # noqa: BLE001 - reportar cualquier fallo y seguir con la siguiente semilla
            print(f"  ERROR ({type(e).__name__}): {e}")
            ok = False
            continue

        registro = {
            "seed_id": seed_id,
            "generador": cfg["nombre"],
            "modelo": cfg["modelo"],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "prompt": prompt,
            "respuesta_cruda": texto,
        }
        salida_path.write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  OK: guardado en {salida_path.relative_to(GENERATION_DIR.parent)}")
        procesadas += 1

    print(f"\nTotal: {procesadas} generadas, {saltadas} ya existían, {'sin errores' if ok else 'con errores (ver arriba)'}.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
