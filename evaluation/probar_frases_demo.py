"""
evaluation/probar_frases_demo.py

Traduce una lista de frases con el modelo DESPLEGADO (base Qwen2.5-3B-Instruct +
el adaptador de api/space/adapter, que es el promedio exacto de los tres
generadores, `peft_cat_norm`) y, opcionalmente, con DeepL como referencia, para
elegir qué frases mostrar en la demo. No usa el test común.

En CPU tarda ~1 minuto por frase (ver evaluation/pi3_portabilidad.md): sirve para
preparar la demo, no para mostrarla en vivo (para eso, el Space: ~2.5 s).
Un modelo ya descargado funciona sin internet (HF_HUB_OFFLINE=1).

    python evaluation/probar_frases_demo.py frases.txt salida.json [--deepl]

`frases.txt`: una frase por línea, con el dialecto opcional tras `|`.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "finetuning"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import torch  # noqa: E402
from peft import PeftModel  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

import probar_baseline  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("frases", type=Path)
    p.add_argument("salida", type=Path)
    p.add_argument("--deepl", action="store_true")
    a = p.parse_args()
    items = []
    for linea in a.frases.read_text(encoding="utf-8").splitlines():
        if linea.strip():
            texto, _, dial = linea.partition("|")
            items.append({"texto": texto.strip(), "dialecto": dial.strip()})

    previo = {x["texto"]: x for x in json.loads(a.salida.read_text(encoding="utf-8"))} if a.salida.exists() else {}
    tok = AutoTokenizer.from_pretrained(probar_baseline.MODEL_ID)
    base = AutoModelForCausalLM.from_pretrained(probar_baseline.MODEL_ID, dtype=torch.bfloat16, device_map="cpu")
    modelo = PeftModel.from_pretrained(base, str(RAIZ / "api" / "space" / "adapter")).merge_and_unload()
    modelo.eval()

    deepl = None
    if a.deepl:
        from dotenv import load_dotenv

        import comparar_comerciales as cc

        load_dotenv(RAIZ / ".env")
        clave = os.environ.get("DEEPL_API_KEY", "").strip()
        if clave:
            deepl = lambda t: cc.traducir_con_reintento(cc.traducir_deepl, clave, t)  # noqa: E731

    for i, it in enumerate(items, 1):
        r = previo.get(it["texto"], dict(it))
        if "modelo" not in r:
            t0 = time.time()
            r["modelo"] = probar_baseline.traducir(tok, modelo, it["texto"])
            r["segundos"] = round(time.time() - t0, 1)
        if deepl and "deepl" not in r:
            r["deepl"] = deepl(it["texto"])
        previo[it["texto"]] = r
        a.salida.write_text(json.dumps(list(previo.values()), ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{i}/{len(items)} ({r.get('segundos')} s)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
