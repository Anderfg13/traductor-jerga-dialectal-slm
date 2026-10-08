"""
generation/comparar_generadores.py

Compara los datasets de los tres generadores sintéticos (cifras de
generación y filtrado) para dejar a la vista cualquier diferencia
relevante para PI1 antes de entrenar. Solo lee archivos ya generados;
no llama a ninguna API.

    python generation/comparar_generadores.py

Salida: tabla en consola y generation/comparacion_generadores.md
"""

import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

GEN = Path(__file__).resolve().parent
NOMBRES = {1: "Groq (gpt-oss-20b)", 2: "Cohere (command-r)", 3: "Google (gemini-3.5-flash-lite)"}


def palabras(t):
    return len(t.split())


def main() -> int:
    filas = []
    for g in (1, 2, 3):
        crudo = json.loads((GEN / f"dataset_generador{g}.json").read_text(encoding="utf-8"))
        limpio = json.loads((GEN / f"dataset_generador{g}_limpio.json").read_text(encoding="utf-8"))
        por_semilla = Counter(v["seed_id"] for v in crudo)
        reg = Counter(v["registro"] for v in crudo)
        # el texto dialectal de una variante repetido en OTRA semilla del mismo generador
        textos = Counter(v["texto_dialectal"].strip().lower() for v in limpio)
        repetidos = sum(c - 1 for c in textos.values() if c > 1)
        # marcador rioplatense "che" en variantes que no son rioplatenses (mezcla de dialecto, ver Sesión 10)
        che = sum(
            1 for v in limpio
            if v["dialecto_region"] != "Rioplatense" and re.search(r"\bche\b", v["texto_dialectal"], re.I)
        )
        filas.append(
            {
                "g": g,
                "crudo": len(crudo),
                "limpio": len(limpio),
                "descartadas": len(crudo) - len(limpio),
                "pct": 100 * (len(crudo) - len(limpio)) / len(crudo),
                "por_semilla": statistics.mean(por_semilla.values()),
                "min_max": (min(por_semilla.values()), max(por_semilla.values())),
                "pal_es": statistics.mean(palabras(v["texto_dialectal"]) for v in limpio),
                "pal_en": statistics.mean(palabras(v["traduccion"]) for v in limpio),
                "reg": reg,
                "repetidos": repetidos,
                "che": che,
            }
        )

    registros = sorted({k for f in filas for k in f["reg"]})
    L = ["# Comparación de los tres generadores sintéticos", "",
         "Mismas 100 semillas (`seeds/lote_01` + `lote_02`), misma plantilla de prompt, mismo filtro (`generation/validar.py`). "
         "Generado por `generation/comparar_generadores.py`.", "",
         "| | " + " | ".join(f"G{f['g']}: {NOMBRES[f['g']]}" for f in filas) + " |", "|---|" + "---|" * len(filas)]

    def fila(nombre, fn):
        L.append(f"| {nombre} | " + " | ".join(fn(f) for f in filas) + " |")

    fila("Variantes generadas (crudo)", lambda f: str(f["crudo"]))
    fila("Variantes tras el filtro", lambda f: str(f["limpio"]))
    fila("Descartadas por el filtro", lambda f: f"{f['descartadas']} ({f['pct']:.1f} %)")
    fila("Variantes por semilla (prom., mín-máx)", lambda f: f"{f['por_semilla']:.1f} ({f['min_max'][0]}-{f['min_max'][1]})")
    fila("Palabras por texto dialectal (prom.)", lambda f: f"{f['pal_es']:.1f}")
    fila("Palabras por traducción (prom.)", lambda f: f"{f['pal_en']:.1f}")
    for r in registros:
        fila(f"Registro `{r}`", lambda f, r=r: f"{100 * f['reg'][r] / f['crudo']:.0f} %")
    fila("Textos repetidos entre semillas", lambda f: str(f["repetidos"]))
    fila("'che' en variantes no rioplatenses", lambda f: str(f["che"]))
    L.append("")
    texto = "\n".join(L)
    (GEN / "comparacion_generadores.md").write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
