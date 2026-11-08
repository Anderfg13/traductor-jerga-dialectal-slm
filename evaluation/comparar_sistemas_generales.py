"""
evaluation/comparar_sistemas_generales.py

PI3: ¿es competitivo el modelo pequeño ajustado frente a sistemas de
propósito general? Traduce el test común (evaluation/test_comun.json) con
LLMs grandes de propósito general, por API, con EXACTAMENTE el mismo
prompt de sistema que el modelo pequeño (finetuning/probar_baseline.py),
y calcula BLEU/chrF contra las mismas referencias.

Sistemas (todos en capa gratuita):
  - gpt-oss-20b (Groq), command-r (Cohere), gemini-3.5-flash-lite (Google):
    son los 3 LLMs GENERADORES de los datos de entrenamiento. Tienen una
    ventaja circular: las referencias de "su" fuente las escribió ese mismo
    modelo. Por eso cada uno se evalúa EXCLUYENDO sus propias referencias.
  - gpt-oss-120b y qwen3.8-27b (Groq): grandes y que NO generaron datos.
    Son la comparación sin ventaja circular (gpt-oss-120b es de la misma
    familia que el generador 1; qwen3.8-27b, de la misma que nuestro base).

NO incluye Google Translate ni DeepL (no hay clave): son LLMs de propósito
general, no productos de traducción automática dedicados.

    python evaluation/comparar_sistemas_generales.py --probar          # 3 frases por sistema
    python evaluation/comparar_sistemas_generales.py                   # todo (reanudable)
    python evaluation/comparar_sistemas_generales.py --solo-informe    # solo reconstruye el informe

Traducciones en evaluation/predicciones_generales/<sistema>.json (caché:
se reanuda si se interrumpe). Informe: evaluation/comparacion_pi3_sistemas_generales.md
"""

import argparse
import json
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import sacrebleu
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "finetuning"))
import probar_baseline  # noqa: E402

load_dotenv(RAIZ / ".env")

EVAL = Path(__file__).resolve().parent
CACHE = EVAL / "predicciones_generales"
SYSTEM_PROMPT = probar_baseline.SYSTEM_PROMPT

# nombre -> (proveedor, modelo, fuente de datos que él mismo generó o None, parámetros extra)
SISTEMAS = {
    "gpt-oss-20b": ("groq", "openai/gpt-oss-20b", "generador1", {"reasoning_effort": "low"}),
    "command-r": ("cohere", "command-r-08-2024", "generador2", {}),
    "gemini-3.5-flash-lite": ("google", "gemini-3.5-flash-lite", "generador3", {}),
    "gpt-oss-120b": ("groq", "openai/gpt-oss-120b", None, {"reasoning_effort": "low"}),
    "qwen3.8-27b": ("groq", "qwen/qwen3.8-27b", None, {}),
}


def _transitorio(e):
    cod = getattr(e, "status_code", None) or getattr(e, "code", None)
    if isinstance(cod, int) and (cod == 429 or 500 <= cod < 600):
        return True
    return any(k in type(e).__name__ for k in ("RateLimit", "TooManyRequests", "Timeout", "Connection", "InternalServer", "ServiceUnavailable"))


def _cliente(proveedor):
    if proveedor == "groq":
        from groq import Groq
        return Groq(api_key=os.environ["GROQ_API_KEY"])
    if proveedor == "cohere":
        import cohere
        return cohere.ClientV2(api_key=os.environ["COHERE_API_KEY"])
    from google import genai
    return genai.Client(api_key=os.environ["GOOGLE_API_KEY"])


def _traducir_una_vez(proveedor, cliente, modelo, extra, texto):
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": texto}]
    if proveedor == "groq":
        r = cliente.chat.completions.create(model=modelo, messages=msgs, max_tokens=600, temperature=0, **extra)
        return (r.choices[0].message.content or "").strip()
    if proveedor == "cohere":
        r = cliente.chat(model=modelo, messages=msgs, max_tokens=300, temperature=0)
        return r.message.content[0].text.strip()
    from google.genai import types
    r = cliente.models.generate_content(
        model=modelo, contents=texto,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, max_output_tokens=400, temperature=0,
                                           thinking_config=types.ThinkingConfig(thinking_level="minimal")))
    return (r.text or "").strip()


def traducir(proveedor, cliente, modelo, extra, texto, reintentos=6):
    for i in range(reintentos + 1):
        try:
            return _traducir_una_vez(proveedor, cliente, modelo, extra, texto)
        except Exception as e:  # noqa: BLE001
            if not _transitorio(e) or i == reintentos:
                raise
            time.sleep(min(2 * 2 ** i, 60))


def correr_sistema(nombre, test, hilos, limite=None):
    proveedor, modelo, _, extra = SISTEMAS[nombre]
    CACHE.mkdir(exist_ok=True)
    ruta = CACHE / f"{nombre}.json"
    cache = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}
    pendientes = [t for t in test if t["texto_dialectal"] not in cache][:limite]
    if not pendientes:
        print(f"{nombre}: nada pendiente ({len(cache)} en caché)")
        return
    cliente = _cliente(proveedor)
    lat = []

    def uno(item):
        t0 = time.monotonic()
        try:
            out = traducir(proveedor, cliente, modelo, extra, item["texto_dialectal"])
        except Exception as e:  # noqa: BLE001
            return item["texto_dialectal"], None, f"{type(e).__name__}: {str(e)[:120]}", 0
        return item["texto_dialectal"], out, None, time.monotonic() - t0

    errores = []
    with ThreadPoolExecutor(max_workers=hilos) as ex:
        for k, (texto, out, err, dt) in enumerate(ex.map(uno, pendientes), 1):
            if out is None or not out:
                errores.append((texto, err or "respuesta vacía"))
                continue
            cache[texto] = out
            lat.append(dt)
            if k % 20 == 0:
                ruta.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
                print(f"  {nombre}: {k}/{len(pendientes)}", flush=True)
    ruta.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    med = f"{statistics.median(lat):.1f} s" if lat else "—"
    print(f"{nombre}: {len(cache)} traducciones en caché; {len(errores)} errores; latencia mediana {med}")
    for t, e in errores[:3]:
        print(f"   ERROR en {t[:40]!r}: {e}")


def metricas(pares):
    hip = [h for h, _ in pares]
    ref = [[r for _, r in pares]]
    return sacrebleu.corpus_bleu(hip, ref).score, sacrebleu.corpus_chrf(hip, ref).score


def informe(test):
    # nuestros modelos
    ours = {}
    for nombre, et in [("baseline", "Qwen2.5-3B base (sin ajustar)"), ("generador3", "SLM ajustado: Generador 3"),
                       ("mezcla", "SLM ajustado: mezcla"), ("mergekit_linear", "SLM ajustado: fusión lineal (mergekit)"),
                       ("mergekit_ties", "SLM ajustado: fusión TIES (mergekit)")]:
        r = EVAL / "predicciones" / f"{nombre}.json"
        if r.exists():
            ours[et] = {x["texto_dialectal"]: x["traduccion_modelo"] for x in json.loads(r.read_text(encoding="utf-8"))}
    grandes = {}
    for nombre in SISTEMAS:
        r = CACHE / f"{nombre}.json"
        if r.exists():
            grandes[nombre] = json.loads(r.read_text(encoding="utf-8"))

    def evaluar(pred, items):
        pares = [(pred[i["texto_dialectal"]], i["traduccion"]) for i in items if i["texto_dialectal"] in pred]
        return (len(pares),) + metricas(pares) if pares else (0, float("nan"), float("nan"))

    L = ["# PI3: modelo pequeño ajustado frente a sistemas de propósito general", "",
         "Generado por `evaluation/comparar_sistemas_generales.py`. Mismo test común (`evaluation/test_comun.json`), mismo prompt de sistema, "
         "BLEU/chrF con las mismas referencias. **Lectura con cautela**: 9 semillas de prueba, una corrida, sin evaluación humana.", "",
         "## 1. Solo referencias humanas del banco de semillas (`oro`, n = 9, sin ventaja circular)", "",
         "| Sistema | Parámetros | n | BLEU | chrF |", "|---|---|---|---|---|"]
    oro = [i for i in test if i["fuente"] == "oro"]
    tam = {"gpt-oss-20b": "20B", "command-r": "~32-35B (no verificado)", "gemini-3.5-flash-lite": "no publicado", "gpt-oss-120b": "120B", "qwen3.8-27b": "27B"}
    for et, pred in ours.items():
        n, b, c = evaluar(pred, oro)
        L.append(f"| {et} | 3B (+15 MB de adaptador) | {n} | {b:.1f} | {c:.1f} |")
    for nombre, pred in grandes.items():
        n, b, c = evaluar(pred, oro)
        L.append(f"| {nombre} | {tam[nombre]} | {n} | {b:.1f} | {c:.1f} |")
    L.append("")
    L += ["## 2. Sin ventaja circular: cada generador excluye sus propias referencias", "",
          "Cada fila compara el sistema y los modelos pequeños sobre las **mismas** entradas: las del test común cuya referencia NO escribió "
          "ese sistema. Los sistemas que no fueron generadores usan todo el test común.", ""]
    for nombre, pred in grandes.items():
        propio = SISTEMAS[nombre][2]
        items = [i for i in test if i["fuente"] != propio] if propio else test
        n, b, c = evaluar(pred, items)
        L += [f"### {nombre} ({'excluye `' + propio + '`' if propio else 'test común completo'}; n = {n} traducciones evaluadas de {len(items)} entradas)", "",
              "| Sistema | BLEU | chrF |", "|---|---|---|"]
        L.append(f"| **{nombre}** | {b:.1f} | {c:.1f} |")
        for et, p in ours.items():
            n2, b2, c2 = evaluar(p, items)
            L.append(f"| {et} | {b2:.1f} | {c2:.1f} |")
        L.append("")
    L += ["## Cómo leerlo", "",
          "- Los generadores tienen ventaja en sus propias referencias; por eso la sección 2 las excluye. Aun así, entre los generadores y los "
          "SLM ajustados con sus datos hay una dependencia: el SLM aprendió a imitar a esos LLM.",
          "- No hay Google Translate ni DeepL: son LLMs de propósito general, no sistemas de traducción dedicados.",
          "- BLEU/chrF miden coincidencia con una referencia, no retención de matices.", ""]
    texto = "\n".join(L)
    (EVAL / "comparacion_pi3_sistemas_generales.md").write_text(texto, encoding="utf-8")
    print(texto)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--probar", action="store_true", help="solo 3 frases por sistema, para verificar que funciona")
    p.add_argument("--solo-informe", action="store_true")
    p.add_argument("--sistemas", nargs="+", default=list(SISTEMAS))
    p.add_argument("--hilos", type=int, default=4)
    a = p.parse_args()
    test = json.loads((EVAL / "test_comun.json").read_text(encoding="utf-8"))
    if not a.solo_informe:
        for s in a.sistemas:
            correr_sistema(s, test, a.hilos, limite=3 if a.probar else None)
            if a.probar:
                c = json.loads((CACHE / f"{s}.json").read_text(encoding="utf-8")) if (CACHE / f"{s}.json").exists() else {}
                for t, o in list(c.items())[:3]:
                    print(f"   ES: {t}\n   EN: {o}")
    if not a.probar:
        informe(test)
    return 0


if __name__ == "__main__":
    sys.exit(main())
