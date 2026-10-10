"""
evaluation/juez_jev.py

Prueba (exploratoria) de Jev, el modelo de decisión de TypeSafe AI, como
juez automático adicional: no genera texto; para cada traducción devuelve
un puntaje 1-5 de "conserva el sentido de la expresión dialectal".
Es una señal automática más, NO evaluación humana.

Necesita TYPESAFE_API_KEY en .env. Primero valida el juez contra las 9
entradas "oro" (referencia humana): ¿puntúa mejor la referencia humana que
una traducción deliberadamente mala?

    python evaluation/juez_jev.py --validar          # 9 oro: referencia vs. mala vs. modelos
    python evaluation/juez_jev.py                    # test común completo (reanudable)

Salida: evaluation/predicciones_jev/<modelo>.json y evaluation/juez_jev.md
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
EVAL = Path(__file__).resolve().parent
CACHE = EVAL / "predicciones_jev"
load_dotenv(RAIZ / ".env")
URL = "https://api.typesafe.ai/v1/systemone"
MODELOS = {"baseline": "base sin ajustar", "mergekit_linear": "fusión simple", "mezcla": "mezcla"}
DEEPL = EVAL / "predicciones_comerciales" / "deepl.json"

PREGUNTA = {
    "type": "score",
    "instructions": "El texto original es una expresión o frase en español dialectal (jerga regional). Evalúa si la traducción al inglés "
                    "conserva su sentido y matiz real, no solo si es fluida en inglés.",
    "criteria": ["sentido equivocado o inventado", "sentido aproximado, pierde mucho matiz", "sentido correcto con algo de matiz perdido",
                 "sentido correcto y natural en inglés", "sentido y matiz plenamente conservados"],
}


def juzgar(clave, original, traduccion, reintentos=4):
    cuerpo = {"model": "jev-latest", "state": {"original_es": original, "traduccion_en": traduccion}, "questions": {"fidelidad": PREGUNTA}}
    for i in range(reintentos + 1):
        r = requests.post(URL, headers={"Authorization": f"Bearer {clave}"}, json=cuerpo, timeout=60)
        if r.status_code in (429, 500, 502, 503) and i < reintentos:
            time.sleep(2 * 2 ** i)
            continue
        r.raise_for_status()
        a = r.json()["answers"]["fidelidad"]
        return a["score"] + 1, a["confidence"]  # escala 1-5


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--validar", action="store_true")
    a = p.parse_args()
    clave = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if not clave:
        print("Falta TYPESAFE_API_KEY en .env")
        return 1
    test = json.loads((EVAL / "test_comun.json").read_text(encoding="utf-8"))
    items = [t for t in test if t["fuente"] == "oro"] if a.validar else test
    sistemas = {n: {x["texto_dialectal"]: x["traduccion_modelo"] for x in json.loads((EVAL / "predicciones" / f"{n}.json").read_text(encoding="utf-8"))}
                for n in MODELOS}
    if DEEPL.exists():
        sistemas["deepl"] = json.loads(DEEPL.read_text(encoding="utf-8"))
    sistemas["referencia"] = {t["texto_dialectal"]: t["traduccion"] for t in test}
    if a.validar:
        sistemas["control_malo"] = {t["texto_dialectal"]: "The weather is nice today." for t in test}  # control negativo evidente
    CACHE.mkdir(exist_ok=True)
    resumen = {}
    for nombre, pred in sistemas.items():
        ruta = CACHE / f"{nombre}.json"
        cache = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}
        for t in items:
            k = t["texto_dialectal"]
            if k in pred and k not in cache:
                cache[k] = juzgar(clave, k, pred[k])
        ruta.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
        v = [cache[t["texto_dialectal"]][0] for t in items if t["texto_dialectal"] in cache]
        resumen[nombre] = (len(v), sum(v) / len(v)) if v else (0, float("nan"))
        print(f"{nombre}: n={resumen[nombre][0]} puntaje medio (1-5) = {resumen[nombre][1]:.2f}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
