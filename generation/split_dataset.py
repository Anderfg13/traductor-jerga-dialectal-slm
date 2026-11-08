"""
generation/split_dataset.py

Divide un dataset limpio (salida de validar.py, ej.
generation/dataset_generador1_limpio.json) en train/val/test
80/10/10, para el fine-tuning (Semana 3+).

La unidad que se reparte entre splits es la SEMILLA (`seed_id`), no la
variante individual: todas las variantes de una misma semilla van al
mismo split. Si se repartieran variantes sueltas, el modelo podría ver
en entrenamiento una variante de "Está brutal" y en test otra variante
de esa misma semilla — casi memorizar la respuesta en vez de aprender a
generalizar (fuga de datos).

El split además es estratificado por `dialecto_region`: se reparten las
semillas 80/10/10 DENTRO de cada dialecto por separado (no sobre el
total mezclado), para que ningún dialecto quede ausente o subrepresentado
en val/test solo por mala suerte del muestreo aleatorio.

El reparto de semillas es FIJO e igual para todos los generadores (ver
`cargar_split_semillas`); un generador al que se le filtró alguna
semilla simplemente no tiene variantes de ella en ese split.

Uso:
    python generation/split_dataset.py [ruta_dataset_limpio]

Salidas (en generation/splits/<nombre_dataset>/):
    train.json, val.json, test.json
"""

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

GENERATION_DIR = Path(__file__).resolve().parent
SEMILLA_ALEATORIA = 42
PROPORCIONES = {"train": 0.8, "val": 0.1, "test": 0.1}


def repartir_semillas(seed_ids: list[str], rng: random.Random) -> dict[str, list[str]]:
    seed_ids = sorted(seed_ids)  # orden determinista antes de barajar
    rng.shuffle(seed_ids)
    n = len(seed_ids)
    n_train = round(n * PROPORCIONES["train"])
    n_val = round(n * PROPORCIONES["val"])
    return {
        "train": seed_ids[:n_train],
        "val": seed_ids[n_train:n_train + n_val],
        "test": seed_ids[n_train + n_val:],
    }


SPLIT_SEMILLAS_PATH = GENERATION_DIR.parent / "seeds" / "split_semillas.json"


def cargar_split_semillas() -> dict[str, list[str]]:
    """Reparto FIJO de TODAS las semillas (seeds/lote_*.json) en
    train/val/test, estratificado por dialecto. Depende solo de las
    semillas y de SEMILLA_ALEATORIA, no de qué variantes sobrevivieron
    al filtrado de un generador concreto: así los 3 generadores se
    entrenan y evalúan con EXACTAMENTE las mismas semillas por split
    (requisito para comparar generadores, PI1) y el test se puede
    evaluar contra las traducciones de referencia humanas de las
    semillas. Se guarda en seeds/split_semillas.json."""
    por_dialecto = defaultdict(list)
    for lote in sorted((GENERATION_DIR.parent / "seeds").glob("lote_*.json")):
        for semilla in json.loads(lote.read_text(encoding="utf-8")):
            por_dialecto[semilla["dialecto_region"]].append(semilla["id"])

    rng = random.Random(SEMILLA_ALEATORIA)
    reparto_total = {"train": [], "val": [], "test": []}
    for dialecto in sorted(por_dialecto):
        reparto = repartir_semillas(por_dialecto[dialecto], rng)
        for split, ids in reparto.items():
            reparto_total[split].extend(ids)
    reparto_total = {k: sorted(v) for k, v in reparto_total.items()}
    SPLIT_SEMILLAS_PATH.write_text(json.dumps(reparto_total, ensure_ascii=False, indent=2), encoding="utf-8")
    return reparto_total


def main() -> int:
    dataset_path = Path(sys.argv[1]) if len(sys.argv) > 1 else GENERATION_DIR / "dataset_generador1_limpio.json"
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))

    variantes_por_semilla = defaultdict(list)
    for variante in dataset:
        variantes_por_semilla[variante["seed_id"]].append(variante)

    reparto_fijo = cargar_split_semillas()
    semillas_por_split = {
        split: [i for i in ids if i in variantes_por_semilla] for split, ids in reparto_fijo.items()
    }

    splits = {}
    for split, seed_ids in semillas_por_split.items():
        variantes = []
        for seed_id in seed_ids:
            variantes.extend(variantes_por_semilla[seed_id])
        splits[split] = variantes

    # --- verificacion: ninguna semilla en mas de un split, los tamanos suman el total ---
    ids_por_split = {split: set(semillas_por_split[split]) for split in splits}
    solapes = []
    nombres = list(ids_por_split.keys())
    for i in range(len(nombres)):
        for j in range(i + 1, len(nombres)):
            interseccion = ids_por_split[nombres[i]] & ids_por_split[nombres[j]]
            if interseccion:
                solapes.append((nombres[i], nombres[j], interseccion))

    suma_variantes = sum(len(v) for v in splits.values())
    if solapes or suma_variantes != len(dataset):
        print("VERIFICACION FALLIDA:")
        for a, b, interseccion in solapes:
            print(f"  semillas repetidas entre {a} y {b}: {interseccion}")
        if suma_variantes != len(dataset):
            print(f"  suma de variantes en splits ({suma_variantes}) != total del dataset ({len(dataset)})")
        return 1

    out_dir = GENERATION_DIR / "splits" / dataset_path.stem.replace("_limpio", "")
    out_dir.mkdir(parents=True, exist_ok=True)
    for split, variantes in splits.items():
        (out_dir / f"{split}.json").write_text(
            json.dumps(variantes, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    print("Verificación OK: ninguna semilla repetida entre splits, tamaños suman el total.")
    print(f"Semillas -> train: {len(semillas_por_split['train'])}, val: {len(semillas_por_split['val'])}, test: {len(semillas_por_split['test'])}")
    print(f"Variantes -> train: {len(splits['train'])}, val: {len(splits['val'])}, test: {len(splits['test'])} (total {suma_variantes})")
    print(f"Guardado en {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
