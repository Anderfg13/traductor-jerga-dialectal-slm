"""
generation/consolidar.py

Junta las salidas crudas individuales de generation/raw/generador1/*.json
(generadas por generar_sintetico.py, una por semilla) en un solo dataset
consolidado: generation/dataset_generador1.json.

Por cada archivo crudo:
  1. Parsea la `respuesta_cruda` del modelo como JSON (quitando bloques
     de código ```json``` si el modelo los agregó pese a la
     instrucción de no hacerlo — mismo criterio que
     probar_prompt_derivacion.py).
  2. Descarta variantes vacías (texto_dialectal o traduccion en
     blanco) y variantes duplicadas exactas (mismo texto_dialectal,
     comparado recortado y en minúsculas) frente a las ya incluidas en
     el dataset.
  3. Agrega cada variante sobreviviente al dataset consolidado, con
     metadatos de la semilla de origen (dialecto, registro original)
     para no perder trazabilidad.

Semillas cuya salida cruda no parsea como JSON válido (o no aportan
ninguna variante tras el filtrado) se reportan como falladas por
consola y se excluyen del dataset — no tumban el script.

Uso:
    python generation/consolidar.py
"""

import json
import re
import sys
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent / "raw" / "generador1"
SEEDS_PATH = Path(__file__).resolve().parent.parent / "seeds" / "lote_01.json"
OUT_PATH = Path(__file__).resolve().parent / "dataset_generador1.json"


def limpiar_json(texto: str) -> str:
    texto = texto.strip()
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", texto, re.DOTALL)
    return match.group(1) if match else texto


def main() -> int:
    semillas = {s["id"]: s for s in json.loads(SEEDS_PATH.read_text(encoding="utf-8"))}

    dataset = []
    vistos = set()
    semillas_ok = 0
    semillas_falladas = []
    variantes_vacias_descartadas = 0
    variantes_duplicadas_descartadas = 0

    for raw_path in sorted(RAW_DIR.glob("*.json")):
        registro = json.loads(raw_path.read_text(encoding="utf-8"))
        seed_id = registro["seed_id"]
        semilla = semillas.get(seed_id)
        if semilla is None:
            semillas_falladas.append((seed_id, "semilla no encontrada en seeds/lote_01.json"))
            continue

        try:
            salida = json.loads(limpiar_json(registro["respuesta_cruda"]))
            variantes = salida["variantes"]
            if not isinstance(variantes, list):
                raise ValueError("'variantes' no es una lista")
        except Exception as e:  # noqa: BLE001 - reportar cualquier fallo de parseo y seguir
            semillas_falladas.append((seed_id, f"{type(e).__name__}: {e}"))
            continue

        agregadas = 0
        for v in variantes:
            texto = (v.get("texto_dialectal") or "").strip()
            traduccion = (v.get("traduccion") or "").strip()
            if not texto or not traduccion:
                variantes_vacias_descartadas += 1
                continue
            clave = texto.lower()
            if clave in vistos:
                variantes_duplicadas_descartadas += 1
                continue
            vistos.add(clave)
            dataset.append({
                "seed_id": seed_id,
                "dialecto_region": semilla["dialecto_region"],
                "registro_original_semilla": semilla["registro"],
                "texto_dialectal": texto,
                "traduccion": traduccion,
                "registro": v.get("registro", ""),
                "contexto_uso": v.get("contexto_uso", ""),
                "generador": registro.get("generador", "groq"),
                "modelo": registro.get("modelo", ""),
            })
            agregadas += 1

        if agregadas > 0:
            semillas_ok += 1
        else:
            semillas_falladas.append((seed_id, "0 variantes sobrevivieron el filtrado (vacías/duplicadas)"))

    OUT_PATH.write_text(json.dumps(dataset, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Semillas con al menos 1 variante en el dataset: {semillas_ok}")
    print(f"Semillas falladas: {len(semillas_falladas)}")
    for seed_id, motivo in semillas_falladas:
        print(f"  - {seed_id}: {motivo}")
    print(f"Variantes vacías descartadas: {variantes_vacias_descartadas}")
    print(f"Variantes duplicadas exactas descartadas: {variantes_duplicadas_descartadas}")
    print(f"Total variantes en el dataset: {len(dataset)}")
    print(f"Guardado en {OUT_PATH}")

    return 0 if not semillas_falladas else 1


if __name__ == "__main__":
    sys.exit(main())
