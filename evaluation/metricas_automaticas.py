"""
evaluation/metricas_automaticas.py

Calcula BLEU y chrF (via `sacrebleu`) para un conjunto de traducciones
generadas por un modelo, comparadas contra su traducción de
referencia, reportando el resultado global y desglosado por dialecto.

Pensado para ser reutilizable sin tocar el código: recibe las rutas de
los archivos de predicciones y de referencias como parámetros de línea
de comandos, no hardcodeadas, para poder usarlo con cualquier
generador (Generador 1, 2 o 3) o cualquier checkpoint futuro.

Formato esperado de los archivos (JSON, lista de objetos):

  - Referencias (mismo formato que `generation/splits/dataset_*/test.json`):
    cada objeto necesita al menos `texto_dialectal` (el texto de
    entrada, usado como llave para emparejar con las predicciones) y
    `traduccion` (la traducción de referencia). También puede traer
    `dialecto_region` para el desglose por dialecto.

  - Predicciones: cada objeto necesita `texto_dialectal` (la MISMA
    llave que en las referencias) y un campo con la traducción que
    generó el modelo — el nombre de ese campo es configurable con
    `--campo-prediccion` (default: `traduccion_modelo_con_adapter`,
    el nombre que usa `finetuning/entrenar_lora.py`). Si el archivo de
    predicciones ya trae `dialecto_region` se usa esa; si no, se toma
    la de la referencia emparejada.

El emparejamiento entre predicción y referencia es por
`texto_dialectal` exacto (no por `seed_id`, porque un `seed_id` tiene
varias variantes) — cualquier predicción sin una referencia con el
mismo texto se reporta como no emparejada y se excluye del cálculo,
en vez de fallar en silencio.

Uso:
    python evaluation/metricas_automaticas.py \
        --predicciones finetuning/checkpoints/generador1/salidas_con_adapter.json \
        --referencias generation/splits/dataset_generador1/test.json

    python evaluation/metricas_automaticas.py \
        --predicciones ruta/a/predicciones_generador2.json \
        --referencias generation/splits/dataset_generador2/test.json \
        --campo-prediccion prediccion \
        --salida evaluation/reporte_metricas_generador2.md
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import sacrebleu


def cargar(ruta: Path) -> list[dict]:
    return json.loads(ruta.read_text(encoding="utf-8"))


def emparejar(predicciones: list[dict], referencias: list[dict], campo_prediccion: str) -> tuple[list[dict], int]:
    refs_por_texto = {r["texto_dialectal"]: r for r in referencias}

    emparejados = []
    sin_referencia = 0
    for pred in predicciones:
        ref = refs_por_texto.get(pred["texto_dialectal"])
        if ref is None:
            sin_referencia += 1
            continue
        emparejados.append(
            {
                "texto_dialectal": pred["texto_dialectal"],
                "dialecto_region": pred.get("dialecto_region", ref.get("dialecto_region", "desconocido")),
                "prediccion": pred[campo_prediccion],
                "referencia": ref["traduccion"],
            }
        )
    return emparejados, sin_referencia


def calcular_metricas(ejemplos: list[dict]) -> dict:
    hipotesis = [e["prediccion"] for e in ejemplos]
    referencias = [[e["referencia"] for e in ejemplos]]
    bleu = sacrebleu.corpus_bleu(hipotesis, referencias)
    chrf = sacrebleu.corpus_chrf(hipotesis, referencias)
    return {"n": len(ejemplos), "bleu": bleu.score, "chrf": chrf.score}


def generar_reporte(global_: dict, por_dialecto: dict[str, dict], sin_referencia: int) -> str:
    lineas = [
        "# Reporte de métricas automáticas (BLEU / chrF)",
        "",
        f"Ejemplos evaluados: {global_['n']}"
        + (f" ({sin_referencia} predicciones sin referencia emparejada, excluidas)" if sin_referencia else ""),
        "",
        "## Global",
        "",
        f"- BLEU: {global_['bleu']:.2f}",
        f"- chrF: {global_['chrf']:.2f}",
        "",
        "## Por dialecto",
        "",
        "| Dialecto | n | BLEU | chrF |",
        "|---|---|---|---|",
    ]
    for dialecto in sorted(por_dialecto):
        m = por_dialecto[dialecto]
        lineas.append(f"| {dialecto} | {m['n']} | {m['bleu']:.2f} | {m['chrf']:.2f} |")
    lineas.append("")
    return "\n".join(lineas)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--predicciones", type=Path, required=True, help="JSON con las traducciones del modelo")
    parser.add_argument("--referencias", type=Path, required=True, help="JSON con las traducciones de referencia (formato test.json)")
    parser.add_argument(
        "--campo-prediccion",
        default="traduccion_modelo_con_adapter",
        help="Nombre del campo en --predicciones que trae la traducción del modelo (default: %(default)s)",
    )
    parser.add_argument("--salida", type=Path, default=None, help="Si se da, escribe el reporte en este archivo .md además de imprimirlo")
    args = parser.parse_args()

    if not args.predicciones.exists():
        print(f"ERROR: no existe {args.predicciones}")
        return 1
    if not args.referencias.exists():
        print(f"ERROR: no existe {args.referencias}")
        return 1

    predicciones = cargar(args.predicciones)
    referencias = cargar(args.referencias)
    emparejados, sin_referencia = emparejar(predicciones, referencias, args.campo_prediccion)

    if not emparejados:
        print("ERROR: ninguna predicción pudo emparejarse con una referencia.")
        return 1

    global_ = calcular_metricas(emparejados)

    por_texto_dialecto = defaultdict(list)
    for e in emparejados:
        por_texto_dialecto[e["dialecto_region"]].append(e)
    por_dialecto = {dialecto: calcular_metricas(ejs) for dialecto, ejs in por_texto_dialecto.items()}

    reporte = generar_reporte(global_, por_dialecto, sin_referencia)
    print(reporte)

    if args.salida:
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        args.salida.write_text(reporte, encoding="utf-8")
        print(f"\nReporte guardado en {args.salida}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
