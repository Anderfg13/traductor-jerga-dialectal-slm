"""
generation/mezclar_datasets.py

Arma el dataset "mezcla" (generadores 1+2+3 juntos): la línea de
comparación del CONTEXTO_PROYECTO.md ("un modelo entrenado sobre la
mezcla completa") contra la que se mide si la fusión de adaptadores
iguala o supera al entrenamiento conjunto (PI2).

Concatena train/val/test de generation/splits/dataset_generador{1,2,3}/.
Como los 3 splits salen del MISMO reparto fijo de semillas
(seeds/split_semillas.json, ver split_dataset.py), una semilla nunca
queda en train para un generador y en test para otro: no hay fuga.

Uso:
    python generation/mezclar_datasets.py

Salida: generation/splits/dataset_mezcla/{train,val,test}.json
"""

import json
import sys
from pathlib import Path

GENERATION_DIR = Path(__file__).resolve().parent
GENERADORES = (1, 2, 3)


def main() -> int:
    out_dir = GENERATION_DIR / "splits" / "dataset_mezcla"
    out_dir.mkdir(parents=True, exist_ok=True)

    semillas_por_split = {}
    for split in ("train", "val", "test"):
        variantes = []
        for g in GENERADORES:
            ruta = GENERATION_DIR / "splits" / f"dataset_generador{g}" / f"{split}.json"
            if not ruta.exists():
                print(f"ERROR: falta {ruta} (corre consolidar/validar/split_dataset para el generador {g})")
                return 1
            variantes.extend(json.loads(ruta.read_text(encoding="utf-8")))
        semillas_por_split[split] = {v["seed_id"] for v in variantes}
        (out_dir / f"{split}.json").write_text(json.dumps(variantes, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{split}: {len(variantes)} variantes, {len(semillas_por_split[split])} semillas")

    solapes = (
        (semillas_por_split["train"] & semillas_por_split["val"])
        | (semillas_por_split["train"] & semillas_por_split["test"])
        | (semillas_por_split["val"] & semillas_por_split["test"])
    )
    if solapes:
        print(f"VERIFICACIÓN FALLIDA: semillas en más de un split: {sorted(solapes)}")
        return 1
    print(f"Verificación OK: ninguna semilla repetida entre splits. Guardado en {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
