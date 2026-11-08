"""
evaluation/pi3_cuantizacion.py

PI3 (eficiencia): mide el efecto de CUANTIZAR el mejor modelo disponible en
tamaño en disco, memoria, velocidad de inferencia en CPU y calidad
(BLEU/chrF sobre el mismo test común), y permite correrlo con TODA conexión de
red bloqueada.

Modelo: el modelo base Qwen2.5-3B-Instruct + el adaptador del promedio exacto
de los tres generadores (`finetuning/checkpoints/peft_cat_norm/fusion`,
43.5 BLEU / 58.1 chrF en GPU), fusionado en los pesos (`merge_and_unload`).
Es matemáticamente el mismo promedio que la fusión lineal de mergekit (el
mejor modelo, 44.2 / 58.4, cuyo modelo completo no se conserva localmente).

Variantes (todas en CPU):
  bf16 : bfloat16 (como en la evaluación en GPU; en CPU suele ser lento)
  fp32 : float32 (sin cuantizar)
  int8 : float32 con las capas lineales cuantizadas dinámicamente a 8 bits
         (`torch.ao.quantization.quantize_dynamic`, pesos int8, activaciones
         cuantizadas al vuelo). NO es cuantización de 4 bits: esa requiere
         bitsandbytes, que solo funciona con GPU NVIDIA.

    python evaluation/pi3_cuantizacion.py --variante int8 --n 5 --bloquear-red
    python evaluation/pi3_cuantizacion.py --variante int8 --n 174          # calidad completa (reanudable)

Salida: evaluation/predicciones_cuant/<variante>.json (reanudable) y una
línea JSON con el resumen (tamaño, RAM, latencias).
"""

import argparse
import json
import os
import statistics
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EVAL = Path(__file__).resolve().parent
ADAPTER = RAIZ / "finetuning" / "checkpoints" / "peft_cat_norm" / "fusion"
SALIDA = EVAL / "predicciones_cuant"


def bloquear_red():
    import socket

    intentos = {"n": 0}

    def bloquear(*a, **k):
        intentos["n"] += 1
        raise OSError("RED BLOQUEADA por la prueba de portabilidad")

    socket.socket.connect = bloquear
    socket.socket.connect_ex = bloquear
    socket.create_connection = bloquear
    socket.getaddrinfo = bloquear
    return intentos


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--variante", choices=["bf16", "fp32", "int8"], required=True)
    p.add_argument("--n", type=int, default=5, help="cuántas entradas del test común traducir (default 5)")
    p.add_argument("--bloquear-red", action="store_true")
    p.add_argument("--medir-tam", action="store_true", help="guardar el modelo en un temporal para medir su tamaño en disco")
    a = p.parse_args()

    if a.bloquear_red:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        intentos = bloquear_red()
    else:
        intentos = {"n": None}

    sys.path.insert(0, str(RAIZ / "finetuning"))
    import psutil
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    import probar_baseline

    proc = psutil.Process()
    pico = [0.0]

    def ram():
        r = proc.memory_info().rss / 1e9
        pico[0] = max(pico[0], r)
        return r

    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(probar_baseline.MODEL_ID)
    dtype = torch.bfloat16 if a.variante == "bf16" else torch.float32
    modelo = AutoModelForCausalLM.from_pretrained(probar_baseline.MODEL_ID, dtype=dtype, device_map="cpu")
    modelo = PeftModel.from_pretrained(modelo, str(ADAPTER)).merge_and_unload()
    modelo.eval()
    ram()
    if a.variante == "int8":
        import torch.ao.quantization as q

        modelo = q.quantize_dynamic(modelo, {torch.nn.Linear}, dtype=torch.qint8, inplace=True)
    carga = time.time() - t0
    ram()

    tam_gb = None
    if a.medir_tam:
        tmp = Path(tempfile.gettempdir()) / f"pi3_tam_{a.variante}.pt"
        torch.save(modelo.state_dict(), tmp)
        tam_gb = tmp.stat().st_size / 1e9
        tmp.unlink()
    else:
        tam_gb = sum(x.numel() * x.element_size() for x in modelo.parameters()) / 1e9

    test = json.loads((EVAL / "test_comun.json").read_text(encoding="utf-8"))[: a.n]
    SALIDA.mkdir(exist_ok=True)
    ruta = SALIDA / f"{a.variante}.json"
    hechos = {x["texto_dialectal"]: x for x in json.loads(ruta.read_text(encoding="utf-8"))} if ruta.exists() else {}
    for i, item in enumerate(test, 1):
        if item["texto_dialectal"] in hechos:
            continue
        t1 = time.time()
        sal = probar_baseline.traducir(tok, modelo, item["texto_dialectal"])
        hechos[item["texto_dialectal"]] = {**item, "traduccion_modelo": sal, "segundos": round(time.time() - t1, 2)}
        ram()
        if i % 10 == 0 or i == len(test):
            ruta.write_text(json.dumps(list(hechos.values()), ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"  {a.variante}: {i}/{len(test)}", file=sys.stderr, flush=True)
    ruta.write_text(json.dumps(list(hechos.values()), ensure_ascii=False, indent=1), encoding="utf-8")

    lat = [x["segundos"] for x in hechos.values() if "segundos" in x]
    print(json.dumps({"variante": a.variante, "tamano_gb": round(tam_gb, 2), "medido_en_disco": a.medir_tam, "segundos_carga": round(carga, 1),
                      "ram_pico_gb": round(pico[0], 2), "n": len(hechos), "latencia_mediana_s": round(statistics.median(lat), 2) if lat else None,
                      "latencia_min_max_s": [min(lat), max(lat)] if lat else None, "intentos_de_conexion": intentos["n"],
                      "ejemplos": [(x["texto_dialectal"], x["traduccion_modelo"]) for x in list(hechos.values())[:3]]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
