"""
evaluation/construir_test_comun.py

Construye el conjunto de prueba COMÚN con el que se evalúan todos los
modelos (baseline, adaptadores de los generadores 1/2/3, mezcla y
fusiones), para que la comparación sea justa: mismas entradas para
todos.

Contiene, para las semillas del split `test` (seeds/split_semillas.json):
  - fuente "oro": la expresión original de la semilla con su traducción
    de referencia escrita por el equipo (no generada por ningún LLM).
    Es el subconjunto SIN sesgo hacia ningún generador; es chico (una
    entrada por semilla de test), así que se reporta aparte.
  - fuentes "generador1/2/3": las variantes de test de cada generador
    (generation/splits/dataset_generadorN/test.json). Su referencia es
    la traducción del propio LLM generador, así que un modelo entrenado
    con ese generador puede salir favorecido en "su" fuente — por eso
    se reporta también el desglose por fuente y el oro.

Entradas con el mismo texto_dialectal en varias fuentes se conservan
una sola vez (la primera fuente en el orden oro, 1, 2, 3), porque
metricas_automaticas.py empareja por texto exacto.

Uso:
    python evaluation/construir_test_comun.py

Salida: evaluation/test_comun.json
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = Path(__file__).resolve().parent / "test_comun.json"


def main() -> int:
    split = json.loads((RAIZ / "seeds" / "split_semillas.json").read_text(encoding="utf-8"))
    test_ids = set(split["test"])

    semillas = {}
    for lote in sorted((RAIZ / "seeds").glob("lote_*.json")):
        for s in json.loads(lote.read_text(encoding="utf-8")):
            semillas[s["id"]] = s

    items, vistos = [], set()

    def agregar(texto, traduccion, dialecto, fuente, seed_id):
        clave = texto.strip().lower()
        if clave in vistos:
            return
        vistos.add(clave)
        items.append(
            {
                "texto_dialectal": texto,
                "traduccion": traduccion,
                "dialecto_region": dialecto,
                "fuente": fuente,
                "seed_id": seed_id,
            }
        )

    for sid in sorted(test_ids):
        s = semillas[sid]
        agregar(s["texto_original"], s["traduccion_referencia"], s["dialecto_region"], "oro", sid)

    for g in (1, 2, 3):
        ruta = RAIZ / "generation" / "splits" / f"dataset_generador{g}" / "test.json"
        if not ruta.exists():
            print(f"ADVERTENCIA: falta {ruta}; se omite el generador {g}")
            continue
        for v in json.loads(ruta.read_text(encoding="utf-8")):
            assert v["seed_id"] in test_ids, f"{v['seed_id']} está en test.json pero no en split_semillas.test"
            agregar(v["texto_dialectal"], v["traduccion"], v["dialecto_region"], f"generador{g}", v["seed_id"])

    SALIDA.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    por_fuente = {}
    for it in items:
        por_fuente[it["fuente"]] = por_fuente.get(it["fuente"], 0) + 1
    print(f"{len(items)} entradas en {SALIDA.name}: {por_fuente}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
