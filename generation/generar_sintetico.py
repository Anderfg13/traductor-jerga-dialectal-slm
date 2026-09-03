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

Uso:
    python generation/generar_sintetico.py
    python generation/generar_sintetico.py --ids sem-007 sem-018 sem-006
    python generation/generar_sintetico.py --max-reintentos 5 --espera-base 2

Variables de entorno (definidas en .env, ver .env.example):
    GROQ_API_KEY   -- clave de API de Groq (obligatoria)
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

SEEDS_PATH = Path(__file__).resolve().parent.parent / "seeds" / "lote_01.json"
RAW_DIR = Path(__file__).resolve().parent / "raw" / "generador1"
MODEL = "openai/gpt-oss-20b"
MAX_TOKENS = 1500

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


def llamar_groq_con_reintentos(client, prompt: str, max_reintentos: int, espera_base: float) -> str:
    """Llama a Groq con backoff exponencial ante errores transitorios
    (429 rate limit, timeouts, errores 5xx). Respeta el header
    Retry-After cuando la API lo entrega. Relanza la excepcion tras
    agotar los reintentos, o de inmediato ante errores no transitorios
    (ej. clave invalida, prompt rechazado)."""
    import groq

    for intento in range(max_reintentos + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=MAX_TOKENS,
                reasoning_effort="low",
            )
            return resp.choices[0].message.content or ""
        except (groq.RateLimitError, groq.APIConnectionError, groq.APITimeoutError, groq.InternalServerError) as e:
            if intento == max_reintentos:
                raise
            espera = espera_base * (2 ** intento)
            retry_after = getattr(getattr(e, "response", None), "headers", {}).get("retry-after")
            if retry_after:
                try:
                    espera = max(espera, float(retry_after))
                except ValueError:
                    pass
            print(f"    {type(e).__name__}, reintento {intento + 1}/{max_reintentos} en {espera:.0f}s...")
            time.sleep(espera)

    raise RuntimeError("no debería llegar aquí")  # pragma: no cover


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ids", nargs="+", help="procesar solo estos ids de semilla (por defecto: todas)")
    parser.add_argument("--max-reintentos", type=int, default=5, help="reintentos ante error transitorio (default: 5)")
    parser.add_argument("--espera-base", type=float, default=2.0, help="segundos base del backoff exponencial (default: 2.0)")
    args = parser.parse_args()

    semillas = json.loads(SEEDS_PATH.read_text(encoding="utf-8"))
    if args.ids:
        semillas_por_id = {s["id"]: s for s in semillas}
        faltantes = [i for i in args.ids if i not in semillas_por_id]
        if faltantes:
            print(f"ERROR: ids no encontrados en {SEEDS_PATH.name}: {faltantes}")
            return 1
        semillas = [semillas_por_id[i] for i in args.ids]

    try:
        from groq import Groq

        client = Groq(api_key=os.environ["GROQ_API_KEY"])
    except KeyError:
        print("ERROR: falta la variable de entorno GROQ_API_KEY (ver .env.example)")
        return 1

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    ok = True
    procesadas = 0
    saltadas = 0
    for semilla in semillas:
        seed_id = semilla["id"]
        salida_path = RAW_DIR / f"{seed_id}.json"

        if salida_path.exists():
            print(f"--- {seed_id}: ya existe, se salta ---")
            saltadas += 1
            continue

        print(f"--- {seed_id} ({semilla['texto_original']!r}, {semilla['dialecto_region']}) ---")
        prompt = construir_prompt(semilla)
        try:
            texto = llamar_groq_con_reintentos(client, prompt, args.max_reintentos, args.espera_base)
        except Exception as e:  # noqa: BLE001 - reportar cualquier fallo y seguir con la siguiente semilla
            print(f"  ERROR ({type(e).__name__}): {e}")
            ok = False
            continue

        registro = {
            "seed_id": seed_id,
            "generador": "groq",
            "modelo": MODEL,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "prompt": prompt,
            "respuesta_cruda": texto,
        }
        salida_path.write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  OK: guardado en {salida_path.relative_to(SEEDS_PATH.parent.parent)}")
        procesadas += 1

    print(f"\nTotal: {procesadas} generadas, {saltadas} ya existían, {'sin errores' if ok else 'con errores (ver arriba)'}.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
