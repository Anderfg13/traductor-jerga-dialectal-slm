"""
Prueba manual de la plantilla de derivacion (Sesion 6) contra UNO de los
3 LLMs generadores, sobre semillas reales de seeds/lote_01.json.

Construye el prompt de generation/prompt_derivacion.md, lo manda al
generador elegido, y valida que la respuesta:
  1. Parsee como JSON valido.
  2. Tenga entre 5 y 8 variantes.
  3. No haya cambiado el dialecto_region de la semilla original.

Uso:
    python generation/probar_prompt_derivacion.py --generador cohere --ids sem-007 sem-018
    python generation/probar_prompt_derivacion.py --generador groq --ids sem-007 sem-018
    python generation/probar_prompt_derivacion.py --generador google --ids sem-007 sem-018

Requiere las variables de entorno del generador elegido (ver
.env.example): GROQ_API_KEY, COHERE_API_KEY o GOOGLE_API_KEY.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SEEDS_PATH = Path(__file__).resolve().parent.parent / "seeds" / "lote_01.json"
MAX_TOKENS = 1500

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


def llamar_groq(prompt: str) -> str:
    from groq import Groq

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resp = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=MAX_TOKENS,
        reasoning_effort="low",
    )
    return resp.choices[0].message.content or ""


def llamar_cohere(prompt: str) -> str:
    import cohere

    client = cohere.ClientV2(api_key=os.environ["COHERE_API_KEY"])
    resp = client.chat(
        model="command-r-08-2024",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=MAX_TOKENS,
    )
    return resp.message.content[0].text


def llamar_google(prompt: str) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    resp = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=MAX_TOKENS,
            thinking_config=types.ThinkingConfig(thinking_level="minimal"),
        ),
    )
    return resp.text or ""


GENERADORES = {
    "groq": llamar_groq,
    "cohere": llamar_cohere,
    "google": llamar_google,
}


def limpiar_json(texto: str) -> str:
    """Quita bloques de código ```json ... ``` si el modelo los agrega
    a pesar de la instrucción de no hacerlo."""
    texto = texto.strip()
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", texto, re.DOTALL)
    return match.group(1) if match else texto


def validar_salida(salida_json: dict, semilla: dict) -> list[str]:
    errores = []
    variantes = salida_json.get("variantes")
    if not isinstance(variantes, list):
        errores.append("'variantes' no es una lista")
        return errores
    if not (5 <= len(variantes) <= 8):
        errores.append(f"se esperaban 5-8 variantes, llegaron {len(variantes)}")
    campos_esperados = {"texto_dialectal", "traduccion", "registro", "contexto_uso"}
    for i, v in enumerate(variantes):
        faltantes = campos_esperados - set(v.keys())
        if faltantes:
            errores.append(f"variante {i}: faltan campos {faltantes}")
    return errores


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generador", choices=GENERADORES.keys(), required=True)
    parser.add_argument("--ids", nargs="+", required=True, help="ids de semillas en seeds/lote_01.json")
    args = parser.parse_args()

    semillas = {s["id"]: s for s in json.loads(SEEDS_PATH.read_text(encoding="utf-8"))}
    llamar = GENERADORES[args.generador]

    ok = True
    for seed_id in args.ids:
        semilla = semillas.get(seed_id)
        if semilla is None:
            print(f"--- {seed_id}: no encontrada en {SEEDS_PATH.name} ---")
            ok = False
            continue

        print(f"--- {seed_id} ({semilla['texto_original']!r}, {semilla['dialecto_region']}) ---")
        prompt = construir_prompt(semilla)
        try:
            texto = llamar(prompt)
        except KeyError as e:
            print(f"  FALTA VARIABLE DE ENTORNO {e}")
            ok = False
            continue
        except Exception as e:  # noqa: BLE001 - reportar cualquier fallo de API
            print(f"  ERROR ({type(e).__name__}): {e}")
            ok = False
            continue

        try:
            salida = json.loads(limpiar_json(texto))
        except json.JSONDecodeError as e:
            print(f"  JSON INVALIDO: {e}\n  --- respuesta cruda ---\n{texto}\n")
            ok = False
            continue

        errores = validar_salida(salida, semilla)
        if errores:
            print(f"  VALIDACION FALLIDA: {errores}")
            ok = False
        else:
            print(f"  OK: {len(salida['variantes'])} variantes, JSON valido")
        print(json.dumps(salida, ensure_ascii=False, indent=2))
        print()

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
