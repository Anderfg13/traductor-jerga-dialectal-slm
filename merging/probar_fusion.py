"""
merging/probar_fusion.py

Prueba manual de coherencia de un modelo fusionado (criterio de
aceptación de la fusión): lo carga, traduce 5 frases y revisa a mano
(y con heurísticas simples) que la salida no sea basura ni texto
repetido, que son las señales típicas de una fusión mal hecha.

Heurísticas por traducción (no sustituyen leerlas):
  - vacía, o idéntica a la entrada (no tradujo);
  - demasiado larga (el modelo no se detiene);
  - fracción de palabras repetidas > 0.5 (bucle de texto repetido);
  - contiene muy pocos caracteres alfabéticos (basura).

    python merging/probar_fusion.py merging/salida/ties
    python merging/probar_fusion.py --adapter finetuning/checkpoints/fusion_ties/fusion   # fusión de PEFT

Sale con código 1 si alguna de las 5 salidas es sospechosa.
"""

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "finetuning"))

import torch  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

import probar_baseline  # noqa: E402

EJEMPLOS = [
    "Che, estoy remando con el sueldo que me dan.",
    "¡Qué chimba de parche, nos vemos más tarde, parcero!",
    "Ese cuate es bien gandalla, no te fíes de él.",
    "No hay bronca, ahorita te marco.",
    "Estar hecho percha después de tanto laburar.",
]


def sospechosa(entrada: str, salida: str) -> str | None:
    s = salida.strip()
    if not s:
        return "salida vacía"
    if s.lower() == entrada.strip().lower():
        return "idéntica a la entrada (no tradujo)"
    palabras = s.lower().split()
    if len(s) > 400 or len(palabras) > 80:
        return "demasiado larga (no se detiene)"
    if len(palabras) >= 6 and len(set(palabras)) / len(palabras) < 0.5:
        return "texto repetido (bucle)"
    if sum(c.isalpha() for c in s) < 0.5 * len(s):
        return "pocos caracteres alfabéticos (basura)"
    return None


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("modelo", nargs="?", type=Path, help="carpeta de un modelo completo (salida de mergekit)")
    p.add_argument("--adapter", type=Path, default=None, help="alternativa: adaptador LoRA sobre el modelo base")
    a = p.parse_args()
    if (a.modelo is None) == (a.adapter is None):
        print("ERROR: da una carpeta de modelo completo O --adapter, no ambos ni ninguno")
        return 1

    cuda = torch.cuda.is_available()
    ruta_modelo = str(a.modelo) if a.modelo else probar_baseline.MODEL_ID
    tokenizer = AutoTokenizer.from_pretrained(probar_baseline.MODEL_ID)
    try:
        modelo = AutoModelForCausalLM.from_pretrained(ruta_modelo, dtype=torch.bfloat16, device_map="auto" if cuda else "cpu")
    except Exception as e:  # noqa: BLE001 - documentar cualquier fallo de carga
        print(f"[FALLO DE CARGA] {type(e).__name__}: {e}")
        return 1
    if a.adapter:
        from peft import PeftModel

        modelo = PeftModel.from_pretrained(modelo, str(a.adapter))
    modelo.eval()

    malas = 0
    for texto in EJEMPLOS:
        salida = probar_baseline.traducir(tokenizer, modelo, texto)
        motivo = sospechosa(texto, salida)
        malas += motivo is not None
        print(f"ES : {texto}\nEN : {salida}\n     -> {'SOSPECHOSA: ' + motivo if motivo else 'ok'}\n")
    print(f"{len(EJEMPLOS) - malas}/{len(EJEMPLOS)} salidas sin señales de fusión rota (revísalas igual a mano).")
    return 1 if malas else 0


if __name__ == "__main__":
    sys.exit(main())
