"""
evaluation/comparacion_completa_pi2.py

Tabla comparativa COMPLETA para PI2 (¿la fusión iguala o supera al mejor
individual y al entrenamiento sobre la mezcla?): base, los tres individuales,
la mezcla, todas las variantes de fusión simple y de TIES/DARE, y la
destilación, sobre el mismo test común. Escribe
evaluation/comparacion_completa_pi2.md.

Las cifras salen de las predicciones (sacrebleu) y los intervalos de
evaluation/analisis_bootstrap.md y analisis_bootstrap_aislar_lineal.md
(bootstrap por semilla, ya calculados).

    python evaluation/comparacion_completa_pi2.py
"""

import json
import re
import sys
from pathlib import Path

import sacrebleu

EVAL = Path(__file__).resolve().parent
sys.path.insert(0, str(EVAL))
from comparacion_fusion import diferencia_bootstrap, fmt  # noqa: E402

FILAS = [
    ("Referencias", None, None),
    ("baseline", "Base sin ajustar", "base"),
    ("Modelos individuales", None, None),
    ("generador1", "LoRA Generador 1 (Groq)", "individual"),
    ("generador2", "LoRA Generador 2 (Cohere)", "individual"),
    ("generador3", "LoRA Generador 3 (Google lite)", "individual"),
    ("Entrenamiento sobre la mezcla de los tres datasets", None, None),
    ("mezcla", "LoRA sobre la mezcla 1+2+3", "mezcla"),
    ("Fusión simple (promedio)", None, None),
    ("mergekit_linear", "Promedio simple, mergekit (modelos completos)", "simple"),
    ("peft_linear_norm", "Promedio simple, PEFT (pesos 1/3)", "simple"),
    ("peft_cat_norm", "Promedio exacto, PEFT cat (pesos 1/3)", "simple"),
    ("fusion_linear", "Promedio PEFT con pesos 1.0 (suma; error de configuración)", "error"),
    ("Fusión TIES / DARE", None, None),
    ("mergekit_ties", "TIES, mergekit (modelos completos)", "ties"),
    ("fusion_ties", "TIES, PEFT", "ties"),
    ("fusion_dare_ties", "DARE+TIES, PEFT", "ties"),
    ("Fusión guiada por destilación", None, None),
    ("destilacion", "Destilación multi-maestro (parte de TIES PEFT)", "destilacion"),
]


def intervalos():
    out = {}
    for arch in ("analisis_bootstrap.md", "analisis_bootstrap_aislar_lineal.md"):
        r = EVAL / arch
        if not r.exists():
            continue
        for m in re.finditer(r"^\| (\w+) \| ([\d.]+) \[([\d.]+), ([\d.]+)\] \| ([\d.]+) \[([\d.]+), ([\d.]+)\] \|$", r.read_text(encoding="utf-8"), re.M):
            n = m.group(1)
            out.setdefault(n, ((float(m.group(3)), float(m.group(4))), (float(m.group(6)), float(m.group(7)))))
    return out


def main() -> int:
    glob, datos = {}, {}
    for n, _, _ in FILAS:
        ruta = EVAL / "predicciones" / f"{n}.json"
        if not ruta.exists():
            continue
        d = json.loads(ruta.read_text(encoding="utf-8"))
        datos[n] = d
        hip = [x["traduccion_modelo"] for x in d]
        ref = [[x["traduccion"] for x in d]]
        glob[n] = (sacrebleu.corpus_bleu(hip, ref).score, sacrebleu.corpus_chrf(hip, ref).score)
    base = [(x["texto_dialectal"], x["traduccion"], x["seed_id"]) for x in datos["baseline"]]
    for n, d in datos.items():
        assert [(x["texto_dialectal"], x["traduccion"], x["seed_id"]) for x in d] == base, f"{n} no se evaluó sobre el mismo conjunto"
    ic = intervalos()

    individuales = [n for n, _, g in FILAS if g == "individual"]
    mejor_ind = max(individuales, key=lambda n: glob[n][1])
    L = ["# Comparación completa para PI2: fusión simple, destilación, mezcla e individuales", "",
         f"Generado por `evaluation/comparacion_completa_pi2.py`. Mismas {len(base)} entradas de {len({b[2] for b in base})} semillas para todos los modelos "
         "(verificado), mismas métricas (sacrebleu). Intervalo de 95 % entre corchetes (bootstrap por semilla).", "",
         "## 1. Todas las variantes", "", "| Modelo | BLEU [IC 95 %] | chrF [IC 95 %] |", "|---|---|---|"]
    for n, et, g in FILAS:
        if et is None:
            L.append(f"| **{n}** | | |")
            continue
        if n not in glob:
            continue
        b, c = glob[n]
        i = ic.get(n)
        cb = f" [{i[0][0]:.1f}, {i[0][1]:.1f}]" if i else ""
        cc = f" [{i[1][0]:.1f}, {i[1][1]:.1f}]" if i else ""
        L.append(f"| {et} | {b:.1f}{cb} | {c:.1f}{cc} |")

    cinco = [("baseline", "Base sin ajustar"), (mejor_ind, f"Mejor individual (criterio fijo: mayor chrF): {dict((n, e) for n, e, _ in FILAS)[mejor_ind]}"),
             ("mezcla", "Entrenar sobre la mezcla"), ("mergekit_linear", "Fusión simple (mergekit)"), ("destilacion", "Fusión por destilación")]
    L += ["", "## 2. Las cinco opciones que compara PI2", "", "| Opción | BLEU | chrF |", "|---|---|---|"]
    orden = sorted(cinco, key=lambda t: glob[t[0]][1], reverse=True)
    for n, et in cinco:
        L.append(f"| {et} | {glob[n][0]:.1f} | {glob[n][1]:.1f} |")
    mejor = max(cinco, key=lambda t: glob[t[0]][0] + glob[t[0]][1] / 1000)[0]  # por BLEU, desempate chrF
    etq = {"baseline": "base", mejor_ind: "mejor individual", "mezcla": "mezcla", "mergekit_linear": "fusión simple", "destilacion": "destilación"}
    L += ["", "Ranking por chrF: " + " > ".join(etq[n] for n, _ in orden) + ". "
          f"Por BLEU, el primero es **{dict(cinco)[mejor]}** ({glob[mejor][0]:.1f}).", "",
          "## 3. ¿Es grande o marginal la diferencia entre fusión simple y destilación?", ""]
    d = diferencia_bootstrap("destilacion", "mergekit_linear")
    L += [f"- Destilación − fusión simple (mergekit): BLEU {fmt(d[0])}, chrF {fmt(d[1])}. "
          + ("**Marginal**: el intervalo incluye 0 en ambas métricas, no se distingue de un empate. " if d[0][1] <= 0 <= d[0][2] and d[1][1] <= 0 <= d[1][2] else "Hay una diferencia distinguible. ")
          + "La destilación costó 95 min de GPU frente a 13 s (promedio simple con PEFT) o ~20 min (con mergekit, contando la incorporación de adaptadores) de la fusión simple (`merging/fusion_destilacion.md`).", ""]
    L += ["## 4. Diferencias clave (con intervalo)", "", "| A − B | ΔBLEU | ΔchrF |", "|---|---|---|"]
    for a, b in [("mergekit_linear", mejor_ind), ("mergekit_linear", "mezcla"), ("destilacion", mejor_ind), ("destilacion", "mezcla"),
                 ("mergekit_ties", "mergekit_linear"), ("destilacion", "mergekit_ties")]:
        dd = diferencia_bootstrap(a, b)
        L.append(f"| {a} − {b} | {fmt(dd[0]) if dd else '—'} | {fmt(dd[1]) if dd else '—'} |")
    L += ["", "`*` = el intervalo no incluye 0.", "",
          "## 5. Respuesta completa (pero cautelosa) a PI2", "",
          "- **¿La fusión iguala o supera al mejor individual?** Lo iguala siempre y, en BLEU, parece superarlo por ~2 puntos con la fusión simple de mergekit "
          "(intervalo que apenas excluye 0); en chrF no se distingue. No se puede afirmar que lo supere.",
          "- **¿Y al entrenamiento sobre la mezcla de todos los datos?** Las fusiones lo superan en BLEU (~+1.3 a +1.9, intervalos que excluyen 0 salvo la destilación); "
          "en chrF solo la fusión simple lo supera con claridad. Es decir, fusionar adaptadores ya entrenados dio un resultado al menos tan bueno como volver a entrenar con "
          "todos los datos, a una fracción del costo (de 13 s a unos 20 min según la herramienta, frente a ~52 min de reentrenar con la mezcla).",
          "- **¿Importa la técnica de fusión?** Con estos datos no: simple, TIES, DARE+TIES y destilación quedan en 43.7-44.2 BLEU, sin diferencias distinguibles entre ellas. "
          "Importa fusionar bien: sumar en vez de promediar dio 35.3.",
          "- **Cautelas**: 9 semillas de prueba, una corrida por modelo, referencias mayormente sintéticas, decenas de comparaciones, sin evaluación humana.", ""]
    texto = "\n".join(L)
    (EVAL / "comparacion_completa_pi2.md").write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
