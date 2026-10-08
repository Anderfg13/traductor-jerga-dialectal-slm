"""
evaluation/bootstrap_pi3.py

Intervalos de confianza (bootstrap por semilla, igual que bootstrap.py)
para las diferencias entre el mejor modelo pequeño (fusión lineal con
mergekit) y cada sistema de propósito general, sobre las mismas entradas
(cada generador excluye sus propias referencias). Salida:
evaluation/analisis_bootstrap_pi3.md.

    python evaluation/bootstrap_pi3.py
"""

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import sacrebleu

EVAL = Path(__file__).resolve().parent
sys.path.insert(0, str(EVAL))
from comparar_sistemas_generales import SISTEMAS  # noqa: E402

N = 1000
MODELOS_PEQUENOS = ["mergekit_linear", "generador3"]


def m(items, pred, ref):
    hip = [pred[i] for i in items]
    r = [[ref[i] for i in items]]
    return sacrebleu.corpus_bleu(hip, r).score, sacrebleu.corpus_chrf(hip, r).score


def main() -> int:
    test = json.loads((EVAL / "test_comun.json").read_text(encoding="utf-8"))
    ref = {t["texto_dialectal"]: t["traduccion"] for t in test}
    fuente = {t["texto_dialectal"]: t["fuente"] for t in test}
    semilla = {t["texto_dialectal"]: t["seed_id"] for t in test}
    pequenos = {n: {x["texto_dialectal"]: x["traduccion_modelo"] for x in json.loads((EVAL / "predicciones" / f"{n}.json").read_text(encoding="utf-8"))}
                for n in MODELOS_PEQUENOS}
    L = ["# Incertidumbre de la comparación PI3 (bootstrap por semilla)", "",
         f"{N} remuestreos de semillas con reemplazo. Diferencia = modelo pequeño − sistema general; intervalo de 95 %. `*` = el intervalo no incluye 0. "
         "Cada sistema se compara sobre las mismas entradas, excluyendo las referencias que él mismo escribió (los generadores).", "",
         "| Modelo pequeño | Sistema general | n | ΔBLEU (IC 95 %) | ΔchrF (IC 95 %) |", "|---|---|---|---|---|"]
    rng = random.Random(42)
    for sis, (_, _, propio, _) in SISTEMAS.items():
        cache = EVAL / "predicciones_generales" / f"{sis}.json"
        if not cache.exists():
            continue
        grande = json.loads(cache.read_text(encoding="utf-8"))
        textos = [t for t in ref if t in grande and all(t in p for p in pequenos.values()) and (propio is None or fuente[t] != propio)]
        por_sem = defaultdict(list)
        for t in textos:
            por_sem[semilla[t]].append(t)
        sems = sorted(por_sem)
        diffs = {n: ([], []) for n in pequenos}
        for _ in range(N):
            items = [t for s in [rng.choice(sems) for _ in sems] for t in por_sem[s]]
            bg, cg = m(items, grande, ref)
            for n, p in pequenos.items():
                b, c = m(items, p, ref)
                diffs[n][0].append(b - bg)
                diffs[n][1].append(c - cg)
        for n in pequenos:
            fila = [n, sis, str(len(textos))]
            for d in diffs[n]:
                v = sorted(d)
                lo, hi = v[int(0.025 * N)], v[int(0.975 * N) - 1]
                fila.append(f"{sum(d) / N:+.1f} [{lo:+.1f}, {hi:+.1f}]" + ("" if lo <= 0 <= hi else " *"))
            L.append("| " + " | ".join(fila) + " |")
    L.append("")
    (EVAL / "analisis_bootstrap_pi3.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
