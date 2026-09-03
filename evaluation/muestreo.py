"""
Muestreo aleatorio de validacion manual (Sesion 10).

Toma el 15% de las variantes de generation/dataset_generadorN.json,
de forma proporcional a la cantidad de variantes por dialecto (no una
muestra global ciega), y escribe evaluation/muestreo_manual.csv con una
fila por variante muestreada, lista para que un evaluador humano llene
la columna `calificacion` (correcta / parcial / incorrecta) y
`comentario`.

Uso:
    python evaluation/muestreo.py
    python evaluation/muestreo.py --dataset generation/dataset_generador1.json --pct 0.15 --seed 42
"""

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path


def muestrear_proporcional(dataset, pct, seed):
    random.seed(seed)
    por_dialecto = defaultdict(list)
    for i, item in enumerate(dataset):
        por_dialecto[item["dialecto_region"]].append(i)

    indices_muestra = []
    for dialecto, indices in por_dialecto.items():
        n = round(len(indices) * pct)
        n = max(n, 1) if indices else 0
        indices_muestra.extend(random.sample(indices, n))

    indices_muestra.sort()
    return indices_muestra


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="generation/dataset_generador1.json")
    parser.add_argument("--out", default="evaluation/muestreo_manual.csv")
    parser.add_argument("--pct", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    dataset = json.loads(Path(args.dataset).read_text(encoding="utf-8"))
    indices = muestrear_proporcional(dataset, args.pct, args.seed)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id_muestra", "seed_id", "dialecto_region", "texto_dialectal",
            "traduccion", "contexto_uso", "calificacion", "comentario",
        ])
        for id_muestra, idx in enumerate(indices, start=1):
            item = dataset[idx]
            writer.writerow([
                id_muestra,
                item["seed_id"],
                item["dialecto_region"],
                item["texto_dialectal"],
                item["traduccion"],
                item.get("contexto_uso", ""),
                "",
                "",
            ])

    por_dialecto = defaultdict(int)
    for idx in indices:
        por_dialecto[dataset[idx]["dialecto_region"]] += 1

    print(f"Dataset: {args.dataset} ({len(dataset)} variantes)")
    print(f"Muestra: {len(indices)} variantes ({100*len(indices)/len(dataset):.1f}%)")
    print("Por dialecto:")
    for dialecto, n in sorted(por_dialecto.items()):
        print(f"  {dialecto}: {n}")
    print(f"Escrito en {out_path}")


if __name__ == "__main__":
    main()
