"""
evaluation/verificar_ciego.py

Comprueba que las hojas de evaluación humana (evaluation/evaluacion_humana/
hojas/*.csv) son realmente CIEGAS, usando la clave privada. Mira cinco
cosas que podrían permitir a un evaluador adivinar qué modelo produjo cada
traducción:

  1. Las hojas solo tienen las columnas esperadas y ninguna celda contiene
     un nombre de modelo, proveedor o técnica.
  2. La posición (A/B/C) no delata al modelo: reparto de posiciones por modelo.
  3. La longitud no delata al modelo: palabras por traducción y por modelo.
  4. Cada ítem tiene a los TRES modelos representados (misma comparación
     para todos) y ninguna opción repetida.
  5. Los identificadores de ítem y de opción no codifican el modelo.

El informe nombra a los modelos, así que se escribe en un archivo PRIVADO
(ignorado por git). No lo compartas con los evaluadores.

    python evaluation/verificar_ciego.py
"""

import csv
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

DIR = Path(__file__).resolve().parent / "evaluacion_humana"
COLUMNAS = ["id_item", "opcion", "dialecto", "texto_dialectal", "traduccion", "calificacion", "comentario"]
PROHIBIDAS = re.compile(r"generador|groq|cohere|google|gemini|qwen|lora|mergekit|fusion|fusión|adapter|adaptador|mezcla|baseline|gpt|command", re.I)


def main() -> int:
    clave = json.loads((DIR / "clave_modelos.json").read_text(encoding="utf-8"))
    problemas, avisos = [], []
    pos = defaultdict(Counter)
    palabras = defaultdict(list)
    por_item = defaultdict(lambda: defaultdict(list))  # item -> opcion -> modelos
    n_filas = 0

    for hoja in sorted((DIR / "hojas").glob("*.csv")):
        with hoja.open(encoding="utf-8-sig", newline="") as f:
            lector = csv.DictReader(f)
            if lector.fieldnames != COLUMNAS:
                problemas.append(f"{hoja.name}: columnas inesperadas {lector.fieldnames}")
            for fila in lector:
                n_filas += 1
                for col, val in fila.items():
                    if PROHIBIDAS.search(val or ""):
                        problemas.append(f"{hoja.name} {fila['id_item']}|{fila['opcion']}: la columna '{col}' contiene '{PROHIBIDAS.search(val).group(0)}'")
                modelos = clave.get(f"{fila['id_item']}|{fila['opcion']}")
                if modelos is None:
                    problemas.append(f"{hoja.name}: {fila['id_item']}|{fila['opcion']} no está en la clave")
                    continue
                por_item[fila["id_item"]][fila["opcion"]] = modelos
                for m in modelos:
                    pos[m][fila["opcion"]] += 1
                    palabras[m].append(len(fila["traduccion"].split()))
                if PROHIBIDAS.search(fila["id_item"] + fila["opcion"]):
                    problemas.append(f"identificador que codifica un modelo: {fila['id_item']}|{fila['opcion']}")

    todos = sorted(pos)
    for item, opciones in por_item.items():
        presentes = {m for ms in opciones.values() for m in ms}
        if presentes != set(todos):
            problemas.append(f"{item}: no tiene a los tres modelos ({sorted(presentes)})")
    L = ["# Verificación del diseño ciego (PRIVADO: nombra a los modelos)", "",
         f"{n_filas} filas, {len(por_item)} ítems, {len(todos)} modelos.", "", "## Posición (A/B/C) por modelo", "",
         "| Modelo | A | B | C |", "|---|---|---|---|"]
    for m in todos:
        tot = sum(pos[m].values())
        L.append(f"| {m} | " + " | ".join(f"{100 * pos[m][o] / tot:.0f} % ({pos[m][o]})" for o in "ABC") + " |")
        # con tres opciones el reparto esperado es ~33 %; con menos, algo mayor en A y B
        if max(pos[m][o] / tot for o in "ABC") > 0.5:
            avisos.append(f"{m}: más del 50 % de sus traducciones cae en la misma posición")
    L += ["", "## Longitud (palabras por traducción) por modelo", "", "| Modelo | Media | Mediana |", "|---|---|---|"]
    medias = {}
    for m in todos:
        medias[m] = statistics.mean(palabras[m])
        L.append(f"| {m} | {medias[m]:.1f} | {statistics.median(palabras[m]):.1f} |")
    if max(medias.values()) / min(medias.values()) > 1.2:
        avisos.append(f"las longitudes medias difieren más de 20 % entre modelos ({', '.join(f'{m} {v:.1f}' for m, v in medias.items())}): "
                      "un evaluador atento podría inferir que la opción más larga es de un modelo concreto")
    L += ["", "## Resultado", ""]
    L += [f"- PROBLEMA: {p}" for p in problemas] or ["- Sin problemas de filtración de nombres, columnas, claves ni cobertura."]
    L += [f"- AVISO: {a}" for a in avisos] or ["- Sin avisos de posición ni de longitud."]
    texto = "\n".join(L) + "\n"
    (DIR / "verificacion_ciego_PRIVADO.md").write_text(texto, encoding="utf-8")
    print(texto)
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
