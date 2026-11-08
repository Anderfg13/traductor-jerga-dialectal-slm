"""
evaluation/kappa.py

Acuerdo entre evaluadores humanos y puntaje promedio por modelo, a
partir de las hojas de respuestas (evaluation/evaluacion_humana/
respuestas/*.csv) que llenan los hablantes nativos.

Calcula, por dialecto:
  - **Kappa de Fleiss**: acuerdo entre 3 o más evaluadores (la
    propuesta exige mínimo 3 hablantes nativos por dialecto). Trata las
    calificaciones 1-5 como categorías nominales.
  - **Kappa de Cohen ponderado cuadrático** (promedio de todos los
    pares de evaluadores): como la escala 1-5 es ordinal, un 4 vs. 5
    pesa mucho menos que un 1 vs. 5.
y el puntaje promedio (1-5) de cada modelo, desglosado por dialecto.

Formato de cada CSV de respuestas (una fila por traducción evaluada):
    id_item, opcion, dialecto, texto_dialectal, traduccion, calificacion, comentario
más el nombre del evaluador, que se toma del nombre del archivo
(`<dialecto>__<evaluador>.csv`). La clave que dice qué modelo hay detrás
de cada `opcion` está en evaluation/evaluacion_humana/clave_modelos.json
(la evaluación es ciega: los evaluadores nunca la ven).

Uso:
    python evaluation/kappa.py
    python evaluation/kappa.py --dir evaluation/evaluacion_humana --salida evaluation/resultados_evaluacion_humana.md

Interpretación habitual de kappa (Landis y Koch): <0 sin acuerdo,
0-0.20 leve, 0.21-0.40 aceptable, 0.41-0.60 moderado, 0.61-0.80
sustancial, 0.81-1 casi perfecto.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

CATEGORIAS = [1, 2, 3, 4, 5]
DIR_DEFAULT = Path(__file__).resolve().parent / "evaluacion_humana"


def fleiss_kappa(tabla: list[list[int]]) -> float:
    """tabla[i][j] = cuántos evaluadores dieron la categoría j al ítem i.
    Todos los ítems deben tener el mismo número de evaluadores."""
    n_items = len(tabla)
    n_raters = sum(tabla[0])
    assert all(sum(f) == n_raters for f in tabla), "todos los ítems necesitan el mismo número de evaluadores"
    n_cat = len(tabla[0])
    p_j = [sum(f[j] for f in tabla) / (n_items * n_raters) for j in range(n_cat)]
    P_i = [(sum(c * c for c in f) - n_raters) / (n_raters * (n_raters - 1)) for f in tabla]
    P_bar = sum(P_i) / n_items
    P_e = sum(p * p for p in p_j)
    if P_e == 1:
        return 1.0
    return (P_bar - P_e) / (1 - P_e)


def cohen_kappa_ponderado(a: list[int], b: list[int], categorias=CATEGORIAS) -> float:
    """Kappa de Cohen con pesos cuadráticos entre dos evaluadores."""
    k = len(categorias)
    idx = {c: i for i, c in enumerate(categorias)}
    n = len(a)
    obs = [[0.0] * k for _ in range(k)]
    for x, y in zip(a, b):
        obs[idx[x]][idx[y]] += 1 / n
    fila = [sum(obs[i]) for i in range(k)]
    col = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    num = den = 0.0
    for i in range(k):
        for j in range(k):
            w = ((i - j) / (k - 1)) ** 2
            num += w * obs[i][j]
            den += w * fila[i] * col[j]
    if den == 0:
        return 1.0
    return 1 - num / den


def cargar_respuestas(dir_respuestas: Path):
    """-> {dialecto: {evaluador: {(id_item, opcion): calificacion}}} y metadatos."""
    datos = defaultdict(dict)
    for ruta in sorted(dir_respuestas.glob("*.csv")):
        if "__" not in ruta.stem:
            print(f"ADVERTENCIA: {ruta.name} no sigue el formato <dialecto>__<evaluador>.csv, se ignora")
            continue
        dialecto, evaluador = ruta.stem.split("__", 1)
        califs = {}
        with ruta.open(encoding="utf-8", newline="") as f:
            for fila in csv.DictReader(f):
                c = (fila.get("calificacion") or "").strip()
                if not c:
                    continue
                if not c.isdigit() or int(c) not in CATEGORIAS:
                    raise ValueError(f"{ruta.name}: calificación inválida {c!r} (id_item={fila.get('id_item')}); debe ser 1-5")
                califs[(fila["id_item"], fila["opcion"])] = int(c)
        datos[dialecto][evaluador] = califs
    return datos


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dir", type=Path, default=DIR_DEFAULT)
    p.add_argument("--salida", type=Path, default=None)
    a = p.parse_args()

    clave_ruta = a.dir / "clave_modelos.json"
    resp_dir = a.dir / "respuestas"
    if not clave_ruta.exists() or not resp_dir.exists():
        print(f"ERROR: faltan {clave_ruta} o {resp_dir} (corre evaluation/preparar_evaluacion_humana.py y reúne las respuestas)")
        return 1
    clave = json.loads(clave_ruta.read_text(encoding="utf-8"))  # "id_item|opcion" -> modelo
    datos = cargar_respuestas(resp_dir)
    if not datos:
        print(f"ERROR: no hay CSV de respuestas en {resp_dir}")
        return 1

    lineas = ["# Resultados de la evaluación humana", "", "## Acuerdo entre evaluadores", "",
              "| Dialecto | Evaluadores | Ítems en común | Kappa de Fleiss | Kappa de Cohen pond. (prom. pares) |", "|---|---|---|---|---|"]
    promedios = defaultdict(lambda: defaultdict(list))  # modelo -> dialecto -> [calificaciones]
    alerta_minimo = []

    for dialecto in sorted(datos):
        evaluadores = datos[dialecto]
        if len(evaluadores) < 3:
            alerta_minimo.append(f"{dialecto} ({len(evaluadores)} evaluadores)")
        comunes = set.intersection(*[set(c) for c in evaluadores.values()])
        claves = sorted(comunes)
        if len(evaluadores) >= 2 and claves:
            nombres = sorted(evaluadores)
            fleiss = "—"
            if len(nombres) >= 3:
                tabla = [[sum(1 for e in nombres if evaluadores[e][k] == c) for c in CATEGORIAS] for k in claves]
                fleiss = f"{fleiss_kappa(tabla):.3f}"
            pares = [cohen_kappa_ponderado([evaluadores[x][k] for k in claves], [evaluadores[y][k] for k in claves])
                     for x, y in combinations(nombres, 2)]
            lineas.append(f"| {dialecto} | {len(nombres)} | {len(claves)} | {fleiss} | {sum(pares) / len(pares):.3f} |")
        else:
            lineas.append(f"| {dialecto} | {len(evaluadores)} | {len(claves)} | — | — |")

        for evaluador, califs in evaluadores.items():
            for (id_item, opcion), c in califs.items():
                modelos = clave.get(f"{id_item}|{opcion}") or []
                for modelo in ([modelos] if isinstance(modelos, str) else modelos):
                    promedios[modelo][dialecto].append(c)

    dialectos = sorted(datos)
    lineas += ["", "## Puntaje promedio (1-5) por modelo", "", "| Modelo | " + " | ".join(dialectos) + " | Global |",
               "|---|" + "---|" * (len(dialectos) + 1)]
    for modelo in sorted(promedios):
        celdas, todas = [], []
        for d in dialectos:
            v = promedios[modelo].get(d, [])
            todas += v
            celdas.append(f"{sum(v) / len(v):.2f}" if v else "—")
        lineas.append(f"| {modelo} | " + " | ".join(celdas) + f" | {sum(todas) / len(todas):.2f} |")
    if alerta_minimo:
        lineas += ["", f"**ADVERTENCIA**: menos de 3 evaluadores en: {', '.join(alerta_minimo)}. La propuesta exige mínimo 3 hablantes nativos por dialecto."]
    lineas.append("")

    texto = "\n".join(lineas)
    print(texto)
    if a.salida:
        a.salida.write_text(texto, encoding="utf-8")
        print(f"Guardado en {a.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
