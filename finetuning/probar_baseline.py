"""
finetuning/probar_baseline.py

Carga un SLM candidato SIN ajustar y prueba su traducción
español->inglés en zero-shot sobre 8 ejemplos reales tomados de
`generation/splits/dataset_generador1/test.json` (split de prueba del
Generador 1, separado del set de entrenamiento/validación en la Sesión
11-12), para dejar una línea base documentada ANTES de empezar el
ajuste fino (LoRA).

Candidato usado: **Qwen2.5-3B-Instruct** (`Qwen/Qwen2.5-3B-Instruct`),
NO Llama 3.2 3B Instruct (candidato principal según
CONTEXTO_PROYECTO.md). Motivo del cambio: `meta-llama/Llama-3.2-3B-Instruct`
tiene `gated="manual"` en HuggingFace (revisión humana de Meta, no
automática) y la cuenta usada para solicitar acceso tenía el correo
sin verificar al momento de correr esto — la descarga falló con
`GatedRepoError` (403, "not in authorized list") pese a tener un
`HF_TOKEN` válido. Qwen2.5-3B-Instruct es la alternativa ya listada en
`CONTEXTO_PROYECTO.md` y no tiene licencia restringida, así que permite
tener el baseline documentado sin bloquearse en la aprobación de
Meta. Cuando el acceso a Llama 3.2 3B quede aprobado, correr este
mismo script cambiando solo `MODEL_ID` reproduce el mismo baseline
para el candidato principal.

Precisión del modelo — bfloat16 SIN cuantizar, en el mejor dispositivo
disponible (GPU si hay CUDA, si no CPU):
  - En la máquina local de desarrollo, el `torch` instalado es la
    build CPU-only (`torch==2.13.0+cpu`; `torch.cuda.is_available()`
    devuelve `False`). La única GPU NVIDIA de esa máquina (MX230)
    tiene 2GB de VRAM: insuficiente incluso para un 3B cuantizado en
    4-bit de forma confiable, y `bitsandbytes` solo acelera de verdad
    con CUDA — sin CUDA no aporta nada, solo complejidad extra. Esa
    máquina sí tiene 18GB de RAM, suficiente para un 3B en bfloat16
    (~6-6.5GB) sin cuantizar.
  - En Google Colab (GPU T4/L4 gratuita, usada para
    `entrenar_lora.py` desde la Sesión 14 — ver BITACORA.md, en la
    máquina local un entrenamiento de prueba tardó ~80-95 min POR
    PASO y se abandonó a las 10h con 5% de avance), la VRAM libre
    (~15GB) también alcanza de sobra para un 3B en bfloat16 sin
    cuantizar.
  - **Conclusión**: en ambos casos no hace falta cuantizar — el
    modelo se carga tal cual en bfloat16 (`torch_dtype=torch.bfloat16`),
    con `device_map="auto"` para usar la GPU automáticamente cuando
    esté disponible (Colab) y caer a CPU si no (máquina local). El
    cuello de botella real es la ausencia de GPU en la máquina local
    (por eso conviene Colab para entrenar), no la memoria disponible
    en ninguno de los dos entornos.

Salida: guarda las 8 traducciones generadas (crudas, sin editar) en
finetuning/baseline_sin_ajustar_salidas.json. El análisis narrado de
los errores va en finetuning/baseline_sin_ajustar.md (escrito a mano a
partir de esta salida).

Uso:
    python finetuning/probar_baseline.py

Qwen2.5-3B-Instruct es público (no requiere token), pero si hay un
HF_TOKEN en .env se usa igual (no estorba, y hace falta el día que se
cambie MODEL_ID a un modelo con licencia restringida como Llama 3.2).
"""

import json
import os
from pathlib import Path

import torch
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer

load_dotenv()

MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"
TEST_PATH = Path(__file__).resolve().parent.parent / "generation" / "splits" / "dataset_generador1" / "test.json"
OUT_JSON = Path(__file__).resolve().parent / "baseline_sin_ajustar_salidas.json"

# Índices elegidos a mano dentro de test.json para cubrir los 4
# dialectos del lote (Caribeña, Andina, Rioplatense, Mexicana) con una
# mezcla de registro informal/jerga, 2 ejemplos por dialecto.
INDICES_MUESTRA = [0, 4, 5, 8, 11, 14, 17, 20]

SYSTEM_PROMPT = (
    "Traduce del español al inglés la frase que te dé el usuario. "
    "Responde ÚNICAMENTE con la traducción al inglés, sin explicaciones "
    "ni texto adicional."
)


def cargar_modelo():
    token = os.environ.get("HF_TOKEN") or None  # Qwen2.5 es público; no hace falta token
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=token)
    modelo = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        token=token,
        torch_dtype=torch.bfloat16,
        device_map="auto" if torch.cuda.is_available() else "cpu",
    )
    modelo.eval()
    return tokenizer, modelo


def traducir(tokenizer, modelo, texto: str) -> str:
    mensajes = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": texto},
    ]
    entrada = tokenizer.apply_chat_template(
        mensajes, add_generation_prompt=True, return_tensors="pt", return_dict=True
    )
    entrada = {k: v.to(modelo.device) for k, v in entrada.items()}
    with torch.no_grad():
        salida = modelo.generate(
            **entrada,
            max_new_tokens=80,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    texto_generado = tokenizer.decode(salida[0][entrada["input_ids"].shape[1]:], skip_special_tokens=True)
    return texto_generado.strip()


def main() -> int:
    test = json.loads(TEST_PATH.read_text(encoding="utf-8"))
    muestra = [test[i] for i in INDICES_MUESTRA]

    print(f"Cargando {MODEL_ID} en bfloat16 (CPU, sin cuantizar)...")
    tokenizer, modelo = cargar_modelo()
    print("Modelo cargado. Generando traducciones (zero-shot, sin ajustar)...")

    resultados = []
    for i, ejemplo in enumerate(muestra):
        print(f"  [{i + 1}/{len(muestra)}] {ejemplo['seed_id']} ({ejemplo['dialecto_region']})...")
        salida = traducir(tokenizer, modelo, ejemplo["texto_dialectal"])
        resultados.append(
            {
                "seed_id": ejemplo["seed_id"],
                "dialecto_region": ejemplo["dialecto_region"],
                "registro": ejemplo["registro"],
                "texto_dialectal": ejemplo["texto_dialectal"],
                "traduccion_referencia": ejemplo["traduccion"],
                "traduccion_modelo_sin_ajustar": salida,
            }
        )
        print(f"      -> {salida!r}")

    OUT_JSON.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nGuardado en {OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
