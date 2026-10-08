"""
merging/incorporar_adaptadores.py

Paso previo a `mergekit`: convierte cada adaptador LoRA en un MODELO
COMPLETO (modelo base + adaptador ya incorporado a los pesos, con
`merge_and_unload`), porque `mergekit` fusiona modelos completos, no
adaptadores LoRA sueltos. COMPUTO PESADO (3 modelos de ~6 GB): Colab.

Por qué float16 y no bfloat16: la actualización de un LoRA r=8 es
pequeña frente a los pesos del base; bfloat16 solo tiene 7 bits de
mantisa y puede redondear parte de esa actualización al volver a guardar
los pesos fusionados. float16 tiene 10 bits, así que conserva mejor la
diferencia entre modelos que luego se va a fusionar. Es una decisión
técnica, no verificada contra bfloat16; ver merging/fusion_simple.md.

    python merging/incorporar_adaptadores.py
    python merging/incorporar_adaptadores.py --generadores generador1   # solo uno

Entrada: finetuning/checkpoints/<generadorN>/adapter/
Salida:  merging/modelos_completos/<generadorN>/  (fuera de git, ~6 GB c/u)
"""

import argparse
import gc
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "finetuning"))

import torch  # noqa: E402
from peft import PeftModel  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

import probar_baseline  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--generadores", nargs="+", default=["generador1", "generador2", "generador3"])
    p.add_argument("--salida", type=Path, default=RAIZ / "merging" / "modelos_completos")
    a = p.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(probar_baseline.MODEL_ID)
    for g in a.generadores:
        adapter = RAIZ / "finetuning" / "checkpoints" / g / "adapter"
        if not (adapter / "adapter_config.json").exists():
            print(f"ERROR: falta {adapter}")
            return 1
        destino = a.salida / g
        if (destino / "config.json").exists() and sum(f.stat().st_size for f in destino.glob("*.safetensors")) > 5e9:
            print(f"{g}: ya existe {destino} (completo), se salta", flush=True)
            continue
        t0 = time.time()
        # En GPU el modelo no ocupa la RAM del sistema (Colab gratis tiene ~12.7 GB y el modelo fp16 ya
        # pesa ~6 GB): en la primera corrida real el proceso murió sin traceback en una sesión sin GPU.
        dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"{g}: cargando base en float16 ({dispositivo})...", flush=True)
        base = AutoModelForCausalLM.from_pretrained(probar_baseline.MODEL_ID, dtype=torch.float16, device_map=dispositivo)
        modelo = PeftModel.from_pretrained(base, str(adapter)).merge_and_unload()
        destino.mkdir(parents=True, exist_ok=True)
        # shards de 1 GB: guardar de a pedazos evita el pico de memoria de serializar todo junto
        modelo.save_pretrained(str(destino), safe_serialization=True, max_shard_size="1GB")
        tokenizer.save_pretrained(str(destino))
        tam = sum(f.stat().st_size for f in destino.glob("*.safetensors"))
        if tam < 5e9:
            print(f"ERROR: {g}: pesos guardados incompletos ({tam / 1e9:.1f} GB, se esperaban ~6 GB)", flush=True)
            return 1
        print(f"{g}: modelo completo guardado en {destino} ({tam / 1e9:.1f} GB, {time.time() - t0:.0f} s)", flush=True)
        del modelo, base
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    return 0


if __name__ == "__main__":
    sys.exit(main())
