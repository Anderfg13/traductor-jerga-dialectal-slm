"""
merging/analisis_lineal_peft.py

Aísla, con los adaptadores LoRA reales (sin inferencia), por qué el
promedio simple hecho con PEFT (`combination_type="linear"`, pesos 1.0)
quedó por debajo del modelo base mientras que el promedio simple de
`mergekit` sobre modelos completos funcionó.

Para cada matriz objetivo (q/k/v/o de cada capa) y con
D_i = s * B_i @ A_i la actualización del adaptador i (s = alpha / r):

  ideal      = (D_1 + D_2 + D_3) / 3             lo que hace mergekit "linear"
  peft_w1    = s * (sum B_i) @ (sum A_i)         lo que hizo nuestra corrida (pesos 1.0)
  peft_w1_3  = peft_w1 / 3                       PEFT con pesos normalizados a 1/3

PEFT "linear" promedia por separado A y B (con raíz de peso en cada lado,
ver peft/tuners/lora/model.py `_generalized_task_arithmetic_weighted_adapter`),
de modo que el producto es la suma de TODOS los pares B_i A_j: los 3
términos diagonales (la suma de las actualizaciones) más 6 términos
cruzados B_i A_j (i != j), que ningún adaptador entrenó.

Mide: factor de escala frente al ideal, similitud coseno, y la energía
de los términos cruzados. Salida: merging/analisis_lineal_peft.md.

    python merging/analisis_lineal_peft.py
"""

import json
import sys
from pathlib import Path

import torch
from safetensors.torch import load_file

RAIZ = Path(__file__).resolve().parent.parent
GENS = ["generador1", "generador2", "generador3"]


def cargar(g):
    cfg = json.loads((RAIZ / "finetuning" / "checkpoints" / g / "adapter" / "adapter_config.json").read_text(encoding="utf-8"))
    w = load_file(str(RAIZ / "finetuning" / "checkpoints" / g / "adapter" / "adapter_model.safetensors"))
    return cfg["lora_alpha"] / cfg["r"], w


def coseno(x, y):
    return (x.flatten() @ y.flatten() / (x.norm() * y.norm())).item()


def main() -> int:
    adaptadores = [cargar(g) for g in GENS]
    s = adaptadores[0][0]
    claves_A = sorted(k for k in adaptadores[0][1] if k.endswith("lora_A.weight"))

    filas = []
    por_tipo = {}
    cos_A_entre_adaptadores = []
    for kA in claves_A:
        kB = kA.replace("lora_A", "lora_B")
        A = [w[kA].float() for _, w in adaptadores]
        B = [w[kB].float() for _, w in adaptadores]
        D = [s * b @ a for a, b in zip(A, B)]
        ideal = sum(D) / 3
        suma_D = sum(D)
        peft_w1 = s * sum(B) @ sum(A)
        cruzados = peft_w1 - suma_D  # los 6 términos B_i A_j (i != j)
        peft_w13 = peft_w1 / 3
        n_ideal = ideal.norm().item()
        fila = {
            "escala_w1": peft_w1.norm().item() / n_ideal,
            "cos_w1": coseno(peft_w1, ideal),
            "err_w13": (peft_w13 - ideal).norm().item() / n_ideal,
            "cos_w13": coseno(peft_w13, ideal),
            "cruz_vs_ideal": (cruzados / 3).norm().item() / n_ideal,
            "cruz_vs_suma": cruzados.norm().item() / suma_D.norm().item(),
        }
        filas.append(fila)
        tipo = kA.split(".")[-3]  # q_proj / k_proj ...
        por_tipo.setdefault(tipo, []).append(fila)
        cos_A_entre_adaptadores.append(coseno(A[0], A[1]))

    def media(lst, k):
        return sum(f[k] for f in lst) / len(lst)

    L = [
        "# Aislar por qué el promedio simple con PEFT salió mal", "",
        "Generado por `merging/analisis_lineal_peft.py` con los adaptadores reales de los generadores 1, 2 y 3 "
        f"(`{len(filas)}` matrices objetivo; `s = alpha/r = {s:g}`). **No requiere inferencia**: compara las actualizaciones de pesos.", "",
        "## Qué compara", "",
        "- **ideal** = promedio de las tres actualizaciones `(D1+D2+D3)/3` (lo que hace `mergekit` lineal, con normalización).",
        "- **PEFT w=1** = lo que corrimos: pesos 1.0 por adaptador, sin normalizar. PEFT promedia por separado A y B, así que el "
        "producto es la suma de los 9 pares `B_i A_j`: 3 diagonales (la suma de las actualizaciones, o sea 3 veces el promedio) y 6 cruzados.",
        "- **PEFT w=1/3** = el mismo método con pesos normalizados.", "",
        "## Resultados (promedio sobre todas las matrices)", "",
        "| Magnitud | Valor |", "|---|---|",
        f"| Norma de PEFT w=1 / norma del ideal | **{media(filas, 'escala_w1'):.2f}** (si fuera exactamente la suma sin cruzados sería 3.00) |",
        f"| Coseno entre PEFT w=1 y el ideal | {media(filas, 'cos_w1'):.3f} |",
        f"| Energía de los 6 términos cruzados, relativa a la suma de las actualizaciones | {media(filas, 'cruz_vs_suma'):.3f} |",
        f"| Energía de los términos cruzados (con w=1/3), relativa al ideal | {media(filas, 'cruz_vs_ideal'):.3f} |",
        f"| Error relativo de PEFT w=1/3 frente al ideal | {media(filas, 'err_w13'):.3f} |",
        f"| Coseno entre PEFT w=1/3 y el ideal | {media(filas, 'cos_w13'):.3f} |",
        f"| Coseno entre las matrices A de dos adaptadores distintos | {sum(cos_A_entre_adaptadores) / len(cos_A_entre_adaptadores):.3f} |",
        "",
        "## Por tipo de matriz", "",
        "| Matriz | Escala PEFT w=1 / ideal | Coseno w=1 | Error relativo w=1/3 | Energía cruzada vs. ideal |", "|---|---|---|---|---|",
    ]
    for tipo, lst in sorted(por_tipo.items()):
        L.append(f"| {tipo} | {media(lst, 'escala_w1'):.2f} | {media(lst, 'cos_w1'):.3f} | {media(lst, 'err_w13'):.3f} | {media(lst, 'cruz_vs_ideal'):.3f} |")
    L += [
        "## Resultado posterior: qué causaba el fallo (experimento con inferencia)", "",
        "Este análisis de pesos hacía sospechar de los términos cruzados (energía 1.22 veces la de la señal). El experimento "
        "`merging/aislar_lineal_peft_colab.ipynb` lo **refutó**: PEFT `linear` con pesos normalizados a 1/3 (conserva los cruzados) dio "
        "43.6 BLEU / 58.1 chrF y PEFT `cat` con pesos 1/3 (promedio exacto, sin cruzados) 43.5 / 58.1, indistinguibles entre sí y +8.5 BLEU "
        "por encima del original con pesos 1.0. **La causa era la escala (sumar en vez de promediar)**, no los términos cruzados. "
        "Ver `merging/fusion_simple.md` y `evaluation/analisis_bootstrap_aislar_lineal.md`.", "",
    ]
    L.append("")
    texto = "\n".join(L)
    (RAIZ / "merging" / "analisis_lineal_peft.md").write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
