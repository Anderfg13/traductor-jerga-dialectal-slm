"""
finetuning/verificar_config_identica.py

Verifica que TODOS los adaptadores entrenados (generadores 1, 2, 3 y
mezcla) salieron con la MISMA configuración de LoRA y de entrenamiento,
de modo que la única variable que cambia sea el dataset (condición para
que la comparación de PI1 sea válida). Falla (código 1) nombrando el
campo exacto que difiere.

Dos comprobaciones:
  1. La configuración EN EL CÓDIGO de finetuning/entrenar_lora.py (se
     lee con `ast`, sin ejecutarlo): LoraConfig, TrainingArguments y
     constantes. Es un único script para todos los datasets, así que
     esta es la configuración de todos; se imprime para dejar constancia.
  2. Los `adapter_config.json` realmente guardados por cada
     entrenamiento (finetuning/checkpoints/<nombre>/adapter/): se
     comparan entre sí y contra el código. Los checkpoints que todavía
     no existen se reportan como pendientes, no como error.

    python finetuning/verificar_config_identica.py
"""

import ast
import json
import sys
from pathlib import Path

FT = Path(__file__).resolve().parent
SCRIPT = FT / "entrenar_lora.py"
CHECKPOINTS = ["generador1", "generador2", "generador3", "mezcla"]
CAMPOS_ADAPTER = ["peft_type", "task_type", "base_model_name_or_path", "r", "lora_alpha", "lora_dropout", "bias", "target_modules"]


def kwargs_de_llamada(arbol, nombre):
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Call) and getattr(nodo.func, "id", getattr(nodo.func, "attr", None)) == nombre:
            if any(k.arg for k in nodo.keywords):
                return {k.arg: ast.unparse(k.value) for k in nodo.keywords if k.arg}
    return {}


def constantes(arbol, nombres):
    out = {}
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign) and isinstance(nodo.targets[0], ast.Name) and nodo.targets[0].id in nombres:
            out[nodo.targets[0].id] = ast.unparse(nodo.value)
    return out


def main() -> int:
    arbol = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    lora = kwargs_de_llamada(arbol, "LoraConfig")
    train = kwargs_de_llamada(arbol, "TrainingArguments") or {}
    # TrainingArguments(**kwargs): los valores viven en el dict kwargs_entrenamiento
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Assign) and getattr(nodo.targets[0], "id", None) == "kwargs_entrenamiento" and isinstance(nodo.value, ast.Call):
            train = {k.arg: ast.unparse(k.value) for k in nodo.value.keywords if k.arg}
    consts = constantes(arbol, {"EPOCAS_COMPLETO_MAX", "PATIENCE_DEFAULT", "SEMILLA_ALEATORIA", "MAX_LENGTH"})

    print(f"== Configuración en el código ({SCRIPT.name}), idéntica para todo dataset ==")
    print("LoraConfig:", {k: v for k, v in lora.items() if k != "task_type"})
    print("TrainingArguments:", {k: train[k] for k in ("per_device_train_batch_size", "learning_rate", "num_train_epochs") if k in train})
    print("Constantes:", consts)

    problemas = []
    esperado = {"r": 8, "lora_alpha": 16, "lora_dropout": 0.05, "bias": "none",
                "target_modules": ["k_proj", "o_proj", "q_proj", "v_proj"]}
    adapters = {}
    for nombre in CHECKPOINTS:
        ruta = FT / "checkpoints" / nombre / "adapter" / "adapter_config.json"
        if ruta.exists():
            cfg = json.loads(ruta.read_text(encoding="utf-8"))
            cfg["target_modules"] = sorted(cfg["target_modules"])
            adapters[nombre] = {c: cfg.get(c) for c in CAMPOS_ADAPTER}

    print("\n== adapter_config.json guardados ==")
    pendientes = [n for n in CHECKPOINTS if n not in adapters]
    for nombre, cfg in adapters.items():
        print(f"  {nombre}: r={cfg['r']} alpha={cfg['lora_alpha']} dropout={cfg['lora_dropout']} bias={cfg['bias']} módulos={cfg['target_modules']}")
        for campo, valor in esperado.items():
            if cfg[campo] != valor:
                problemas.append(f"{nombre}: {campo} = {cfg[campo]!r}, esperado {valor!r} (el del código)")
    if pendientes:
        print(f"  (aún sin entrenar/traer al repo: {', '.join(pendientes)})")

    base = next(iter(adapters), None)
    for nombre, cfg in adapters.items():
        for campo in CAMPOS_ADAPTER:
            if cfg[campo] != adapters[base][campo]:
                problemas.append(f"{nombre} vs {base}: {campo} difiere ({cfg[campo]!r} vs {adapters[base][campo]!r})")

    if problemas:
        print("\nCONFIGURACIÓN DISTINTA — la comparación de PI1 NO es válida:")
        for p in problemas:
            print("  -", p)
        return 1
    print(f"\nOK: {len(adapters)} adaptador(es) con configuración idéntica entre sí y con el código; "
          f"{len(pendientes)} pendiente(s) de comparar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
