"""
evaluation/consolidar_resultados_humanos.py

Reúne las hojas que devuelven los evaluadores
(evaluation/evaluacion_humana/respuestas/<dialecto>__<evaluador>.csv) en
UN archivo largo, evaluation/resultados_humanos_pi1.csv, con una fila por
(evaluador, ítem, opción) y el modelo que hay detrás ya resuelto con la
clave. Es el formato que usa evaluation/kappa.py.

NO inventa nada: si no hay respuestas, o faltan calificaciones, o una hoja
fue alterada, avisa y NO escribe el archivo.

Validaciones por hoja devuelta:
  - mismas filas que la hoja original (id_item, opcion, texto y traducción
    sin cambios: nadie editó el contenido);
  - toda fila con calificación entera de 1 a 5;
  - el evaluador no calificó dos veces el mismo ítem (nombre de archivo único).
Y por dialecto: mínimo de evaluadores (3 por defecto, el de la propuesta).

    python evaluation/consolidar_resultados_humanos.py
    python evaluation/kappa.py        # luego, acuerdo entre evaluadores
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

EVAL = Path(__file__).resolve().parent


def leer(ruta):
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dir", type=Path, default=EVAL / "evaluacion_humana")
    p.add_argument("--salida", type=Path, default=EVAL / "resultados_humanos_pi1.csv")
    p.add_argument("--minimo", type=int, default=3, help="evaluadores mínimos por dialecto (default 3)")
    a = p.parse_args()

    clave_ruta = a.dir / "clave_modelos.json"
    if not clave_ruta.exists():
        print(f"ERROR: falta {clave_ruta} (la clave privada de la ronda)")
        return 1
    clave = json.loads(clave_ruta.read_text(encoding="utf-8"))
    respuestas = sorted((a.dir / "respuestas").glob("*.csv"))
    if not respuestas:
        print("No hay hojas devueltas en evaluacion_humana/respuestas/: no se escribe nada (no se simulan resultados).")
        return 1

    filas_salida, problemas = [], []
    evaluadores = defaultdict(set)
    for ruta in respuestas:
        if "__" not in ruta.stem:
            problemas.append(f"{ruta.name}: el nombre debe ser <dialecto>__<evaluador>.csv")
            continue
        dialecto, evaluador = ruta.stem.split("__", 1)
        original = a.dir / "hojas" / f"{dialecto}.csv"
        if not original.exists():
            problemas.append(f"{ruta.name}: no existe la hoja original {original.name}")
            continue
        base = {(r["id_item"], r["opcion"]): r for r in leer(original)}
        devuelta = {(r["id_item"], r["opcion"]): r for r in leer(ruta)}
        if set(base) != set(devuelta):
            problemas.append(f"{ruta.name}: las filas no coinciden con la hoja original (faltan {len(set(base) - set(devuelta))}, sobran {len(set(devuelta) - set(base))})")
            continue
        malo = False
        for k, r in devuelta.items():
            if r["texto_dialectal"] != base[k]["texto_dialectal"] or r["traduccion"] != base[k]["traduccion"]:
                problemas.append(f"{ruta.name}: se alteró el contenido de {k}")
                malo = True
                break
            c = (r.get("calificacion") or "").strip()
            if not c.isdigit() or not 1 <= int(c) <= 5:
                problemas.append(f"{ruta.name}: calificación inválida o vacía en {k}: {c!r} (debe ser entero 1-5)")
                malo = True
                break
        if malo:
            continue
        evaluadores[dialecto].add(evaluador)
        for (item, opcion), r in sorted(devuelta.items()):
            filas_salida.append({"dialecto": dialecto, "evaluador": evaluador, "id_item": item, "opcion": opcion,
                                 "modelo": "+".join(clave[f"{item}|{opcion}"]), "texto_dialectal": r["texto_dialectal"],
                                 "traduccion": r["traduccion"], "calificacion": int(r["calificacion"]), "comentario": r.get("comentario", "")})

    dialectos = sorted(p.stem for p in (a.dir / "hojas").glob("*.csv"))
    print("Evaluadores válidos por dialecto:")
    for d in dialectos:
        n = len(evaluadores[d])
        print(f"  {d}: {n}" + ("" if n >= a.minimo else f"  <-- menos del mínimo ({a.minimo})"))
        if n < a.minimo:
            problemas.append(f"{d}: {n} evaluadores válidos, la propuesta exige mínimo {a.minimo}")
    if problemas:
        print("\nPROBLEMAS (no se escribió el archivo):")
        for x in problemas:
            print("  -", x)
        return 1
    campos = ["dialecto", "evaluador", "id_item", "opcion", "modelo", "texto_dialectal", "traduccion", "calificacion", "comentario"]
    with a.salida.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(filas_salida)
    print(f"\nEscrito {a.salida} ({len(filas_salida)} calificaciones). Siguiente: python evaluation/kappa.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
