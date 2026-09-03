"""
finetuning/entrenar_lora.py

Prueba de humo (smoke test) del pipeline COMPLETO de fine-tuning con
LoRA: carga de datos -> tokenización -> entrenamiento -> guardado del
adaptador -> recarga del adaptador desde disco -> inferencia. Corre
sobre un subconjunto pequeño (50 ejemplos, dentro del rango 50-100
pedido) de `generation/splits/dataset_generador1/train.json` y pocas
épocas. El objetivo NO es un modelo bueno — es confirmar que las
piezas del pipeline encajan de punta a punta, y que la pérdida baja de
forma consistente, ANTES de escalar al entrenamiento completo (Sesión
19+). Este script no existía en el repo (Paula no lo había dejado
listo); se escribió en esta sesión para no bloquear la prueba
end-to-end (ver BITACORA.md).

Modelo base: el mismo candidato usado en la línea base zero-shot
(`finetuning/probar_baseline.py`) — **Qwen2.5-3B-Instruct**, NO Llama
3.2 3B (candidato principal, aún bloqueado por acceso "gated=manual"
de Meta — ver BITACORA.md Sesión 13). Cuando se apruebe el acceso a
Llama, correr este mismo script cambiando `MODEL_ID` (importado de
`probar_baseline.py`) reproduce la prueba con el candidato principal.

Formato de entrenamiento: cada ejemplo usa el MISMO prompt de sistema
que la evaluación zero-shot (`probar_baseline.SYSTEM_PROMPT`) — mismo
formato en entrenamiento y en evaluación, para que el LoRA aprenda
exactamente la tarea que se mide después. La pérdida solo se calcula
sobre los tokens de la respuesta del asistente (los del prompt quedan
enmascarados con `label=-100`), para no premiar al modelo por
"aprender a copiar" el prompt.

Precisión / cómputo — bfloat16 sin cuantizar, GPU si hay disponible:
  **Correr esto en CPU pura NO es viable** — se probó en la máquina
  local de desarrollo (sin GPU CUDA) y un solo paso de entrenamiento
  tardaba 80-95 minutos; a las 10 horas de correr solo se había
  completado el 5% (8 de 150 pasos) y se abandonó. Este script debe
  correrse en un entorno con GPU — **Google Colab (gratis, T4/L4)** es
  el usado para esta prueba (ver `finetuning/entrenar_lora_colab.ipynb`).
  El modelo se carga vía `cargar_modelo()` (importado de
  `probar_baseline.py`), que ya detecta el dispositivo automáticamente
  (`device_map="auto"` si hay CUDA, si no `"cpu"`) y no cuantiza en
  ningún caso: un 3B en bfloat16 pesa ~6-6.5GB, que cabe cómodo tanto
  en la VRAM libre de una GPU gratuita de Colab (~15GB) como en los
  18GB de RAM de la máquina local — cuantizar no habría resuelto el
  problema real, que era la falta de GPU, no de memoria. LoRA además
  ya reduce el costo de memoria de entrenamiento de por sí, porque los
  pesos base quedan congelados: solo se entrenan los adaptadores
  (unos pocos millones de parámetros, no los 3B completos).

Uso (recomendado, en Google Colab):
    Abrir finetuning/entrenar_lora_colab.ipynb en Colab, activar GPU
    (Entorno de ejecución > Cambiar tipo de entorno > GPU) y correr
    las celdas en orden.

Uso (local, solo si hay GPU CUDA disponible; en CPU pura NO
terminará en un tiempo razonable, ver arriba):
    python finetuning/entrenar_lora.py

Salidas:
    finetuning/lora_prueba/adapter/              adaptador LoRA entrenado
    finetuning/lora_prueba/loss_log.json         pérdida por paso, cruda
    finetuning/lora_prueba/salidas_con_adapter.json  traducciones de prueba
        con el adaptador recargado desde disco, sobre los MISMOS 8
        ejemplos de test.json que usa probar_baseline.py — permite
        comparar directamente "antes" (sin ajustar) vs. "después"
        (con LoRA) sobre exactamente los mismos ejemplos.
"""

import gc
import json
import random
import sys
from pathlib import Path

import torch
from peft import LoraConfig, PeftModel, get_peft_model
from transformers import AutoModelForCausalLM, Trainer, TrainerCallback, TrainingArguments, default_data_collator

sys.path.insert(0, str(Path(__file__).resolve().parent))
from probar_baseline import INDICES_MUESTRA, MODEL_ID, SYSTEM_PROMPT, TEST_PATH, cargar_modelo, traducir  # noqa: E402

TRAIN_PATH = Path(__file__).resolve().parent.parent / "generation" / "splits" / "dataset_generador1" / "train.json"
OUT_DIR = Path(__file__).resolve().parent / "lora_prueba"
ADAPTER_DIR = OUT_DIR / "adapter"
LOSS_LOG_PATH = OUT_DIR / "loss_log.json"
SALIDAS_ADAPTER_PATH = OUT_DIR / "salidas_con_adapter.json"

N_EJEMPLOS = 50  # subconjunto pequeño, límite inferior del rango 50-100 pedido (CPU sin GPU: cada paso es caro)
EPOCAS = 3
SEMILLA_ALEATORIA = 42  # misma semilla que generation/split_dataset.py, por consistencia


def cargar_muestra_entrenamiento() -> list[dict]:
    datos = json.loads(TRAIN_PATH.read_text(encoding="utf-8"))
    random.Random(SEMILLA_ALEATORIA).shuffle(datos)
    return datos[:N_EJEMPLOS]


class DatasetTraduccion(torch.utils.data.Dataset):
    """Cada ejemplo: prompt (sistema+usuario) enmascarado con -100 +
    la traducción de referencia como objetivo de la pérdida."""

    def __init__(self, ejemplos: list[dict], tokenizer):
        self.ejemplos = ejemplos
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.ejemplos)

    def __getitem__(self, idx):
        ej = self.ejemplos[idx]
        mensajes_prompt = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": ej["texto_dialectal"]},
        ]
        mensajes_completos = mensajes_prompt + [{"role": "assistant", "content": ej["traduccion"]}]

        # apply_chat_template sin return_tensors devuelve un BatchEncoding
        # (dict-like), no una lista de ids directamente -> hay que sacar
        # "input_ids" explícitamente (ver BITACORA.md, bug encontrado en
        # esta misma sesión).
        ids_prompt = self.tokenizer.apply_chat_template(mensajes_prompt, add_generation_prompt=True)["input_ids"]
        ids_completos = self.tokenizer.apply_chat_template(mensajes_completos, add_generation_prompt=False)[
            "input_ids"
        ]

        etiquetas = list(ids_completos)
        n_prompt = min(len(ids_prompt), len(etiquetas))
        for i in range(n_prompt):
            etiquetas[i] = -100

        return {
            "input_ids": torch.tensor(ids_completos, dtype=torch.long),
            "attention_mask": torch.ones(len(ids_completos), dtype=torch.long),
            "labels": torch.tensor(etiquetas, dtype=torch.long),
        }


class RegistrarPerdida(TrainerCallback):
    def __init__(self):
        self.historial = []

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs and "loss" in logs:
            self.historial.append({"paso": state.global_step, "epoca": round(state.epoch, 3), "loss": logs["loss"]})


def entrenar() -> RegistrarPerdida:
    dispositivo = "GPU (CUDA)" if torch.cuda.is_available() else "CPU"
    print(f"Cargando {MODEL_ID} en bfloat16 (sin cuantizar) para entrenar, dispositivo: {dispositivo}...")
    tokenizer, modelo_base = cargar_modelo()

    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )
    modelo = get_peft_model(modelo_base, lora_config)
    modelo.print_trainable_parameters()

    muestra = cargar_muestra_entrenamiento()
    print(f"Entrenando sobre {len(muestra)} ejemplos de train.json, {EPOCAS} épocas...")
    dataset = DatasetTraduccion(muestra, tokenizer)

    registrador = RegistrarPerdida()
    args_entrenamiento = TrainingArguments(
        output_dir=str(OUT_DIR / "checkpoints"),
        per_device_train_batch_size=1,
        num_train_epochs=EPOCAS,
        learning_rate=2e-4,
        logging_steps=1,
        save_strategy="no",
        report_to=[],
        remove_unused_columns=False,
    )
    trainer = Trainer(
        model=modelo,
        args=args_entrenamiento,
        train_dataset=dataset,
        data_collator=default_data_collator,
        callbacks=[registrador],
    )
    trainer.train()

    ADAPTER_DIR.mkdir(parents=True, exist_ok=True)
    modelo.save_pretrained(str(ADAPTER_DIR))
    tokenizer.save_pretrained(str(ADAPTER_DIR))
    print(f"Adaptador LoRA guardado en {ADAPTER_DIR}")

    LOSS_LOG_PATH.write_text(json.dumps(registrador.historial, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Curva de pérdida guardada en {LOSS_LOG_PATH}")

    # Liberar el modelo de entrenamiento de memoria antes de recargar desde
    # disco — así la prueba de inferencia de abajo usa de verdad el
    # adaptador guardado en disco, no el objeto que quedó en memoria.
    del trainer, modelo, modelo_base
    gc.collect()

    return registrador


def probar_adapter_recargado():
    print(f"\nRecargando {MODEL_ID} + adaptador LoRA desde disco ({ADAPTER_DIR})...")
    tokenizer, modelo_base = cargar_modelo()
    modelo_ajustado = PeftModel.from_pretrained(modelo_base, str(ADAPTER_DIR))
    modelo_ajustado.eval()
    print("Adaptador recargado. Generando traducciones de prueba (mismos ejemplos que el baseline)...")

    test = json.loads(TEST_PATH.read_text(encoding="utf-8"))
    muestra = [test[i] for i in INDICES_MUESTRA]

    resultados = []
    for i, ejemplo in enumerate(muestra):
        salida = traducir(tokenizer, modelo_ajustado, ejemplo["texto_dialectal"])
        resultados.append(
            {
                "seed_id": ejemplo["seed_id"],
                "dialecto_region": ejemplo["dialecto_region"],
                "registro": ejemplo["registro"],
                "texto_dialectal": ejemplo["texto_dialectal"],
                "traduccion_referencia": ejemplo["traduccion"],
                "traduccion_modelo_con_adapter": salida,
            }
        )
        print(f"  [{i + 1}/{len(muestra)}] {ejemplo['seed_id']} -> {salida!r}")

    SALIDAS_ADAPTER_PATH.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nGuardado en {SALIDAS_ADAPTER_PATH}")


def main() -> int:
    registrador = entrenar()
    if not registrador.historial:
        print("ERROR: no se registró ninguna pérdida durante el entrenamiento.")
        return 1
    probar_adapter_recargado()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
