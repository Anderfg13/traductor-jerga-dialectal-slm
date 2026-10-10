"""
evaluation/comparar_comerciales.py

PI3: el modelo pequeño ajustado frente a traductores dedicados (Google
Translate y DeepL) sobre el test común. Necesita claves de API en .env:

    GOOGLE_TRANSLATE_API_KEY=...   (Cloud Translation v2)
    DEEPL_API_KEY=...              (las claves gratuitas terminan en ":fx")

Si falta una clave, ese sistema se omite y el informe lo dice (no se
inventa ningún resultado). Las traducciones se guardan en
evaluation/predicciones_comerciales/<sistema>.json (se reanuda si se
interrumpe). Informe: evaluation/comparacion_pi3_comerciales.md

    python evaluation/comparar_comerciales.py --probar        # 3 frases por sistema
    python evaluation/comparar_comerciales.py                 # todo
    python evaluation/comparar_comerciales.py --solo-informe

Ojo: un traductor dedicado no recibe el prompt de sistema; traduce el texto
tal cual, por lo que la comparación es contra el producto, no contra un LLM.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
import sacrebleu
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
EVAL = Path(__file__).resolve().parent
CACHE = EVAL / "predicciones_comerciales"
load_dotenv(RAIZ / ".env")

SISTEMAS = {"google-translate": "GOOGLE_TRANSLATE_API_KEY", "deepl": "DEEPL_API_KEY"}
NUESTROS = [("baseline", "Qwen2.5-3B base (sin ajustar)"), ("generador3", "SLM ajustado: Generador 3"),
            ("mezcla", "SLM ajustado: mezcla"), ("mergekit_linear", "SLM ajustado: fusión lineal (mergekit)")]


def traducir_google(clave, texto):
    r = requests.post("https://translation.googleapis.com/language/translate/v2", params={"key": clave},
                      json={"q": texto, "source": "es", "target": "en", "format": "text"}, timeout=30)
    r.raise_for_status()
    return r.json()["data"]["translations"][0]["translatedText"].strip()


def traducir_deepl(clave, texto):
    host = "api-free.deepl.com" if clave.endswith(":fx") else "api.deepl.com"
    r = requests.post(f"https://{host}/v2/translate", headers={"Authorization": f"DeepL-Auth-Key {clave}"},
                      json={"text": [texto], "source_lang": "ES", "target_lang": "EN-US"}, timeout=30)
    r.raise_for_status()
    return r.json()["translations"][0]["text"].strip()


TRADUCTORES = {"google-translate": traducir_google, "deepl": traducir_deepl}


def traducir_con_reintento(fn, clave, texto, reintentos=5):
    for i in range(reintentos + 1):
        try:
            return fn(clave, texto)
        except requests.HTTPError as e:
            cod = e.response.status_code if e.response is not None else 0
            if cod in (401, 403, 456):  # clave inválida o cuota agotada: no tiene caso reintentar
                raise
            if i == reintentos:
                raise
            time.sleep(min(2 * 2 ** i, 30))
        except requests.RequestException:
            if i == reintentos:
                raise
            time.sleep(min(2 * 2 ** i, 30))


def correr(nombre, test, limite=None):
    clave = os.environ.get(SISTEMAS[nombre], "").strip()
    if not clave:
        print(f"{nombre}: falta {SISTEMAS[nombre]} en .env; se omite")
        return False
    CACHE.mkdir(exist_ok=True)
    ruta = CACHE / f"{nombre}.json"
    cache = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}
    pendientes = [t for t in test if t["texto_dialectal"] not in cache][:limite]
    for k, item in enumerate(pendientes, 1):
        cache[item["texto_dialectal"]] = traducir_con_reintento(TRADUCTORES[nombre], clave, item["texto_dialectal"])
        if k % 20 == 0:
            ruta.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"  {nombre}: {k}/{len(pendientes)}", flush=True)
    ruta.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{nombre}: {len(cache)} traducciones en caché")
    return True


def metricas(pares):
    hip, ref = [h for h, _ in pares], [[r for _, r in pares]]
    return sacrebleu.corpus_bleu(hip, ref).score, sacrebleu.corpus_chrf(hip, ref).score


def informe(test):
    sistemas = {}
    for n in SISTEMAS:
        r = CACHE / f"{n}.json"
        if r.exists():
            sistemas[n] = json.loads(r.read_text(encoding="utf-8"))
    ours = {}
    for n, et in NUESTROS:
        r = EVAL / "predicciones" / f"{n}.json"
        if r.exists():
            ours[et] = {x["texto_dialectal"]: x["traduccion_modelo"] for x in json.loads(r.read_text(encoding="utf-8"))}
    L = ["# PI3: modelo pequeño frente a traductores dedicados (Google Translate, DeepL)", "",
         "Generado por `evaluation/comparar_comerciales.py`. Mismo test común. **Lectura con cautela**: 9 semillas de prueba, una corrida, "
         "referencias mayormente sintéticas, sin evaluación humana.", ""]
    faltan = [n for n in SISTEMAS if n not in sistemas]
    if faltan:
        L += [f"**No se evaluaron: {', '.join(faltan)}** (sin clave de API o sin traducciones en caché). No hay resultado para ellos.", ""]
    if not sistemas:
        L += ["Sin ningún sistema evaluado no hay comparación que mostrar.", ""]
    else:
        for titulo, items in [("Test común completo", test), ("Solo referencias humanas (`oro`, sin sesgo de LLM)", [i for i in test if i["fuente"] == "oro"])]:
            L += [f"## {titulo} (n = {len(items)})", "", "| Sistema | BLEU | chrF |", "|---|---|---|"]
            todos = {**{n: p for n, p in sistemas.items()}, **ours}
            for n, p in todos.items():
                pares = [(p[i["texto_dialectal"]], i["traduccion"]) for i in items if i["texto_dialectal"] in p]
                if pares:
                    b, c = metricas(pares)
                    L.append(f"| {n} ({len(pares)}) | {b:.1f} | {c:.1f} |")
            L.append("")
        L += ["Un traductor dedicado no usa el prompt de sistema del proyecto ni conoce el dialecto: si queda por debajo, es información sobre "
              "la jerga dialectal, no un juicio general de calidad.", ""]
    texto = "\n".join(L)
    (EVAL / "comparacion_pi3_comerciales.md").write_text(texto, encoding="utf-8")
    print(texto)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--probar", action="store_true")
    p.add_argument("--solo-informe", action="store_true")
    a = p.parse_args()
    test = json.loads((EVAL / "test_comun.json").read_text(encoding="utf-8"))
    if not a.solo_informe:
        for s in SISTEMAS:
            correr(s, test, limite=3 if a.probar else None)
    if not a.probar:
        informe(test)
    return 0


if __name__ == "__main__":
    sys.exit(main())
