"""
merging/destilacion_multimaestro.py

Fusión guiada por DESTILACIÓN MULTI-MAESTRO (segunda técnica de fusión
de la propuesta, PI2). COMPUTO PESADO: correr en Colab con GPU.

Idea: en vez de combinar los pesos de los adaptadores directamente
(TIES/DARE, merging/fusionar_adaptadores.py), se entrena un adaptador
ESTUDIANTE para imitar lo que los 3 adaptadores-maestro (uno por
generador sintético) predicen, token por token, sobre el dataset
mezcla. La señal de entrenamiento combina:

    pérdida = alfa * KL( promedio_de_maestros || estudiante )
            + (1 - alfa) * CE( traducción de referencia | estudiante )

  - KL contra el PROMEDIO de las distribuciones de los maestros: el
    estudiante aprende el "consenso" de los tres generadores, y donde
    discrepan aprende una mezcla suave en vez de elegir uno.
  - CE contra la referencia (como en el entrenamiento normal): ancla al
    estudiante a la traducción correcta.
Ambas se calculan solo sobre los tokens de la respuesta (el prompt de
sistema + usuario queda enmascarado, igual que en entrenar_lora.py).

Los maestros y el estudiante viven en UN solo modelo base con 4
adaptadores LoRA (se cambia de adaptador activo con `set_adapter`), así
que no hace falta cargar el modelo de 3B varias veces. Los maestros
quedan congelados; solo se entrena el estudiante. Con `--inicial` el
estudiante arranca desde una fusión ya hecha (p. ej. la de TIES) en
vez de desde ceros: la destilación la refina en vez de aprender de cero.

Uso:
    python merging/destilacion_multimaestro.py \
        --maestros finetuning/checkpoints/generador1/adapter \
                   finetuning/checkpoints/generador2/adapter \
                   finetuning/checkpoints/generador3/adapter \
        --inicial finetuning/checkpoints/fusion_ties/fusion \
        --dataset-dir generation/splits/dataset_mezcla \
        --salida finetuning/checkpoints/destilacion

El mejor adaptador (menor CE en validación) queda en <salida>/estudiante/.
"""

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "finetuning"))

import torch  # noqa: E402
import torch.nn.functional as F  # noqa: E402
from peft import LoraConfig, PeftModel  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

import probar_baseline  # noqa: E402
from entrenar_lora import DatasetTraduccion, cargar_ejemplos  # noqa: E402


def perdidas(modelo, ids, mask, etiquetas, maestros, alfa):
    """Devuelve (pérdida total, KL, CE) para UN ejemplo."""
    # el modelo puede estar en GPU (Colab) y los tensores del dataset nacen en CPU: indexar un tensor
    # CUDA con una máscara booleana de CPU falla, así que se mueve todo al dispositivo del modelo
    dev = modelo.device
    ids, mask, etiquetas = ids.unsqueeze(0).to(dev), mask.unsqueeze(0).to(dev), etiquetas.unsqueeze(0).to(dev)
    objetivo = etiquetas[:, 1:] != -100  # posiciones de la respuesta (tras el desplazamiento)

    with torch.no_grad():
        probs_maestros = []
        for nombre in maestros:
            modelo.set_adapter(nombre)
            logits = modelo(input_ids=ids, attention_mask=mask).logits[:, :-1][objetivo].float()
            probs_maestros.append(F.softmax(logits, dim=-1))
        prob_promedio = torch.stack(probs_maestros).mean(0)

    modelo.set_adapter("estudiante")
    for n, p in modelo.named_parameters():
        p.requires_grad = "lora_" in n and ".estudiante." in n
    logits_est = modelo(input_ids=ids, attention_mask=mask).logits[:, :-1][objetivo].float()
    log_probs_est = F.log_softmax(logits_est, dim=-1)

    kl = F.kl_div(log_probs_est, prob_promedio, reduction="batchmean")
    ce = F.nll_loss(log_probs_est, etiquetas[:, 1:][objetivo])
    return alfa * kl + (1 - alfa) * ce, kl.item(), ce.item()


def ce_validacion(modelo, val, maestros):
    modelo.set_adapter("estudiante")
    total, n = 0.0, 0
    with torch.no_grad():
        for ej in val:
            dev = modelo.device
            ids, mask, et = (ej["input_ids"].unsqueeze(0).to(dev), ej["attention_mask"].unsqueeze(0).to(dev),
                             ej["labels"].unsqueeze(0).to(dev))
            obj = et[:, 1:] != -100
            lp = F.log_softmax(modelo(input_ids=ids, attention_mask=mask).logits[:, :-1][obj].float(), dim=-1)
            total += F.nll_loss(lp, et[:, 1:][obj]).item()
            n += 1
    return total / max(n, 1)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--maestros", type=Path, nargs="+", required=True, help="adaptadores-maestro (uno por generador)")
    p.add_argument("--inicial", type=Path, default=None, help="adaptador desde el que arranca el estudiante (default: LoRA nuevo)")
    p.add_argument("--dataset-dir", type=Path, default=RAIZ / "generation" / "splits" / "dataset_mezcla")
    p.add_argument("--salida", type=Path, required=True)
    p.add_argument("--alfa", type=float, default=0.7, help="peso de la KL frente a la CE (default: 0.7)")
    p.add_argument("--epocas", type=int, default=2)
    p.add_argument("--lr", type=float, default=5e-5)
    p.add_argument("--acumulacion", type=int, default=8, help="ejemplos por paso del optimizador (default: 8)")
    p.add_argument("--max-ejemplos", type=int, default=None, help="limitar train y val (solo para pruebas de humo)")
    a = p.parse_args()

    for ruta in a.maestros + ([a.inicial] if a.inicial else []):
        if not (ruta / "adapter_config.json").exists():
            print(f"ERROR: {ruta} no parece un adaptador (falta adapter_config.json)")
            return 1

    cuda = torch.cuda.is_available()
    tokenizer = AutoTokenizer.from_pretrained(probar_baseline.MODEL_ID)
    base = AutoModelForCausalLM.from_pretrained(
        probar_baseline.MODEL_ID, dtype=torch.bfloat16, device_map="auto" if cuda else "cpu"
    )

    nombres = [f"maestro{i}" for i in range(len(a.maestros))]
    modelo = PeftModel.from_pretrained(base, str(a.maestros[0]), adapter_name=nombres[0])
    for nombre, ruta in zip(nombres[1:], a.maestros[1:]):
        modelo.load_adapter(str(ruta), adapter_name=nombre)
    if a.inicial:
        modelo.load_adapter(str(a.inicial), adapter_name="estudiante", is_trainable=True)
    else:
        cfg = LoraConfig.from_pretrained(str(a.maestros[0]))
        modelo.add_adapter("estudiante", cfg)

    train = DatasetTraduccion(cargar_ejemplos(a.dataset_dir / "train.json", a.max_ejemplos), tokenizer)
    val = DatasetTraduccion(cargar_ejemplos(a.dataset_dir / "val.json", a.max_ejemplos), tokenizer)
    train = [train[i] for i in range(len(train))]
    val = [val[i] for i in range(len(val))]
    print(f"Maestros: {len(a.maestros)} | train: {len(train)} | val: {len(val)} | GPU: {cuda}")

    modelo.set_adapter("estudiante")
    for n, prm in modelo.named_parameters():
        prm.requires_grad = "lora_" in n and ".estudiante." in n
    entrenables = [prm for prm in modelo.parameters() if prm.requires_grad]
    print(f"Parámetros entrenables (solo el estudiante): {sum(x.numel() for x in entrenables):,}")
    opt = torch.optim.AdamW(entrenables, lr=a.lr)

    mejor, a.salida = float("inf"), a.salida
    modelo.eval()  # sin dropout: la señal de los maestros debe ser determinista
    for epoca in range(1, a.epocas + 1):
        acum_kl = acum_ce = 0.0
        opt.zero_grad()
        for i, ej in enumerate(train, 1):
            perdida, kl, ce = perdidas(modelo, ej["input_ids"], ej["attention_mask"], ej["labels"], nombres, a.alfa)
            (perdida / a.acumulacion).backward()
            acum_kl += kl
            acum_ce += ce
            if i % a.acumulacion == 0 or i == len(train):
                opt.step()
                opt.zero_grad()
        ce_val = ce_validacion(modelo, val, nombres)
        print(f"Época {epoca}: KL train {acum_kl / len(train):.4f} | CE train {acum_ce / len(train):.4f} | CE validación {ce_val:.4f}")
        if ce_val < mejor:
            mejor = ce_val
            a.salida.mkdir(parents=True, exist_ok=True)
            modelo.save_pretrained(str(a.salida), selected_adapters=["estudiante"])
            print(f"  -> mejor hasta ahora, guardado en {a.salida / 'estudiante'}")

    print(f"Listo. Mejor CE de validación: {mejor:.4f}. Adaptador en {a.salida / 'estudiante'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
