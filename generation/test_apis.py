"""
Prueba minima de conectividad para los 3 LLMs generadores del proyecto.

Hace UNA sola llamada corta (prompt breve, max_tokens/output bajo) a cada
API para confirmar que las credenciales funcionan, sin gastar cuota de mas.

Generadores usados (los 3 con capa gratuita, a la fecha de escritura
de este script):
  1. Groq    -> openai/gpt-oss-20b (capa gratuita)
  2. Cohere  -> command-r-08-2024 (capa gratuita "trial", 1000 llamadas/mes)
  3. Google  -> gemini-3.6-flash (capa gratuita, via el SDK `google-genai`)

Los proveedores retiran/renombran modelos con cierta frecuencia. Si
alguno de estos IDs deja de existir, revisa la lista vigente de
modelos del proveedor (ver enlaces en README.md) y actualiza la
constante MODEL de la función correspondiente abajo.

Uso:
    python generation/test_apis.py

Requiere las variables de entorno (definidas en .env, ver .env.example):
    GROQ_API_KEY, COHERE_API_KEY, GOOGLE_API_KEY
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

PROMPT = "Responde en una sola frase corta: ¿qué es una jerga dialectal?"
# openai/gpt-oss-20b y gemini-3.6-flash son modelos de "razonamiento":
# gastan una parte del presupuesto de tokens pensando antes de responder,
# por eso el limite es mas alto que una llamada normal (se desactiva el
# razonamiento explicitamente donde el proveedor lo permite, ver abajo).
MAX_TOKENS = 300


def test_groq() -> tuple[str, str]:
    from groq import Groq

    api_key = os.environ["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
    model = "openai/gpt-oss-20b"
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": PROMPT}],
        max_tokens=MAX_TOKENS,
        reasoning_effort="low",  # gpt-oss razona por defecto; lo bajamos para no gastar el limite de tokens pensando
    )
    texto = resp.choices[0].message.content
    return model, (texto or "").strip()


def test_cohere() -> tuple[str, str]:
    import cohere

    api_key = os.environ["COHERE_API_KEY"]
    client = cohere.ClientV2(api_key=api_key)
    model = "command-r-08-2024"
    resp = client.chat(
        model=model,
        messages=[{"role": "user", "content": PROMPT}],
        max_tokens=MAX_TOKENS,
    )
    return model, resp.message.content[0].text.strip()


def test_google() -> tuple[str, str]:
    from google import genai
    from google.genai import types

    api_key = os.environ["GOOGLE_API_KEY"]
    client = genai.Client(api_key=api_key)
    model_name = "gemini-3.6-flash"
    resp = client.models.generate_content(
        model=model_name,
        contents=PROMPT,
        config=types.GenerateContentConfig(
            max_output_tokens=MAX_TOKENS,
            thinking_config=types.ThinkingConfig(thinking_level="minimal"),  # gemini 3.x usa thinking_level, no thinking_budget
        ),
    )
    return model_name, (resp.text or "").strip()


def main() -> int:
    generadores = [
        ("Groq", test_groq),
        ("Cohere", test_cohere),
        ("Google", test_google),
    ]

    ok = True
    for nombre, fn in generadores:
        print(f"--- {nombre} ---")
        try:
            model, texto = fn()
            print(f"  modelo: {model}")
            print(f"  respuesta: {texto}")
            if texto:
                print("  estado: OK\n")
            else:
                ok = False
                print("  estado: RESPUESTA VACIA (credenciales OK, pero no llego texto; revisa MAX_TOKENS o el modelo)\n")
        except KeyError as e:
            ok = False
            print(f"  estado: FALTA VARIABLE DE ENTORNO {e}\n")
        except Exception as e:  # noqa: BLE001 - queremos reportar cualquier fallo de credenciales/red
            ok = False
            print(f"  estado: ERROR ({type(e).__name__}): {e}\n")

    if ok:
        print("Las 3 APIs respondieron correctamente.")
        return 0
    else:
        print("Al menos una API fallo. Revisa las claves en tu archivo .env.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
