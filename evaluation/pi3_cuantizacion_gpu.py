"""
evaluation/pi3_cuantizacion_gpu.py

PI3: calidad (BLEU/chrF sobre el test común), tamaño en memoria de GPU y
velocidad de la cuantización del modelo fusionado, con bitsandbytes en GPU
(COMPUTO PESADO: correr en Colab, ver CONTEXTO_PROYECTO.md).

Modelo: base Qwen2.5-3B-Instruct + el adaptador del promedio exacto de los tres
generadores (`finetuning/checkpoints/peft_cat_norm/fusion`), fusionado en los
pesos con `merge_and_unload` y luego cargado/cuantizado. Las tres variantes se
miden en la MISMA sesión, para que la comparación sea limpia:

  fp16 : referencia sin cuantizar
  int8 : bitsandbytes LLM.int8() (8 bits)
  nf4  : bitsandbytes NF4 (4 bits)

OJO: es cuantización de bitsandbytes en GPU, que NO es la misma que la
cuantización dinámica de PyTorch en CPU de `pi3_cuantizacion.py`. Sirve para
saber cuánta calidad se pierde al pasar a 8 y 4 bits, no para medir la
latencia en CPU.

    python evaluation/pi3_cuantizacion_gpu.py --variante fp16
    python evaluation/pi3_cuantizacion_gpu.py --variante int8
    python evaluation/pi3_cuantizacion_gpu.py --variante nf4

Salida: evaluation/predicciones_cuant/gpu_<variante>.json (reanudable) y una
línea JSON con el resumen. Después: `python evaluation/pi3_cuantizacion_gpu.py --informe`
genera evaluation/pi3_cuantizacion_calidad.md (BLEU/chrF con IC por semilla).
"""

import argparse
import json
import random
import statistics
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EVAL = Path(__file__).resolve().parent
ADAPTER = RAIZ / "finetuning" / "checkpoints" / "peft_cat_norm" / "fusion"
SALIDA = EVAL / "predicciones_cuant"
VARIANTES = ["fp16", "int8", "nf4"]


def correr(variante: str) -> None:
    sys.path.insert(0, str(RAIZ / "finetuning"))
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    import probar_baseline

    assert torch.cuda.is_available(), "Se necesita GPU (Colab: T4)"
    tok = AutoTokenizer.from_pretrained(probar_baseline.MODEL_ID)
    # Se fusiona en fp16 y se guarda, para cuantizar los pesos YA fusionados (no base + adaptador por separado).
    base = AutoModelForCausalLM.from_pretrained(probar_baseline.MODEL_ID, dtype=torch.float16, device_map="cuda")
    fusionado = PeftModel.from_pretrained(base, str(ADAPTER)).merge_and_unload()
    tmp = Path(tempfile.mkdtemp()) / "fusionado"
    fusionado.save_pretrained(tmp)
    tok.save_pretrained(tmp)
    del fusionado, base
    torch.cuda.empty_cache()

    kwargs = {"device_map": "cuda"}
    if variante == "fp16":
        kwargs["dtype"] = torch.float16
    elif variante == "int8":
        kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
    else:
        kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
    modelo = AutoModelForCausalLM.from_pretrained(tmp, **kwargs)
    modelo.eval()
    mem_gb = modelo.get_memory_footprint() / 1e9

    test = json.loads((EVAL / "test_comun.json").read_text(encoding="utf-8"))
    SALIDA.mkdir(exist_ok=True)
    ruta = SALIDA / f"gpu_{variante}.json"
    hechos = {x["texto_dialectal"]: x for x in json.loads(ruta.read_text(encoding="utf-8"))} if ruta.exists() else {}
    for i, item in enumerate(test, 1):
        if item["texto_dialectal"] in hechos:
            continue
        t0 = time.time()
        sal = probar_baseline.traducir(tok, modelo, item["texto_dialectal"])
        hechos[item["texto_dialectal"]] = {**item, "traduccion_modelo": sal, "segundos": round(time.time() - t0, 2)}
        if i % 20 == 0 or i == len(test):
            ruta.write_text(json.dumps(list(hechos.values()), ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"  {variante}: {i}/{len(test)}", flush=True)
    ruta.write_text(json.dumps(list(hechos.values()), ensure_ascii=False, indent=1), encoding="utf-8")
    lat = [x["segundos"] for x in hechos.values()]
    print(json.dumps({"variante": variante, "memoria_gpu_modelo_gb": round(mem_gb, 2), "n": len(hechos),
                      "latencia_mediana_s": round(statistics.median(lat), 2), "gpu": torch.cuda.get_device_name(0)}, ensure_ascii=False))


def informe() -> None:
    import sacrebleu

    test = json.loads((EVAL / "test_comun.json").read_text(encoding="utf-8"))
    ref = {t["texto_dialectal"]: t["traduccion"] for t in test}
    sem = {t["texto_dialectal"]: t["seed_id"] for t in test}
    pred = {}
    for v in VARIANTES:
        r = SALIDA / f"gpu_{v}.json"
        if r.exists():
            pred[v] = {x["texto_dialectal"]: x["traduccion_modelo"] for x in json.loads(r.read_text(encoding="utf-8"))}
    completas = {v: p for v, p in pred.items() if len(p) == len(ref)}
    L = ["# PI3: efecto de la cuantización sobre la calidad (bitsandbytes, GPU)", "",
         "Generado por `evaluation/pi3_cuantizacion_gpu.py --informe`. Modelo: base + adaptador del promedio exacto (`peft_cat_norm`) fusionado, "
         "mismo test común (174 entradas, 9 semillas). **Es cuantización de bitsandbytes en GPU, no la dinámica de PyTorch en CPU** "
         "(`evaluation/pi3_portabilidad.md`).", ""]
    if "fp16" not in completas:
        L += ["No hay corrida completa de la variante de referencia fp16: no se puede comparar.", ""]
    else:
        L += ["| Variante | BLEU | chrF | ΔBLEU vs fp16 (IC 95 %) | ΔchrF vs fp16 (IC 95 %) |", "|---|---|---|---|---|"]
        textos = list(ref)
        por = defaultdict(list)
        for t in textos:
            por[sem[t]].append(t)
        ss = sorted(por)
        for v, p in completas.items():
            hip, r = [p[t] for t in textos], [[ref[t] for t in textos]]
            b, c = sacrebleu.corpus_bleu(hip, r).score, sacrebleu.corpus_chrf(hip, r).score
            if v == "fp16":
                L.append(f"| fp16 (referencia) | {b:.1f} | {c:.1f} | — | — |")
                continue
            rng = random.Random(42)
            d = ([], [])
            for _ in range(1000):
                it = [t for s in [rng.choice(ss) for _ in ss] for t in por[s]]
                rr = [[ref[t] for t in it]]
                for k, f in enumerate((sacrebleu.corpus_bleu, sacrebleu.corpus_chrf)):
                    d[k].append(f([p[t] for t in it], rr).score - f([completas["fp16"][t] for t in it], rr).score)
            celdas = []
            for x in d:
                x = sorted(x)
                lo, hi = x[25], x[974]
                celdas.append(f"{sum(x) / len(x):+.1f} [{lo:+.1f}, {hi:+.1f}]" + ("" if lo <= 0 <= hi else " *"))
            L.append(f"| {v} | {b:.1f} | {c:.1f} | {celdas[0]} | {celdas[1]} |")
        L += ["", "`*` = el intervalo no incluye 0 (pérdida o ganancia distinguible). Memoria y latencia de cada variante: ver la línea JSON que imprime cada corrida (se anotan a mano en esta sección).", ""]
    texto = "\n".join(L)
    (EVAL / "pi3_cuantizacion_calidad.md").write_text(texto, encoding="utf-8")
    print(texto)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--variante", choices=VARIANTES)
    p.add_argument("--informe", action="store_true")
    a = p.parse_args()
    if a.informe:
        informe()
    elif a.variante:
        correr(a.variante)
    else:
        p.error("indica --variante o --informe")
    return 0


if __name__ == "__main__":
    sys.exit(main())
