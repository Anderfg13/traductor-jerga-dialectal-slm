"""
evaluation/preparar_evaluacion_humana.py

Arma las hojas de la evaluación humana CIEGA (escala 1-5 de retención
de matices, evaluation/rubrica_humana.md): para cada ítem del test
común se muestran al evaluador las traducciones de varios modelos con
etiquetas anónimas (A, B, C...) en orden aleatorio, sin decir qué modelo
produjo cuál. Si dos modelos dan exactamente la misma traducción, se
muestra una sola opción y se acredita a ambos.

Requisitos previos: haber generado las predicciones de los modelos
(evaluation/generar_predicciones.py, en Colab).

Uso:
    python evaluation/preparar_evaluacion_humana.py \
        --modelos baseline generador1 mezcla fusion_ties destilacion \
        --items-por-dialecto 12

Salidas en evaluation/evaluacion_humana/:
    hojas/<dialecto>.csv      lo que se le manda a los evaluadores (una
                              copia por evaluador; NO incluye la clave)
    clave_modelos.json        qué modelo(s) hay detrás de cada opción
                              ("id_item|opcion" -> [modelos]). PRIVADA:
                              no se le envía a los evaluadores.
    instrucciones_evaluador.md

Cada evaluador devuelve su hoja llena como
evaluation/evaluacion_humana/respuestas/<dialecto>__<nombre>.csv y se
calcula con evaluation/kappa.py (mínimo 3 evaluadores por dialecto).
"""

import argparse
import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
SALIDA = EVAL_DIR / "evaluacion_humana"

INSTRUCCIONES = """# Instrucciones para el evaluador

Gracias por ayudarnos. Eres hablante nativo del dialecto indicado en tu
hoja (`<dialecto>.csv`). Cada fila tiene una expresión en español y UNA
posible traducción al inglés. Para cada fila:

1. Lee `texto_dialectal` (lo que dice el hablante).
2. Lee `traduccion` (la traducción propuesta).
3. Pon en `calificacion` un número de 1 a 5 según qué tanto la
   traducción conserva el **significado y el tono** (no solo si está bien
   escrita en inglés):

| Punto | Significa |
|---|---|
| 5 | Significado y tono/registro se conservan por completo. |
| 4 | Significado intacto, pero el tono queda un poco más neutro/formal. |
| 3 | Se entiende, pero se pierde un matiz importante. |
| 2 | Significado parcialmente distorsionado o ambiguo. |
| 1 | Significado perdido o invertido. |

Si dudas entre dos números, elige el **más bajo**. Si calificas 3 o
menos, escribe en `comentario` una frase de por qué.

Notas:
- Varias filas comparten el mismo `id_item` (la misma frase) con
  traducciones distintas (`opcion` A, B, C...). Califícalas por separado.
- No sabes ni necesitas saber qué sistema produjo cada traducción.
- No consultes a otros evaluadores mientras calificas.
- Guarda el archivo como CSV (UTF-8) con el nombre `<Dialecto>__<tu ID>.csv` (por ejemplo `Andina__E1.csv`; usa el ID que te dieron, no tu nombre) y devuélvelo.
"""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--modelos", nargs="+", required=True, help="nombres de evaluation/predicciones/<nombre>.json")
    p.add_argument("--items-por-dialecto", type=int, default=12)
    p.add_argument("--semilla", type=int, default=42)
    a = p.parse_args()

    preds = {}
    for m in a.modelos:
        ruta = EVAL_DIR / "predicciones" / f"{m}.json"
        if not ruta.exists():
            print(f"ERROR: falta {ruta} (genera las predicciones primero)")
            return 1
        preds[m] = {x["texto_dialectal"]: x for x in json.loads(ruta.read_text(encoding="utf-8"))}

    comunes = set.intersection(*[set(v) for v in preds.values()])
    base = {t: next(iter(preds.values()))[t] for t in comunes}
    por_dialecto = defaultdict(list)
    for t, it in sorted(base.items()):
        por_dialecto[it["dialecto_region"]].append(t)

    rng = random.Random(a.semilla)
    (SALIDA / "hojas").mkdir(parents=True, exist_ok=True)
    (SALIDA / "respuestas").mkdir(parents=True, exist_ok=True)
    clave = {}
    resumen = {}

    for dialecto in sorted(por_dialecto):
        textos = por_dialecto[dialecto]
        # el subconjunto "oro" primero (referencias humanas, sin sesgo de generador)
        textos.sort(key=lambda t: (base[t].get("fuente") != "oro", rng.random()))
        elegidos = textos[: a.items_por_dialecto]
        filas = []
        for n, texto in enumerate(elegidos, 1):
            id_item = f"{dialecto[:3].lower()}-{n:03d}"
            por_traduccion = defaultdict(list)
            for m in a.modelos:
                por_traduccion[preds[m][texto]["traduccion_modelo"].strip()].append(m)
            opciones = list(por_traduccion.items())
            rng.shuffle(opciones)
            for letra, (traduccion, modelos) in zip("ABCDEFGH", opciones):
                clave[f"{id_item}|{letra}"] = modelos
                filas.append(
                    {"id_item": id_item, "opcion": letra, "dialecto": dialecto, "texto_dialectal": texto,
                     "traduccion": traduccion, "calificacion": "", "comentario": ""}
                )
        ruta = SALIDA / "hojas" / f"{dialecto}.csv"
        with ruta.open("w", encoding="utf-8-sig", newline="") as f:  # utf-8-sig: Excel abre bien los acentos
            w = csv.DictWriter(f, fieldnames=list(filas[0]))
            w.writeheader()
            w.writerows(filas)
        resumen[dialecto] = (len(elegidos), len(filas))

    (SALIDA / "clave_modelos.json").write_text(json.dumps(clave, ensure_ascii=False, indent=1), encoding="utf-8")
    (SALIDA / "instrucciones_evaluador.md").write_text(INSTRUCCIONES, encoding="utf-8")
    for d, (n_items, n_filas) in resumen.items():
        print(f"{d}: {n_items} ítems, {n_filas} filas a calificar por evaluador")
    print(f"Hojas en {SALIDA / 'hojas'}. NO envíes clave_modelos.json a los evaluadores.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
