"""
merging/fusionar_adaptadores.py

Fusiona los adaptadores LoRA de varios generadores en UN solo adaptador
(PI2: ¿la fusión de pesos iguala o supera al mejor modelo individual?).
COMPUTO PESADO: correr en Colab (ver CONTEXTO_PROYECTO.md).

Métodos (los de la propuesta del proyecto):
  - ties      : TIES — recorta los valores pequeños de cada adaptador
                (`--densidad` = fracción que se conserva), resuelve el
                conflicto de signos entre adaptadores y promedia lo que
                coincide.
  - dare_ties : DARE + TIES — descarta al azar una fracción de los
                parámetros de cada adaptador y reescala el resto antes
                de aplicar TIES (`--densidad` = fracción que se conserva).
  - linear    : promedio ponderado simple, como línea de comparación.

Por qué PEFT (`add_weighted_adapter`) y no `mergekit`: los tres
modelos son el MISMO modelo base (Qwen2.5-3B-Instruct) más un adaptador
LoRA con la misma configuración (r=8). PEFT implementa TIES/DARE
directamente sobre los adaptadores, sin materializar tres copias
completas del modelo de 3B (unos 18 GB en disco/RAM, justo en el
límite de Colab gratis). Los adaptadores de entrada deben tener el
mismo rank y módulos objetivo, que es el caso aquí.

Uso:
    python merging/fusionar_adaptadores.py --metodo ties \
        --adaptadores finetuning/checkpoints/generador1/adapter \
                      finetuning/checkpoints/generador2/adapter \
                      finetuning/checkpoints/generador3/adapter \
        --salida finetuning/checkpoints/fusion_ties

El adaptador fusionado queda en <salida>/fusion/ (esa carpeta es la que
se le pasa a evaluation/generar_predicciones.py --adapter).
"""

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "finetuning"))

import torch  # noqa: E402
from peft import PeftModel  # noqa: E402
from transformers import AutoModelForCausalLM  # noqa: E402

import probar_baseline  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--metodo", choices=["ties", "dare_ties", "linear"], required=True)
    p.add_argument("--adaptadores", type=Path, nargs="+", required=True, help="carpetas de adaptadores a fusionar (2 o más)")
    p.add_argument("--pesos", type=float, nargs="+", default=None, help="peso por adaptador (default: todos 1.0)")
    p.add_argument("--densidad", type=float, default=0.5, help="fracción de parámetros que se conserva en ties/dare_ties (default: 0.5)")
    p.add_argument("--salida", type=Path, required=True)
    a = p.parse_args()

    if len(a.adaptadores) < 2:
        print("ERROR: hacen falta al menos 2 adaptadores para fusionar")
        return 1
    pesos = a.pesos or [1.0] * len(a.adaptadores)
    if len(pesos) != len(a.adaptadores):
        print(f"ERROR: {len(a.adaptadores)} adaptadores pero {len(pesos)} pesos")
        return 1
    for ruta in a.adaptadores:
        if not (ruta / "adapter_config.json").exists():
            print(f"ERROR: {ruta} no parece un adaptador (falta adapter_config.json)")
            return 1

    cuda = torch.cuda.is_available()
    base = AutoModelForCausalLM.from_pretrained(
        probar_baseline.MODEL_ID, dtype=torch.bfloat16, device_map="auto" if cuda else "cpu"
    )
    nombres = [f"a{i}" for i in range(len(a.adaptadores))]
    modelo = PeftModel.from_pretrained(base, str(a.adaptadores[0]), adapter_name=nombres[0])
    for nombre, ruta in zip(nombres[1:], a.adaptadores[1:]):
        modelo.load_adapter(str(ruta), adapter_name=nombre)

    kwargs = {} if a.metodo == "linear" else {"density": a.densidad}
    modelo.add_weighted_adapter(
        adapters=nombres, weights=pesos, adapter_name="fusion", combination_type=a.metodo, **kwargs
    )
    modelo.set_adapter("fusion")

    a.salida.mkdir(parents=True, exist_ok=True)
    modelo.save_pretrained(str(a.salida), selected_adapters=["fusion"])
    print(f"Fusión '{a.metodo}' de {len(a.adaptadores)} adaptadores guardada en {a.salida / 'fusion'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
