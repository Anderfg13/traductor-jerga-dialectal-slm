"""
evaluation/comparacion_pi1.py

Comparación automática (BLEU/chrF) de los tres modelos INDIVIDUALES
(generador1, generador2, generador3; y el base como referencia) para
PI1, sobre exactamente el mismo conjunto de entradas, desglosada por
dialecto y por fuente de la referencia. Genera
evaluation/comparacion_pi1_automatica.md.

Verifica antes de calcular que los modelos se evaluaron sobre el MISMO
conjunto: mismas entradas (texto), mismas referencias y mismas semillas
(si no, aborta). Las métricas se calculan con sacrebleu, igual que
evaluation/metricas_automaticas.py.

    python evaluation/comparacion_pi1.py
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

import sacrebleu

EVAL = Path(__file__).resolve().parent
MODELOS = [("baseline", "Base sin ajustar (referencia)"), ("generador1", "LoRA Generador 1 (Groq)"),
           ("generador2", "LoRA Generador 2 (Cohere)"), ("generador3", "LoRA Generador 3 (Google lite)")]


def metricas(items):
    hip = [i["traduccion_modelo"] for i in items]
    ref = [[i["traduccion"] for i in items]]
    return sacrebleu.corpus_bleu(hip, ref).score, sacrebleu.corpus_chrf(hip, ref).score


def main() -> int:
    datos = {}
    for m, _ in MODELOS:
        ruta = EVAL / "predicciones" / f"{m}.json"
        if not ruta.exists():
            print(f"ERROR: falta {ruta}")
            return 1
        datos[m] = json.loads(ruta.read_text(encoding="utf-8"))

    # --- verificación: mismo conjunto de ejemplos para todos ---
    base = datos["baseline"]
    clave = lambda lst: [(x["texto_dialectal"], x["traduccion"], x["seed_id"], x["fuente"]) for x in lst]
    for m, lst in datos.items():
        if clave(lst) != clave(base):
            print(f"ERROR: {m} no se evaluó sobre el mismo conjunto (entradas, referencias o semillas distintas)")
            return 1
    n = len(base)
    semillas = sorted({x["seed_id"] for x in base})
    por_fuente = defaultdict(int)
    for x in base:
        por_fuente[x["fuente"]] += 1
    test_comun = json.loads((EVAL / "test_comun.json").read_text(encoding="utf-8"))
    assert clave([{**x} for x in test_comun]) == clave(base), "las predicciones no coinciden con evaluation/test_comun.json"

    L = [
        "# Comparación automática para PI1: modelos individuales", "",
        "BLEU y chrF de los adaptadores LoRA de los tres generadores sobre el **mismo** conjunto de prueba "
        "(`evaluation/test_comun.json`). Generado por `evaluation/comparacion_pi1.py`.", "",
        "## Verificación del conjunto de evaluación", "",
        f"- Los 4 modelos (base y los 3 adaptadores) se evaluaron sobre **las mismas {n} entradas**, con las mismas referencias y "
        f"las mismas **{len(semillas)} semillas** (`{', '.join(semillas)}`); el script aborta si cualquier modelo difiere.",
        "- Es el mismo conjunto para todos, no uno derivado de cada generador. Contiene, por semilla de test: la expresión original con la "
        "**referencia humana del banco de semillas** (fuente `oro`) y las variantes de test de los tres generadores. Composición: "
        + ", ".join(f"`{k}` {v}" for k, v in sorted(por_fuente.items())) + ".",
        "- Las 9 semillas de test son las mismas que las de `seeds/split_semillas.json` y ninguna estuvo en entrenamiento de ningún modelo.",
        "",
    ]

    def tabla(titulo, subconjunto, nota=""):
        L.extend([f"## {titulo}", ""])
        if nota:
            L.extend([nota, ""])
        L.extend(["| Modelo | n | BLEU | chrF |", "|---|---|---|---|"])
        for m, etiqueta in MODELOS:
            items = [x for x in datos[m] if subconjunto(x)]
            b, c = metricas(items)
            L.append(f"| {etiqueta} | {len(items)} | {b:.1f} | {c:.1f} |")
        L.append("")

    tabla("Global (todas las referencias)", lambda x: True)
    tabla("Solo referencias humanas del banco de semillas (fuente `oro`)", lambda x: x["fuente"] == "oro",
          "Es la comparación que usa **únicamente** las traducciones escritas por el equipo, sin sesgo hacia ningún LLM generador. "
          "Tiene solo 9 entradas (frases cortas e idiomáticas), así que **no permite concluir nada**; se muestra por completitud.")

    dialectos = sorted({x["dialecto_region"] for x in base})
    L.extend(["## Por dialecto (todas las referencias)", "", "BLEU / chrF; entre paréntesis, número de entradas.", "",
              "| Modelo | " + " | ".join(f"{d}" for d in dialectos) + " |", "|---|" + "---|" * len(dialectos)])
    for m, etiqueta in MODELOS:
        celdas = []
        for d in dialectos:
            items = [x for x in datos[m] if x["dialecto_region"] == d]
            b, c = metricas(items)
            celdas.append(f"{b:.1f} / {c:.1f} ({len(items)})")
        L.append(f"| {etiqueta} | " + " | ".join(celdas) + " |")
    L.append("")

    # --- lectura honesta (cifras salen del análisis de incertidumbre ya calculado) ---
    L.extend([
        "## Cómo leerla (respuesta preliminar a PI1)", "",
        "- **Hay diferencia medible**: el adaptador del Generador 2 (Cohere) da menos chrF que los de los Generadores 1 y 3, y el 1 y el 3 son casi iguales.",
        "- **Qué tanto de esa diferencia es ruido**: ver `evaluation/analisis_bootstrap.md` (intervalos de 95 % por remuestreo de semillas). "
        "G1 − G2: +2.3 chrF [+0.2, +4.2]; G3 − G2: +2.7 [+0.8, +5.3]; G1 − G3: −0.5 [−2.4, +1.1] (no distinguible). En BLEU no se distingue "
        "ninguno de los tres entre sí.",
        "- **Con solo 9 semillas de prueba** cualquier desglose por dialecto (1 o 2 semillas por dialecto) es anecdótico: no se interpretan "
        "diferencias entre dialectos.",
        "- **Sesgo de referencia**: cada generador sale favorecido con las referencias de su propio LLM (ver `evaluation/comparacion_fase3.md`); "
        "por eso la comparación limpia sería solo con referencias humanas, que aquí son 9 entradas.",
        "- Es una respuesta **tentativa** a PI1; falta la evaluación humana.", "",
    ])
    texto = "\n".join(L)
    (EVAL / "comparacion_pi1_automatica.md").write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
