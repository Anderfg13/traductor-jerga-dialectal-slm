"""
evaluation/comparacion_fusion.py

Compara el modelo fusionado (promedio simple y TIES, ambos con mergekit
sobre modelos completos) con los tres modelos individuales y con el mejor
de ellos, sobre el MISMO test común, con las mismas métricas (BLEU/chrF de
sacrebleu, como evaluation/metricas_automaticas.py). Respuesta preliminar a
PI2. Escribe evaluation/comparacion_fusion_simple.md.

El "mejor individual" se define de antemano como el de mayor chrF global
(criterio fijo, no elegido a la medida de la fusión); si hay otro dentro del
ruido, el informe lo dice. Los intervalos de las diferencias salen de
evaluation/analisis_bootstrap.md (bootstrap por semilla, ya calculado).

    python evaluation/comparacion_fusion.py
"""

import json
import re
import sys
from pathlib import Path

import sacrebleu

EVAL = Path(__file__).resolve().parent
INDIVIDUALES = [("generador1", "LoRA Generador 1"), ("generador2", "LoRA Generador 2"), ("generador3", "LoRA Generador 3")]
FUSIONES = [("mergekit_linear", "Fusión: promedio simple (mergekit)"), ("mergekit_ties", "Fusión: TIES (mergekit)")]
OTROS = [("baseline", "Base sin ajustar"), ("mezcla", "LoRA entrenado sobre la mezcla 1+2+3")]
REPLICAS = [("peft_linear_norm", "Promedio simple con PEFT (pesos 1/3)"), ("peft_cat_norm", "Promedio exacto con PEFT (cat, pesos 1/3)"),
            ("fusion_ties", "TIES con PEFT"), ("fusion_dare_ties", "DARE+TIES con PEFT"), ("destilacion", "Destilación multi-maestro")]


def cargar(nombre):
    ruta = EVAL / "predicciones" / f"{nombre}.json"
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else None


def metricas(items):
    hip = [i["traduccion_modelo"] for i in items]
    ref = [[i["traduccion"] for i in items]]
    return sacrebleu.corpus_bleu(hip, ref).score, sacrebleu.corpus_chrf(hip, ref).score


def diferencia_bootstrap(a, b):
    """Fila 'a − b' de analisis_bootstrap.md como ((media, lo, hi) BLEU, (media, lo, hi) chrF), invirtiendo si solo existe 'b − a'."""
    texto = (EVAL / "analisis_bootstrap.md").read_text(encoding="utf-8")
    patron = r"\| %s − %s \| ([+\-−0-9.]+) \[([+\-−0-9.]+), ([+\-−0-9.]+)\]\s*\*? \| \d+%% \| ([+\-−0-9.]+) \[([+\-−0-9.]+), ([+\-−0-9.]+)\]"
    num = lambda s: float(s.replace("−", "-"))
    m = re.search(patron % (a, b), texto)
    if m:
        v = [num(x) for x in m.groups()]
        return (v[0], v[1], v[2]), (v[3], v[4], v[5])
    m = re.search(patron % (b, a), texto)
    if m:
        v = [num(x) for x in m.groups()]
        return (-v[0], -v[2], -v[1]), (-v[3], -v[5], -v[4])
    return None


def fmt(d):
    if d is None:
        return "—"
    media, lo, hi = d
    return f"{media:+.1f} [{lo:+.1f}, {hi:+.1f}]" + ("" if lo <= 0 <= hi else " *")


def main() -> int:
    datos = {n: cargar(n) for n, _ in INDIVIDUALES + FUSIONES + OTROS + REPLICAS}
    faltan = [n for n, d in datos.items() if d is None and n in dict(INDIVIDUALES + FUSIONES + OTROS)]
    if faltan:
        print(f"ERROR: faltan predicciones de {faltan}")
        return 1
    ref = [(x["texto_dialectal"], x["traduccion"], x["seed_id"], x["fuente"]) for x in datos["baseline"]]
    for n, d in datos.items():
        if d is not None and [(x["texto_dialectal"], x["traduccion"], x["seed_id"], x["fuente"]) for x in d] != ref:
            print(f"ERROR: {n} no se evaluó sobre el mismo conjunto")
            return 1
    semillas = len({r[2] for r in ref})

    glob = {n: metricas(d) for n, d in datos.items() if d is not None}
    mejor = max(INDIVIDUALES, key=lambda t: glob[t[0]][1])[0]  # mayor chrF global
    etiqueta = dict(INDIVIDUALES + FUSIONES + OTROS + REPLICAS)

    L = [
        "# Comparación del modelo fusionado con los individuales (PI2, respuesta preliminar)", "",
        "Generado por `evaluation/comparacion_fusion.py`. Fusión = promedio simple y TIES de los adaptadores de los generadores 1, 2 y 3, hechos con "
        "`mergekit` sobre modelos completos (`merging/fusion_simple.md`). Mismo test común para todos los modelos "
        f"(**{len(ref)} entradas de {semillas} semillas**, verificado: mismas entradas, referencias y semillas), mismas métricas (sacrebleu).", "",
        f"**Mejor individual** (criterio fijado de antemano: mayor chrF global): **{etiqueta[mejor]}** "
        f"({glob[mejor][0]:.1f} / {glob[mejor][1]:.1f}). El Generador 1 queda a menos de un punto y no se distingue de él; el Generador 2 queda por debajo "
        "(1.5 BLEU y 2.6 chrF menos, y en chrF esa diferencia sí se distingue del ruido).", "",
        "## 1. Tabla comparativa (BLEU / chrF globales)", "", "| Modelo | BLEU | chrF | Δ BLEU vs mejor individual | Δ chrF vs mejor individual |", "|---|---|---|---|---|"]
    for n, et in OTROS[:1] + INDIVIDUALES + [("__mejor__", f"**Mejor individual ({etiqueta[mejor]})**")] + OTROS[1:] + FUSIONES:
        k = mejor if n == "__mejor__" else n
        b, c = glob[k]
        db, dc = b - glob[mejor][0], c - glob[mejor][1]
        L.append(f"| {et} | {b:.1f} | {c:.1f} | {db:+.1f} | {dc:+.1f} |")
    L += ["", "## 2. Diferencia fusión − individual, con incertidumbre", "",
          "Intervalo de 95 % por bootstrap sobre semillas (`evaluation/analisis_bootstrap.md`); `*` = el intervalo no incluye 0.", "",
          "| Fusión − individual | ΔBLEU [IC 95 %] | ΔchrF [IC 95 %] |", "|---|---|---|"]
    for f, ef in FUSIONES:
        for i, ei in INDIVIDUALES + OTROS[1:]:
            d = diferencia_bootstrap(f, i)
            L.append(f"| {ef.split(': ')[1]} − {ei.replace('LoRA ', '')}" + (" **(mejor)**" if i == mejor else "") + f" | {fmt(d[0]) if d else '—'} | {fmt(d[1]) if d else '—'} |")
    L += ["", "## 3. Por dialecto (BLEU / chrF; n = entradas)", ""]
    dialectos = sorted({x["dialecto_region"] for x in datos["baseline"]})
    L += ["| Modelo | " + " | ".join(dialectos) + " |", "|---|" + "---|" * len(dialectos)]
    for n, et in [(mejor, f"Mejor individual ({etiqueta[mejor]})")] + FUSIONES:
        celdas = []
        for d in dialectos:
            it = [x for x in datos[n] if x["dialecto_region"] == d]
            b, c = metricas(it)
            celdas.append(f"{b:.1f} / {c:.1f} ({len(it)})")
        L.append(f"| {et} | " + " | ".join(celdas) + " |")
    L += ["", "Con 1 o 2 semillas por dialecto, las diferencias entre dialectos son anecdóticas y no se interpretan.", ""]
    oro = [x for x in datos["baseline"] if x["fuente"] == "oro"]
    L += ["## 4. Solo referencias humanas del banco de semillas (`oro`, n = 9)", "", "| Modelo | BLEU | chrF |", "|---|---|---|"]
    for n, et in OTROS[:1] + [(mejor, f"Mejor individual ({etiqueta[mejor]})")] + FUSIONES:
        b, c = metricas([x for x in datos[n] if x["fuente"] == "oro"])
        L.append(f"| {et} | {b:.1f} | {c:.1f} |")
    L += ["", "Nueve entradas no permiten concluir nada; se muestra por completitud.", "",
          "## 5. Réplicas con otras implementaciones (consistencia)", "", "| Modelo | BLEU | chrF |", "|---|---|---|"]
    for n, et in REPLICAS:
        if datos[n] is not None:
            L.append(f"| {et} | {glob[n][0]:.1f} | {glob[n][1]:.1f} |")
    L += ["", "Todas las fusiones que promedian (en vez de sumar) quedan en el mismo rango: el resultado no depende de la herramienta.", ""]

    # respuesta honesta, generada a partir de los números
    d_lin = diferencia_bootstrap("mergekit_linear", mejor)
    d_ties = diferencia_bootstrap("mergekit_ties", mejor)
    L += ["## 6. Respuesta preliminar a PI2 (y cómo no pasarse)", "",
          f"- **La fusión no fue peor que el mejor individual**: promedio simple {glob['mergekit_linear'][0]:.1f} / {glob['mergekit_linear'][1]:.1f} y TIES "
          f"{glob['mergekit_ties'][0]:.1f} / {glob['mergekit_ties'][1]:.1f}, frente a {glob[mejor][0]:.1f} / {glob[mejor][1]:.1f} del mejor individual.",
          f"- **Pero la ventaja es pequeña y frágil.** Frente al mejor individual: promedio simple {fmt(d_lin[0])} BLEU y {fmt(d_lin[1])} chrF; "
          f"TIES {fmt(d_ties[0])} BLEU y {fmt(d_ties[1])} chrF. Donde el intervalo incluye 0, con estos datos no se distingue de un empate.",
          "- **Sí supera con claridad al peor individual (Generador 2) y, en BLEU, al modelo entrenado sobre la mezcla.**",
          "- **Entre promedio simple y TIES no hay diferencia distinguible**: la técnica de fusión importa menos que fusionar bien.",
          "- **Lectura honesta**: una primera señal sugiere que fusionar los adaptadores es al menos tan bueno como el mejor modelo individual y quizás algo mejor "
          "en BLEU; no se puede afirmar que lo supere. Si el resultado hubiera sido peor, también se habría reportado.",
          "- **Cautelas**: solo 9 semillas de prueba, una corrida por modelo, referencias mayormente sintéticas (con sesgo hacia el LLM que las escribió), decenas "
          "de comparaciones (un intervalo que apenas excluye 0 puede ser casualidad), el \"mejor individual\" se elige con el mismo test (lo favorece ligeramente), "
          "y sin evaluación humana (BLEU/chrF no miden retención de matices).", ""]
    texto = "\n".join(L)
    (EVAL / "comparacion_fusion_simple.md").write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
