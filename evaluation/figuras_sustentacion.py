"""
evaluation/figuras_sustentacion.py

Genera las figuras de la sustentación final en docs/figuras/ a partir de
las predicciones y los intervalos ya calculados (nada escrito a mano):

  1_resultados_modelos.png  BLEU y chrF de las cinco opciones de PI2 con IC 95 %
  2_costo_vs_calidad.png    tiempo de GPU frente a BLEU por método
  3_errores_cualitativos.png  categorías de error de los 34 peores casos

    python evaluation/figuras_sustentacion.py
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import sacrebleu  # noqa: E402

EVAL = Path(__file__).resolve().parent
SALIDA = EVAL.parent / "docs" / "figuras"
sys.path.insert(0, str(EVAL))
from comparacion_completa_pi2 import intervalos  # noqa: E402

ETIQ = [("baseline", "Base"), ("generador3", "Mejor\nindividual"), ("mezcla", "Entrenar\ncon mezcla"),
        ("mergekit_linear", "Fusión\nsimple"), ("destilacion", "Destilación")]
# segundos de GPU T4, de finetuning/tiempos_fase3_corrida2.json y merging/logs/*.json (ver docs/fase3_costos_y_futuro_borrador.md)
COSTO = [("generador3", "Individual (G3)", 18 * 60), ("mezcla", "Mezcla", 52 * 60),
         ("peft_linear_norm", "Fusión PEFT", 13), ("mergekit_linear", "Fusión mergekit", 466 + 739),
         ("destilacion", "Destilación", 5697)]
COLOR = "#2b6cb0"


def metricas(n):
    d = json.loads((EVAL / "predicciones" / f"{n}.json").read_text(encoding="utf-8"))
    hip, ref = [x["traduccion_modelo"] for x in d], [[x["traduccion"] for x in d]]
    return sacrebleu.corpus_bleu(hip, ref).score, sacrebleu.corpus_chrf(hip, ref).score


def main() -> int:
    SALIDA.mkdir(parents=True, exist_ok=True)
    ic = intervalos()
    m = {n: metricas(n) for n, _ in ETIQ + [(c[0], "") for c in COSTO]}

    fig, ejes = plt.subplots(1, 2, figsize=(11, 4.2))
    for k, (ax, nombre) in enumerate(zip(ejes, ("BLEU", "chrF"))):
        vals = [m[n][k] for n, _ in ETIQ]
        err = [[], []]
        for n, _ in ETIQ:
            i = ic.get(n)
            lo, hi = (i[k] if i else (m[n][k], m[n][k]))
            err[0].append(max(m[n][k] - lo, 0))
            err[1].append(max(hi - m[n][k], 0))
        ax.bar(range(len(ETIQ)), vals, yerr=err, color=[("#a0aec0" if n == "baseline" else COLOR) for n, _ in ETIQ], capsize=4)
        ax.set_xticks(range(len(ETIQ)))
        ax.set_xticklabels([e for _, e in ETIQ], fontsize=9)
        ax.set_title(f"{nombre} (IC 95 %, bootstrap por semilla)")
        ax.set_ylim(min(vals) - 8, max(vals) + 6)
        for x, v in enumerate(vals):
            ax.text(x, v + 0.4, f"{v:.1f}", ha="center", fontsize=9)
    fig.suptitle("Test común: 174 entradas, 9 semillas — las diferencias entre las cuatro ajustadas no son distinguibles", fontsize=10)
    fig.tight_layout()
    fig.savefig(SALIDA / "1_resultados_modelos.png", dpi=160)

    fig, ax = plt.subplots(figsize=(7, 4.2))
    for n, et, seg in COSTO:
        ax.scatter(seg / 60, m[n][0], s=70, color=COLOR)
        ax.annotate(et, (seg / 60, m[n][0]), textcoords="offset points", xytext=(6, 5), fontsize=9)
    ax.set_xscale("log")
    ax.set_xlabel("Minutos de GPU T4 (escala log)")
    ax.set_ylabel("BLEU en el test común")
    ax.set_ylim(36, 46)
    ax.set_title("Costo frente a calidad (fusiones: sin contar los ~57 min de entrenar los 3 adaptadores)", fontsize=8)
    fig.tight_layout()
    fig.savefig(SALIDA / "2_costo_vs_calidad.png", dpi=160)

    # categorías de evaluation/analisis_cualitativo.md (clasificación manual de un solo lector)
    cats = [("Sentido equivocado\n(polisemia)", 8), ("Sustitución por\nexpresión inglesa", 6), ("Pierde matiz", 8),
            ("Literal", 2), ("Aceptable, penalizada\npor la métrica", 10)]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh([c for c, _ in cats][::-1], [v for _, v in cats][::-1], color=COLOR)
    ax.set_xlabel("Casos (de los 34 peor puntuados)")
    ax.set_title("Qué falla: clasificación manual, un solo lector")
    fig.tight_layout()
    fig.savefig(SALIDA / "3_errores_cualitativos.png", dpi=160)
    print("Figuras en", SALIDA)
    return 0


if __name__ == "__main__":
    sys.exit(main())
