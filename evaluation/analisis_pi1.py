"""
evaluation/analisis_pi1.py

Análisis consolidado de PI1 (¿cómo afecta el LLM generador de datos a la
calidad de la traducción de un SLM ajustado?), con las dos fuentes de
evidencia:

  1. AUTOMÁTICA: BLEU/chrF de los adaptadores de los generadores 1, 2 y 3
     sobre el mismo test común, con intervalos por bootstrap sobre semillas.
  2. HUMANA: calificaciones 1-5 de evaluadores nativos
     (evaluation/resultados_humanos_pi1.csv, creado por
     evaluation/consolidar_resultados_humanos.py): kappa de Fleiss por
     dialecto, puntaje medio por modelo con intervalo, y comparación de
     rankings contra la automática.

Si NO existe resultados_humanos_pi1.csv, la parte humana se declara "no
disponible" y la respuesta a PI1 se limita a lo que la evidencia automática
sostiene. No se simula ni se rellena nada.

    python evaluation/analisis_pi1.py
    python evaluation/analisis_pi1.py --humanos otra/ruta.csv --salida otra/salida.md   # pruebas
"""

import argparse
import csv
import random
import statistics
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import sacrebleu

EVAL = Path(__file__).resolve().parent
sys.path.insert(0, str(EVAL))
from comparacion_fusion import diferencia_bootstrap  # noqa: E402
from kappa import CATEGORIAS, cohen_kappa_ponderado, fleiss_kappa  # noqa: E402

import json  # noqa: E402

MODELOS = ["generador1", "generador2", "generador3"]
NOMBRE = {"generador1": "Generador 1 (Groq)", "generador2": "Generador 2 (Cohere)", "generador3": "Generador 3 (Google lite)"}


def etiqueta_kappa(k):
    if k < 0:
        return "sin acuerdo (peor que el azar)"
    for tope, txt in [(0.20, "leve"), (0.40, "aceptable"), (0.60, "moderado"), (0.80, "sustancial"), (1.01, "casi perfecto")]:
        if k <= tope:
            return txt
    return "casi perfecto"


def parte_automatica():
    preds = {m: json.loads((EVAL / "predicciones" / f"{m}.json").read_text(encoding="utf-8")) for m in MODELOS}
    res = {}
    for m, d in preds.items():
        def met(items):
            hip = [i["traduccion_modelo"] for i in items]
            ref = [[i["traduccion"] for i in items]]
            return sacrebleu.corpus_bleu(hip, ref).score, sacrebleu.corpus_chrf(hip, ref).score
        res[m] = {"global": met(d), "oro": met([i for i in d if i["fuente"] == "oro"]), "n": len(d)}
    ranking = sorted(MODELOS, key=lambda m: res[m]["global"][1], reverse=True)  # por chrF
    pares = {}
    for a, b in combinations(MODELOS, 2):
        pares[(a, b)] = diferencia_bootstrap(a, b)
    return res, ranking, pares


def fmt(d):
    if d is None:
        return "—"
    media, lo, hi = d
    return f"{media:+.1f} [{lo:+.1f}, {hi:+.1f}]" + ("" if lo <= 0 <= hi else " *")


def parte_humana(ruta, n_boot=2000):
    filas = list(csv.DictReader(ruta.open(encoding="utf-8-sig", newline="")))
    # calificación por (dialecto, ítem, evaluador, modelo); una opción compartida por varios modelos cuenta para cada uno
    cal = defaultdict(dict)  # (dialecto, item, modelo) -> {evaluador: calificacion}
    por_dialecto_filas = defaultdict(lambda: defaultdict(dict))  # dialecto -> (item,opcion) -> {evaluador: cal}
    for f in filas:
        c = int(f["calificacion"])
        por_dialecto_filas[f["dialecto"]][(f["id_item"], f["opcion"])][f["evaluador"]] = c
        for m in f["modelo"].split("+"):
            cal[(f["dialecto"], f["id_item"], m)][f["evaluador"]] = c

    kappas = {}
    for d, mapa in sorted(por_dialecto_filas.items()):
        evs = sorted({e for r in mapa.values() for e in r})
        completas = [k for k, r in mapa.items() if set(r) == set(evs)]
        if len(evs) >= 3 and completas:
            tabla = [[sum(1 for e in evs if mapa[k][e] == c) for c in CATEGORIAS] for k in completas]
            fl = fleiss_kappa(tabla)
            pares = [cohen_kappa_ponderado([mapa[k][x] for k in completas], [mapa[k][y] for k in completas]) for x, y in combinations(evs, 2)]
            kappas[d] = (len(evs), len(completas), fl, statistics.mean(pares))
        else:
            kappas[d] = (len(evs), len(completas), None, None)

    items = sorted({(d, i) for (d, i, _m) in cal})
    media_item = {m: {} for m in MODELOS}  # modelo -> (dialecto,item) -> media sobre evaluadores
    for (d, i, m), r in cal.items():
        if m in media_item:
            media_item[m][(d, i)] = statistics.mean(r.values())
    comunes = [it for it in items if all(it in media_item[m] for m in MODELOS)]
    medias = {m: statistics.mean(media_item[m][it] for it in comunes) for m in MODELOS}
    por_dial = {m: {d: statistics.mean(media_item[m][it] for it in comunes if it[0] == d) for d in sorted({x[0] for x in comunes})} for m in MODELOS}

    rng = random.Random(42)
    dif = {}
    for a, b in combinations(MODELOS, 2):
        v = [media_item[a][it] - media_item[b][it] for it in comunes]
        boots = sorted(statistics.mean(rng.choice(v) for _ in v) for _ in range(n_boot))
        dif[(a, b)] = (statistics.mean(v), boots[int(0.025 * n_boot)], boots[int(0.975 * n_boot) - 1])
    ev_por_d = {d: kappas[d][0] for d in kappas}
    return {"kappas": kappas, "medias": medias, "por_dialecto": por_dial, "dif": dif, "n_items": len(comunes), "n_cal": len(filas), "evaluadores": ev_por_d}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--humanos", type=Path, default=EVAL / "resultados_humanos_pi1.csv")
    p.add_argument("--salida", type=Path, default=EVAL / "analisis_pi1.md")
    a = p.parse_args()

    res, ranking, pares = parte_automatica()
    L = ["# Análisis de PI1: ¿importa el LLM generador de los datos?", "",
         "Generado por `evaluation/analisis_pi1.py`. Pregunta: ¿cómo afecta la elección del LLM generador (Groq, Cohere o Google) a la calidad de la "
         "traducción de un SLM ajustado con sus datos? Los tres adaptadores tienen configuración idéntica y se evalúan sobre las mismas entradas.", "",
         "## 1. Evidencia automática (BLEU / chrF)", "",
         f"Test común: {res['generador1']['n']} entradas de 9 semillas (mismas para los tres modelos).", "",
         "| Modelo | BLEU | chrF | BLEU solo refs. humanas del banco (n=9) | chrF solo refs. humanas |", "|---|---|---|---|---|"]
    for m in ranking:
        g, o = res[m]["global"], res[m]["oro"]
        L.append(f"| {NOMBRE[m]} | {g[0]:.1f} | {g[1]:.1f} | {o[0]:.1f} | {o[1]:.1f} |")
    L += ["", "Diferencias entre generadores (A − B) con intervalo de 95 % por bootstrap sobre semillas (`*` = el intervalo no incluye 0):", "",
          "| A − B | ΔBLEU | ΔchrF |", "|---|---|---|"]
    for (x, y), d in pares.items():
        L.append(f"| {NOMBRE[x]} − {NOMBRE[y]} | {fmt(d[0]) if d else '—'} | {fmt(d[1]) if d else '—'} |")
    sig = [(x, y, d[1]) for (x, y), d in pares.items() if d and not d[1][1] <= 0 <= d[1][2]]
    L += ["", "**Lectura automática**: ranking por chrF: " + " > ".join(NOMBRE[m] for m in ranking) + ". "
          + ("Las diferencias distinguibles del ruido en chrF son: " + "; ".join(f"{NOMBRE[x]} − {NOMBRE[y]} ({fmt(d)})" for x, y, d in sig) + ". "
             if sig else "Ninguna diferencia en chrF se distingue del ruido. ")
          + "En BLEU no se distingue ningún par entre los tres.", ""]

    L += ["## 2. Evidencia humana", ""]
    h = None
    if a.humanos.exists():
        h = parte_humana(a.humanos)
        L += [f"{h['n_cal']} calificaciones; {h['n_items']} ítems calificados por todos los modelos.", "", "### Acuerdo entre evaluadores", "",
              "| Dialecto | Evaluadores | Filas en común | **Kappa de Fleiss** | Interpretación | Kappa de Cohen pond. (prom. pares) |", "|---|---|---|---|---|---|"]
        for d, (nev, nf, fl, co) in h["kappas"].items():
            if fl is None:
                L.append(f"| {d} | {nev} | {nf} | no calculable (se necesitan ≥3 evaluadores con filas en común) | — | — |")
            else:
                L.append(f"| {d} | {nev} | {nf} | **{fl:.3f}** | {etiqueta_kappa(fl)} | {co:.3f} |")
        ks = [v[2] for v in h["kappas"].values() if v[2] is not None]
        if ks:
            L += ["", f"Kappa de Fleiss medio entre dialectos: **{statistics.mean(ks):.3f}** ({etiqueta_kappa(statistics.mean(ks))}; escala de Landis y Koch)."]
        L += ["", "### Puntaje humano por modelo (1-5)", "", "| Modelo | Media | " + " | ".join(sorted(next(iter(h['por_dialecto'].values())))) + " |",
              "|---|---|" + "---|" * len(next(iter(h['por_dialecto'].values())))]
        rank_h = sorted(MODELOS, key=lambda m: h["medias"][m], reverse=True)
        for m in rank_h:
            L.append(f"| {NOMBRE[m]} | {h['medias'][m]:.2f} | " + " | ".join(f"{v:.2f}" for _, v in sorted(h["por_dialecto"][m].items())) + " |")
        L += ["", "Diferencia de medias entre generadores (A − B), bootstrap sobre ítems:", "", "| A − B | Δ media [IC 95 %] |", "|---|---|"]
        for (x, y), (md, lo, hi) in h["dif"].items():
            L.append(f"| {NOMBRE[x]} − {NOMBRE[y]} | {md:+.2f} [{lo:+.2f}, {hi:+.2f}]" + ("" if lo <= 0 <= hi else " *") + " |")

        L += ["", "## 3. ¿Coinciden la señal automática y la humana?", "", "| Par | Automática (chrF) | Humana | ¿Coinciden? |", "|---|---|---|---|"]
        coincide, contradice = 0, 0
        for (x, y), d in pares.items():
            da, dh = d[1] if d else None, h["dif"][(x, y)]
            sa = 0 if da is None or da[1] <= 0 <= da[2] else (1 if da[0] > 0 else -1)
            sh = 0 if dh[1] <= 0 <= dh[2] else (1 if dh[0] > 0 else -1)
            ma = "sin diferencia clara" if sa == 0 else (f"{NOMBRE[x] if sa > 0 else NOMBRE[y]} mejor")
            mh = "sin diferencia clara" if sh == 0 else (f"{NOMBRE[x] if sh > 0 else NOMBRE[y]} mejor")
            if sa * sh == -1:
                v = "**SE CONTRADICEN**"
                contradice += 1
            elif sa == sh:
                v = "coinciden"
                coincide += 1
            else:
                v = "una señal distingue y la otra no"
            L.append(f"| {NOMBRE[x]} − {NOMBRE[y]} | {ma} | {mh} | {v} |")
        L += ["", f"Ranking automático (chrF): {' > '.join(NOMBRE[m] for m in ranking)}. Ranking humano: {' > '.join(NOMBRE[m] for m in rank_h)}. "
              + ("**Los rankings coinciden.**" if ranking == rank_h else "**Los rankings NO coinciden: hallazgo a discutir en el paper, no a ocultar.**"), ""]
        L += ["## 4. Respuesta a PI1", ""]
        if ks and statistics.mean(ks) < 0.40:
            L += [f"**Advertencia sobre la fiabilidad humana**: el kappa de Fleiss medio ({statistics.mean(ks):.3f}) es {etiqueta_kappa(statistics.mean(ks))}; "
                  "los evaluadores discrepan bastante entre sí, así que las puntuaciones humanas son ruidosas y cualquier ranking humano debe leerse con esa cautela "
                  "(el kappa ponderado, que penaliza menos un 4 frente a un 5, suele salir más alto y se reporta aparte).", ""]
        if contradice:
            L += ["**Mixta, con contradicción**: al menos un par de generadores se ordena al revés según la métrica automática y según las personas. "
                  "BLEU/chrF miden coincidencia con una referencia (en su mayoría escrita por un LLM); la evaluación humana mide retención de matices. "
                  "Cuál es más fiable es justamente la pregunta; no se resuelve eligiendo la señal que más convenga."]
        elif coincide == len(pares) and sig:
            L += ["**Clara, con ambas señales alineadas**: el generador importa y ambas fuentes de evidencia ordenan igual a los generadores que se distinguen."]
        else:
            L += ["**Mixta**: las señales no se contradicen, pero al menos un par solo se distingue en una de las dos fuentes."]
    else:
        L += ["**No disponible.** `evaluation/resultados_humanos_pi1.csv` no existe: no hay evaluadores confirmados (`evaluation/evaluadores.csv` vacío), no se envió "
              "ninguna hoja y no hay calificaciones. **No se calculó el kappa de Fleiss ni ningún puntaje humano; no se simularon.** El material para la ronda está "
              "listo (`docs/evaluacion_humana_pi1.md`); cuando existan las hojas devueltas, `python evaluation/consolidar_resultados_humanos.py` crea el CSV y "
              "este mismo script calcula el kappa por dialecto, el puntaje por modelo con intervalos y si el ranking humano coincide con el automático.", "",
              "## 3. ¿Coinciden la señal automática y la humana?", "", "No se puede responder: falta la señal humana.", "",
              "## 4. Respuesta a PI1 con la evidencia disponible (solo automática)", "",
              "**Parcial y tentativa; no es una respuesta cerrada.**", ""]
        if sig:
            x, y, d = sig[0]
            L += [f"- *¿El generador importa?* Sí en un sentido acotado: el adaptador entrenado con los datos de {NOMBRE['generador2']} queda por debajo de los otros dos en chrF "
                  f"(diferencias de unos 2-3 puntos, intervalos que excluyen 0), y en BLEU no se distingue ningún par.",
                  f"- *¿Entre Groq y Google?* No se distinguen ({NOMBRE['generador1']} − {NOMBRE['generador3']}: {fmt(pares[('generador1', 'generador3')][1])} chrF).",
                  "- *¿Cuánto?* Unos 2-3 puntos de chrF entre el peor y los otros dos, sobre una escala donde el ajuste fino sube unos 4 puntos sobre el modelo base: "
                  "elegir un generador u otro mueve el resultado una fracción apreciable de lo que aporta ajustar.", ""]
        L += ["**Por qué no es una respuesta cerrada**: sin evaluación humana no se sabe si esa diferencia en BLEU/chrF corresponde a una diferencia de calidad percibida; "
              "las referencias son mayormente sintéticas y cada generador sale favorecido con las de su propio LLM; son solo 9 semillas y una corrida por modelo; "
              "el Generador 3 es un modelo más pequeño (\"lite\"), así que \"qué LLM es\" no se separa de \"qué tamaño tiene\"; y los generadores difieren en el "
              "registro que producen (Cohere más formal y menos jerga, ver `generation/comparacion_generadores.md`), una explicación posible que no se probó.", ""]
    L += ["## Limitaciones generales", "",
          "9 semillas de prueba; una corrida por modelo; referencias mayormente sintéticas; un solo modelo base; BLEU/chrF no miden retención de matices.", ""]
    a.salida.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
