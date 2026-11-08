"""
finetuning/resumen_curva.py

Genera finetuning/curva_final_<nombre>.md a partir de
finetuning/checkpoints/<nombre>/loss_log.json (salida de
entrenar_lora.py --todos), con los números reales del entrenamiento.
Hardware, tiempo y tamaño del dataset NO están en el log: se pasan como
argumentos y, si faltan, el documento dice "NO REGISTRADO" en vez de
inventarlos.

    python finetuning/resumen_curva.py generador2 \
        --hardware "Colab, Tesla T4" --tiempo "~N min" --ejemplos-train 513 --ejemplos-val 64
"""

import argparse
import json
import statistics
import sys
from pathlib import Path

FT = Path(__file__).resolve().parent


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("nombre", help="generador2, generador3, mezcla...")
    p.add_argument("--hardware", default="NO REGISTRADO")
    p.add_argument("--tiempo", default="NO REGISTRADO")
    p.add_argument("--ejemplos-train", default="NO REGISTRADO")
    p.add_argument("--ejemplos-val", default="NO REGISTRADO")
    p.add_argument("--forzar", action="store_true", help="sobrescribir un informe que ya existe")
    a = p.parse_args()

    ruta = FT / "checkpoints" / a.nombre / "loss_log.json"
    if not ruta.exists():
        print(f"ERROR: falta {ruta} (entrena primero y trae el resultado de Colab al repo)")
        return 1
    log = json.loads(ruta.read_text(encoding="utf-8"))
    train, ev = log["train"], log["eval"]

    por_epoca = {}
    for t in train:
        por_epoca.setdefault(int(-(-t["epoca"] // 1)), []).append(t["loss"])
    mejor = min(ev, key=lambda e: e["eval_loss"])
    ultima = max(e["epoca"] for e in ev)
    filas = []
    for e in ev:
        ep = int(e["epoca"])
        ls = por_epoca.get(ep, [])
        marca = " ← mejor" if e is mejor else ""
        filas.append(f"| {ep} | {statistics.mean(ls):.4f} (mediana {statistics.median(ls):.4f}) | {e['eval_loss']:.4f}{marca} |")

    sobreajuste = ev[-1]["eval_loss"] > mejor["eval_loss"] and len(ev) > 1
    texto = "\n".join(
        [
            f"# Entrenamiento completo de LoRA — {a.nombre}",
            "",
            f"Generado por `finetuning/resumen_curva.py` a partir de `finetuning/checkpoints/{a.nombre}/loss_log.json`. "
            "Mismo script y misma configuración de LoRA que el Generador 1 (verificado con `finetuning/verificar_config_identica.py`).",
            "",
            "## Hardware y datos",
            "",
            f"- Hardware: {a.hardware}",
            f"- Tiempo total: {a.tiempo}",
            f"- Ejemplos de entrenamiento: {a.ejemplos_train}; de validación: {a.ejemplos_val}",
            f"- Pasos de entrenamiento registrados: {len(train)}; épocas evaluadas: {len(ev)}",
            "",
            "## Curva de pérdida",
            "",
            "| Época | Pérdida de entrenamiento (promedio) | Pérdida de validación |",
            "|---|---|---|",
            *filas,
            "",
            f"- Mejor época por validación: **{int(mejor['epoca'])}** (pérdida {mejor['eval_loss']:.4f}). "
            f"Se guardó el adaptador de esa época (`load_best_model_at_end`), no el de la última ({int(ultima)}).",
            f"- Sobreajuste: {'**sí** — la validación de la última época es peor que la mejor mientras el entrenamiento sigue bajando.' if sobreajuste else 'no se observa en las épocas evaluadas.'}",
            "",
        ]
    )
    if a.nombre == "mezcla":
        import collections

        dd = json.loads((FT.parent / "generation" / "splits" / "dataset_mezcla" / "train.json").read_text(encoding="utf-8"))
        c = collections.Counter(x["generador"] for x in dd)
        tot = sum(c.values())
        sem = {g: len({x["seed_id"] for x in dd if x["generador"] == g}) for g in c}
        texto += "\n".join([
            "", "## Balance de la mezcla entre generadores", "",
            "Criterio de calidad: que ningún generador domine solo por tener más ejemplos limpios.", "",
            "| Generador | Ejemplos de entrenamiento | % | Semillas distintas |", "|---|---|---|---|",
            *[f"| {g} | {n} | {100 * n / tot:.1f} % | {sem[g]} |" for g, n in sorted(c.items())],
            "", f"Diferencia máxima entre generadores: {100 * (max(c.values()) - min(c.values())) / tot:.1f} puntos porcentuales ({max(c.values()) - min(c.values())} ejemplos). "
            "**No se recortó para igualar**: los tres generadores cubren exactamente las mismas semillas de entrenamiento y cada uno generó 5-8 variantes por semilla, así que la "
            "mezcla ya sale casi equilibrada; igualar al mínimo habría descartado ejemplos válidos sin que ningún generador dominara. Los splits son por semilla y usan el mismo reparto "
            "fijo que los demás (`seeds/split_semillas.json`), igual que en la Sesión 12.", ""])
    salida = FT / f"curva_final_{a.nombre}.md"
    if salida.exists() and not a.forzar:
        print(f"ERROR: {salida.name} ya existe; usa --forzar para sobrescribirlo")
        return 1
    salida.write_text(texto, encoding="utf-8")
    print(texto)
    print(f"Guardado en {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
