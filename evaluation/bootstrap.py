"""
evaluation/bootstrap.py

Intervalos de confianza (bootstrap) para las diferencias de BLEU/chrF
entre modelos sobre el test común. Con pocas semillas de prueba, una
diferencia de puntos puede ser ruido; esto cuantifica cuánto.

Remuestreo POR SEMILLA (cluster bootstrap): las variantes de una misma
semilla (y sus versiones de distintos generadores) no son independientes,
así que se remuestrean semillas completas con reemplazo, no oraciones
sueltas. Con pocas semillas los intervalos salen anchos: es la
incertidumbre real, no un defecto del método.

    python evaluation/bootstrap.py                    # todos los modelos con predicciones vs baseline
    python evaluation/bootstrap.py --n 5000 --salida evaluation/analisis_bootstrap.md

Salida: tabla de diferencias (modelo A - modelo B) con IC 95 % y la
fracción de remuestreos en que A supera a B.
"""

import argparse
import json
import random
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import sacrebleu

EVAL = Path(__file__).resolve().parent


def metricas(items, campo):
    hip = [i[campo] for i in items]
    ref = [[i["traduccion"] for i in items]]
    return sacrebleu.corpus_bleu(hip, ref).score, sacrebleu.corpus_chrf(hip, ref).score


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--n", type=int, default=2000, help="remuestreos (default 2000)")
    p.add_argument("--semilla", type=int, default=42)
    p.add_argument("--modelos", nargs="+", default=None, help="limitar a estos modelos (siempre se incluye baseline); por defecto, todos")
    p.add_argument("--salida", type=Path, default=EVAL / "analisis_bootstrap.md")
    a = p.parse_args()

    modelos = {}
    for ruta in sorted((EVAL / "predicciones").glob("*.json")):
        modelos[ruta.stem] = {x["texto_dialectal"]: x for x in json.loads(ruta.read_text(encoding="utf-8"))}
    if "baseline" not in modelos or len(modelos) < 2:
        print("ERROR: hacen falta evaluation/predicciones/baseline.json y al menos otro modelo")
        return 1
    if a.modelos:
        modelos = {m: v for m, v in modelos.items() if m == "baseline" or m in a.modelos}
    comunes = sorted(set.intersection(*[set(v) for v in modelos.values()]))
    por_semilla = defaultdict(list)
    for t in comunes:
        por_semilla[modelos["baseline"][t]["seed_id"]].append(t)
    semillas = sorted(por_semilla)
    for m in modelos:
        modelos[m] = {t: {"traduccion": modelos[m][t]["traduccion"], "pred": modelos[m][t]["traduccion_modelo"]} for t in comunes}

    rng = random.Random(a.semilla)
    muestras = {m: [] for m in modelos}
    for _ in range(a.n):
        elegidas = [rng.choice(semillas) for _ in semillas]
        textos = [t for s in elegidas for t in por_semilla[s]]
        for m in modelos:
            muestras[m].append(metricas([modelos[m][t] for t in textos], "pred"))

    def ic(valores):
        v = sorted(valores)
        return v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1]

    nombres = list(modelos)
    L = [
        "# Análisis de incertidumbre (bootstrap por semilla)", "",
        f"Test común: {len(comunes)} entradas de {len(semillas)} semillas; {a.n} remuestreos de semillas con reemplazo "
        "(`evaluation/bootstrap.py`). Cada fila es la diferencia A − B; el intervalo es el 95 % del remuestreo y "
        "\"P(A>B)\" la fracción de remuestreos en que A supera a B. **Un intervalo que incluye 0 significa que con estos datos "
        "no se puede distinguir A de B.**", "",
        "## Puntaje por modelo (IC 95 %)", "", "| Modelo | BLEU | chrF |", "|---|---|---|",
    ]
    for m in nombres:
        b, c = [x[0] for x in muestras[m]], [x[1] for x in muestras[m]]
        pb, pc = metricas([modelos[m][t] for t in comunes], "pred")
        L.append(f"| {m} | {pb:.1f} [{ic(b)[0]:.1f}, {ic(b)[1]:.1f}] | {pc:.1f} [{ic(c)[0]:.1f}, {ic(c)[1]:.1f}] |")

    L += ["", "## Diferencias entre modelos", "", "| A − B | ΔBLEU (IC 95 %) | P(A>B) BLEU | ΔchrF (IC 95 %) | P(A>B) chrF |", "|---|---|---|---|---|"]
    pares = [(m, "baseline") for m in nombres if m != "baseline"] + [
        (x, y) for x, y in combinations([m for m in nombres if m != "baseline"], 2)
    ]
    for A, B in pares:
        fila = [f"{A} − {B}"]
        for k in (0, 1):
            d = [muestras[A][i][k] - muestras[B][i][k] for i in range(a.n)]
            lo, hi = ic(d)
            media = sum(d) / len(d)
            marca = "" if lo <= 0 <= hi else " *"
            fila += [f"{media:+.1f} [{lo:+.1f}, {hi:+.1f}]{marca}", f"{sum(1 for x in d if x > 0) / len(d):.0%}"]
        L.append("| " + " | ".join(fila) + " |")
    L += ["", "`*` = el intervalo de 95 % NO incluye 0 (diferencia distinguible con estos datos).", ""]
    texto = "\n".join(L)
    a.salida.write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
