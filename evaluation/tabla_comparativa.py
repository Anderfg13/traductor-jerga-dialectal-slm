"""
evaluation/tabla_comparativa.py

Junta los reportes JSON de evaluation/reportes/<modelo>.json (salida de
metricas_automaticas.py --salida-json) en UNA tabla comparativa de todos
los modelos evaluados, lista para pegar en el paper:

    python evaluation/tabla_comparativa.py

Salida: evaluation/comparacion_fase3.md

Cómo leerla: "Global" mezcla todas las fuentes del test común; "Oro" son
solo las traducciones de referencia escritas por el equipo (sin sesgo
hacia ningún generador); las columnas "Ref. gN" usan como referencia la
traducción del LLM generador N — un modelo entrenado con ese generador
puede salir favorecido ahí, por eso el oro es la columna más confiable
para PI1/PI2.
"""

import json
import sys
from pathlib import Path

REPORTES = Path(__file__).resolve().parent / "reportes"
SALIDA = Path(__file__).resolve().parent / "comparacion_fase3.md"

ORDEN = [
    ("baseline", "Base sin ajustar (zero-shot)"),
    ("generador1", "LoRA Generador 1 (Groq)"),
    ("generador2", "LoRA Generador 2 (Cohere)"),
    ("generador3", "LoRA Generador 3 (Google)"),
    ("mezcla", "LoRA sobre la mezcla 1+2+3"),
    ("fusion_ties", "Fusión TIES"),
    ("fusion_dare_ties", "Fusión DARE+TIES"),
    ("fusion_linear", "Fusión lineal (promedio)"),
    ("destilacion", "Fusión guiada por destilación multi-maestro"),
]


def celda(metricas, clave):
    m = (metricas or {}).get(clave)
    return "—" if m is None else f"{m['bleu']:.1f} / {m['chrf']:.1f} (n={m['n']})"


def main() -> int:
    filas = []
    for nombre, etiqueta in ORDEN:
        ruta = REPORTES / f"{nombre}.json"
        if not ruta.exists():
            continue
        d = json.loads(ruta.read_text(encoding="utf-8"))
        pf = d.get("por_fuente", {})
        filas.append(
            f"| {etiqueta} | {d['global']['bleu']:.1f} / {d['global']['chrf']:.1f} "
            f"| {celda(pf, 'oro')} | {celda(pf, 'generador1')} | {celda(pf, 'generador2')} | {celda(pf, 'generador3')} |"
        )
    if not filas:
        print(f"ERROR: no hay reportes JSON en {REPORTES}")
        return 1

    texto = "\n".join(
        [
            "# Comparación de modelos (Fase 3)",
            "",
            "Cada celda es **BLEU / chrF** sobre el test común (`evaluation/test_comun.json`).",
            "",
            "| Modelo | Global | Oro (ref. humana) | Ref. g1 | Ref. g2 | Ref. g3 |",
            "|---|---|---|---|---|---|",
            *filas,
            "",
            "Ver la docstring de `evaluation/tabla_comparativa.py` para cómo interpretar las columnas.",
            "",
        ]
    )
    SALIDA.write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
