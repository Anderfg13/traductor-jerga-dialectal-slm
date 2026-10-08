"""
evaluation/generar_predicciones.py

Genera las traducciones de UN modelo sobre el test común
(evaluation/test_comun.json) para luego calcular BLEU/chrF con
evaluation/metricas_automaticas.py. COMPUTO PESADO: correr en Colab con
GPU (ver CONTEXTO_PROYECTO.md, "CÓMPUTO PESADO").

Qué modelo evalúa (usa SIEMPRE el mismo prompt y decodificación que el
resto del proyecto, vía finetuning/probar_baseline.traducir):
  - sin --adapter:            el modelo base zero-shot (línea base)
  - --adapter <carpeta>:      base + un adaptador LoRA ya guardado
                              (generadores 1/2/3, mezcla, o una fusión
                              guardada con merging/fusionar_adaptadores.py)

Uso:
    python evaluation/generar_predicciones.py --nombre baseline
    python evaluation/generar_predicciones.py --nombre generador1 \
        --adapter finetuning/checkpoints/generador1/adapter

Salida: evaluation/predicciones/<nombre>.json (mismos campos que
test_comun.json + `traduccion_modelo`).
"""

import argparse
import json
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
    p.add_argument("--nombre", required=True, help="nombre del modelo, se usa en el archivo de salida")
    p.add_argument("--adapter", type=Path, default=None, help="carpeta del adaptador LoRA (omitir = modelo base)")
    p.add_argument("--test", type=Path, default=RAIZ / "evaluation" / "test_comun.json")
    p.add_argument("--salida-dir", type=Path, default=RAIZ / "evaluation" / "predicciones")
    a = p.parse_args()

    test = json.loads(a.test.read_text(encoding="utf-8"))
    cuda = torch.cuda.is_available()
    print(f"Modelo: {a.nombre} | adapter: {a.adapter} | GPU: {cuda} | {len(test)} entradas")

    tokenizer = AutoTokenizer.from_pretrained(probar_baseline.MODEL_ID)
    modelo = AutoModelForCausalLM.from_pretrained(
        probar_baseline.MODEL_ID, dtype=torch.bfloat16, device_map="auto" if cuda else "cpu"
    )
    if a.adapter is not None:
        modelo = PeftModel.from_pretrained(modelo, str(a.adapter))
    modelo.eval()

    inicio = time.monotonic()
    salidas = []
    for i, item in enumerate(test, 1):
        salidas.append({**item, "traduccion_modelo": probar_baseline.traducir(tokenizer, modelo, item["texto_dialectal"])})
        if i % 20 == 0 or i == len(test):
            print(f"  {i}/{len(test)} ({time.monotonic() - inicio:.0f}s)")

    a.salida_dir.mkdir(parents=True, exist_ok=True)
    ruta = a.salida_dir / f"{a.nombre}.json"
    ruta.write_text(json.dumps(salidas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Guardado en {ruta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
