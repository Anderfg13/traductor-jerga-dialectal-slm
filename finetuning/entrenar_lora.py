"""
finetuning/entrenar_lora.py

Pipeline de fine-tuning con LoRA para un generador sintético: carga de
datos -> tokenización -> entrenamiento -> guardado del adaptador ->
recarga del adaptador desde disco -> inferencia. Tiene DOS modos,
mismo código, mismo formato de datos:

  - **Prueba de humo (default)**: subconjunto pequeño (50 ejemplos) y
    pocas épocas (3), sin validación. El objetivo NO es un modelo
    bueno — es confirmar que las piezas del pipeline encajan de punta
    a punta y que la pérdida baja de forma consistente. Resultados
    reales de esta corrida (Generador 1): `finetuning/lora_prueba/`
    (Sesión 14).
  - **Entrenamiento completo (`--todos`)**: TODOS los ejemplos de
    `train.json`, con validación sobre `val.json` en cada época y
    selección del MEJOR checkpoint (no el último) vía
    `load_best_model_at_end` + `EarlyStoppingCallback` — si la pérdida
    de validación deja de mejorar durante `--patience` épocas seguidas
    mientras la de entrenamiento sigue bajando (sobreajuste), el
    entrenamiento se detiene ahí y se guarda el mejor punto, no el
    último. Resultados de esta corrida (Generador 1):
    `finetuning/checkpoints/generador1/` (Sesión 19).

Por default corre sobre `generation/splits/dataset_generador1/`,
configurable con `--dataset-dir` para reutilizar el mismo script con
los Generadores 2 y 3 en la Semana 7 (Sesión 15).

Historia: este script no existía en el repo (Paula no lo había dejado
listo); se escribió en la Sesión 14 para no bloquear la prueba
end-to-end, se completó en la Sesión 15 con la justificación de
hiperparámetros y `--dataset-dir`, se le agregó truncamiento en la
Sesión 17, y se le agregó el modo de entrenamiento completo con
validación en la Sesión 19 (ver BITACORA.md para el detalle de cada
sesión). Se extendió el mismo archivo en vez de crear uno nuevo en
cada caso — decisión explícita del equipo desde la Sesión 15 para no
duplicar un pipeline ya probado.

Modelo base: el mismo candidato usado en la línea base zero-shot
(`finetuning/probar_baseline.py`) — **Qwen2.5-3B-Instruct**, NO Llama
3.2 3B (candidato principal, aún bloqueado por acceso "gated=manual"
de Meta — ver BITACORA.md Sesión 13). Cuando se apruebe el acceso a
Llama, correr este mismo script cambiando `MODEL_ID` (importado de
`probar_baseline.py`) reproduce lo mismo con el candidato principal.

Configuración de LoRA (`r=8`, `alpha=16`, `dropout=0.05`, `bias="none"`,
proyecciones de atención Q/K/V/O): validada y justificada línea por
línea en el código de `entrenar()` desde la Sesión 15-16 — no cambia
entre el modo de prueba de humo y el de entrenamiento completo, sigue
siendo la misma configuración validada.

Formato de entrenamiento: cada ejemplo usa el MISMO prompt de sistema
que la evaluación zero-shot (`probar_baseline.SYSTEM_PROMPT`) — mismo
formato en entrenamiento y en evaluación, para que el LoRA aprenda
exactamente la tarea que se mide después. La pérdida solo se calcula
sobre los tokens de la respuesta del asistente (los del prompt quedan
enmascarados con `label=-100`), para no premiar al modelo por
"aprender a copiar" el prompt. Detalle completo, con ejemplo real de
antes/después de tokenizar, en `finetuning/formato_instruccion.md`
(Sesión 17).

Precisión / cómputo — bfloat16 sin cuantizar, GPU si hay disponible:
  **Correr esto en CPU pura NO es viable** — se probó en la máquina
  local de desarrollo (sin GPU CUDA) y un solo paso de entrenamiento
  tardaba 80-95 minutos; a las 10 horas de correr solo se había
  completado el 5% (8 de 150 pasos) y se abandonó. Este script debe
  correrse en un entorno con GPU — **Google Colab (gratis, T4/L4)**,
  política fija del proyecto para cómputo pesado (ver
  `CONTEXTO_PROYECTO.md`, sección "CÓMPUTO PESADO", y
  `finetuning/entrenar_lora_colab.ipynb`). El modelo se carga vía
  `cargar_modelo()` (importado de `probar_baseline.py`), que ya
  detecta el dispositivo automáticamente (`device_map="auto"` si hay
  CUDA, si no `"cpu"`) y no cuantiza en ningún caso: un 3B en bfloat16
  pesa ~6-6.5GB, que cabe cómodo tanto en la VRAM libre de una GPU
  gratuita de Colab (~15GB) como en los 18GB de RAM de la máquina
  local — cuantizar no habría resuelto el problema real, que era la
  falta de GPU, no de memoria. LoRA además ya reduce el costo de
  memoria de entrenamiento de por sí, porque los pesos base quedan
  congelados: solo se entrenan los adaptadores (unos pocos millones de
  parámetros, no los 3B completos).

Uso (recomendado, en Google Colab):
    Abrir finetuning/entrenar_lora_colab.ipynb en Colab, activar GPU
    (Entorno de ejecución > Cambiar tipo de entorno > GPU) y correr
    las celdas en orden (Parte A = prueba de humo, Parte B =
    entrenamiento completo).

Uso (local, solo si hay GPU CUDA disponible; en CPU pura NO
terminará en un tiempo razonable, ver arriba):
    python finetuning/entrenar_lora.py                     # prueba de humo
    python finetuning/entrenar_lora.py --todos              # entrenamiento completo, con validación
    python finetuning/entrenar_lora.py --dataset-dir generation/splits/dataset_generador2

Salidas — prueba de humo (Generador 1, default):
    finetuning/lora_prueba/adapter/              adaptador LoRA entrenado
    finetuning/lora_prueba/loss_log.json         pérdida por paso, cruda
    finetuning/lora_prueba/salidas_con_adapter.json  traducciones de prueba
        con el adaptador recargado desde disco, sobre los MISMOS 8
        ejemplos de test.json que usa probar_baseline.py — permite
        comparar directamente "antes" (sin ajustar) vs. "después"
        (con LoRA) sobre exactamente los mismos ejemplos.
Con --dataset-dir apuntando a otro generador, las mismas tres salidas
se guardan en finetuning/lora_prueba_<generadorN>/ en vez de
finetuning/lora_prueba/, para no pisar los resultados de otro dataset.

Salidas — entrenamiento completo (`--todos`, Generador 1, default):
    finetuning/checkpoints/generador1/adapter/   adaptador LoRA FINAL
        (el MEJOR checkpoint según pérdida de validación, no
        necesariamente el de la última época)
    finetuning/checkpoints/generador1/loss_log.json  pérdida de
        entrenamiento (por paso) y de validación (por época), crudas
    finetuning/checkpoints/generador1/salidas_con_adapter.json  mismas
        8 traducciones de prueba que en el modo de prueba de humo, con
        el checkpoint final
Los checkpoints INTERMEDIOS del Trainer (uno por época, con estado del
optimizador — pesan mucho más que el adaptador final y no aportan nada
una vez que se sabe cuál fue el mejor) se guardan en un directorio
temporal FUERA del repo (`tempfile.mkdtemp()`), nunca en
finetuning/checkpoints/ — solo el adaptador final ya elegido se trae de
vuelta al repo.
"""

import argparse
import gc
import json
import random
import sys
import tempfile
from pathlib import Path

import torch
from peft import LoraConfig, PeftModel, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    EarlyStoppingCallback,
    Trainer,
    TrainerCallback,
    TrainingArguments,
    default_data_collator,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from probar_baseline import INDICES_MUESTRA, MODEL_ID, SYSTEM_PROMPT, TEST_PATH, cargar_modelo, traducir  # noqa: E402

SPLITS_DIR_DEFAULT = Path(__file__).resolve().parent.parent / "generation" / "splits" / "dataset_generador1"
FINETUNING_DIR = Path(__file__).resolve().parent

N_EJEMPLOS_PRUEBA = 50  # prueba de humo: subconjunto pequeño, límite inferior del rango 50-100 pedido
EPOCAS_PRUEBA = 3
# Entrenamiento completo: límite SUPERIOR generoso, no la cantidad real
# de épocas que se espera correr — con --todos, load_best_model_at_end
# + EarlyStoppingCallback cortan antes si la pérdida de validación deja
# de mejorar, así que este número solo importa si el modelo NUNCA
# sobreajusta (caso optimista); no hace falta adivinar el número
# "correcto" de antemano.
EPOCAS_COMPLETO_MAX = 10
PATIENCE_DEFAULT = 2  # épocas sin mejora en pérdida de validación antes de detener (solo con --todos)
SEMILLA_ALEATORIA = 42  # misma semilla que generation/split_dataset.py, por consistencia
MAX_LENGTH = 512  # margen amplio: la secuencia más larga observada en el
# dataset actual (generation/splits/dataset_generador1/) son 125 tokens,
# muy por debajo de esto. Este límite no se activa hoy con estos datos —
# existe como red de seguridad para no reventar la memoria de la GPU si
# en el futuro entra un ejemplo inusualmente largo (otro generador,
# variantes más elaboradas), en vez de fallar sin control (Sesión 17).


def cargar_ejemplos(path: Path, n_ejemplos: int | None) -> list[dict]:
    """n_ejemplos=None -> todos los ejemplos del archivo (mezclados, no
    en el orden en que están guardados). Con un número, solo los
    primeros n tras mezclar (prueba de humo)."""
    datos = json.loads(path.read_text(encoding="utf-8"))
    random.Random(SEMILLA_ALEATORIA).shuffle(datos)
    if n_ejemplos is not None:
        datos = datos[:n_ejemplos]
    return datos


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
        n_prompt = len(ids_prompt)

        # Truncamiento: si la secuencia completa supera MAX_LENGTH, se
        # recorta desde la IZQUIERDA (el inicio del prompt), nunca desde
        # la derecha -- cortar por la derecha eliminaría parte de la
        # traducción de referencia, que es justo lo que el modelo tiene
        # que aprender a generar. Recortar el inicio del prompt es más
        # seguro: en el peor caso se pierde parte del SYSTEM_PROMPT fijo,
        # no la señal de entrenamiento.
        if len(ids_completos) > MAX_LENGTH:
            exceso = len(ids_completos) - MAX_LENGTH
            ids_completos = ids_completos[exceso:]
            n_prompt = max(0, n_prompt - exceso)

        etiquetas = list(ids_completos)
        n_prompt = min(n_prompt, len(etiquetas))
        for i in range(n_prompt):
            etiquetas[i] = -100

        return {
            "input_ids": torch.tensor(ids_completos, dtype=torch.long),
            "attention_mask": torch.ones(len(ids_completos), dtype=torch.long),
            "labels": torch.tensor(etiquetas, dtype=torch.long),
        }


class RegistrarPerdida(TrainerCallback):
    def __init__(self):
        self.historial_train = []
        self.historial_eval = []

    def on_log(self, args, state, control, logs=None, **kwargs):
        if not logs:
            return
        if "loss" in logs:
            self.historial_train.append(
                {"paso": state.global_step, "epoca": round(state.epoch, 3), "loss": logs["loss"]}
            )
        if "eval_loss" in logs:
            self.historial_eval.append(
                {"paso": state.global_step, "epoca": round(state.epoch, 3), "eval_loss": logs["eval_loss"]}
            )


def entrenar(
    train_path: Path,
    val_path: Path | None,
    adapter_dir: Path,
    loss_log_path: Path,
    trainer_output_dir: Path,
    n_ejemplos: int | None,
    epocas: int,
    patience: int,
) -> RegistrarPerdida:
    dispositivo = "GPU (CUDA)" if torch.cuda.is_available() else "CPU"
    print(f"Cargando {MODEL_ID} en bfloat16 (sin cuantizar) para entrenar, dispositivo: {dispositivo}...")
    tokenizer, modelo_base = cargar_modelo()

    lora_config = LoraConfig(
        # Rango del adaptador (r): controla cuántos parámetros nuevos se
        # entrenan. 8 es un punto de partida modesto y muy usado para
        # modelos ~3B — suficiente para que el adaptador aprenda el patrón
        # de traducción dialectal sin sobreajustar con un dataset chico
        # (50-100 ejemplos en esta prueba de humo), y mantiene el adaptador
        # en pocos MB, alineado con el objetivo de portabilidad del
        # proyecto (CONTEXTO_PROYECTO.md).
        r=8,
        # alpha = 2*r es la heurística estándar de la literatura de LoRA:
        # mantiene la magnitud efectiva de la actualización estable aunque
        # se cambie r más adelante (ej. si se sube a r=16 al escalar en la
        # Sesión 19+, alpha subiría a 32 con el mismo criterio).
        lora_alpha=16,
        # Dropout leve sobre las activaciones del adaptador: regularización
        # barata contra sobreajuste dado lo pequeño del dataset de esta
        # prueba — ya se observó un indicio de sobreajuste (dos ejemplos
        # distintos con la misma salida, ver BITACORA.md Sesión 14) con
        # este mismo valor, así que no conviene bajarlo más; tampoco se
        # sube porque con solo 3 épocas ya es un entrenamiento corto.
        lora_dropout=0.05,
        # No adaptar los términos de bias: es el default estándar de LoRA
        # para LLMs causales — los bias de atención rara vez aportan valor
        # al adaptarlos y hacerlo agregaría parámetros sin beneficio claro
        # para esta tarea.
        bias="none",
        task_type="CAUSAL_LM",
        # Proyecciones de atención (Q/K/V/O): es donde más impacto tiene
        # adaptar un modelo para una tarea nueva de comprensión de entrada
        # (interpretar jerga/dialecto), sin tocar las capas MLP — mantiene
        # el adaptador más chico y el entrenamiento más rápido, en línea
        # con el objetivo de eficiencia del proyecto.
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )
    modelo = get_peft_model(modelo_base, lora_config)
    modelo.print_trainable_parameters()

    muestra_train = cargar_ejemplos(train_path, n_ejemplos)
    dataset_train = DatasetTraduccion(muestra_train, tokenizer)

    dataset_val = None
    if val_path is not None:
        muestra_val = cargar_ejemplos(val_path, None)  # validación: siempre completa, nunca una muestra
        dataset_val = DatasetTraduccion(muestra_val, tokenizer)
        print(
            f"Entrenando sobre {len(muestra_train)} ejemplos de {train_path}, "
            f"validando sobre {len(muestra_val)} ejemplos de {val_path}, {epocas} épocas máx "
            f"(patience={patience})..."
        )
    else:
        print(f"Entrenando sobre {len(muestra_train)} ejemplos de {train_path}, {epocas} épocas, sin validación...")

    validando = dataset_val is not None
    registrador = RegistrarPerdida()

    kwargs_entrenamiento = dict(
        output_dir=str(trainer_output_dir),
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        num_train_epochs=epocas,
        learning_rate=2e-4,
        logging_steps=1,
        report_to=[],
        remove_unused_columns=False,
    )
    if validando:
        kwargs_entrenamiento.update(
            eval_strategy="epoch",
            # save_strategy tiene que coincidir con eval_strategy para
            # que load_best_model_at_end funcione (el Trainer compara
            # los checkpoints guardados en cada punto de evaluación).
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            # Solo conservar 2 checkpoints intermedios (el mejor hasta
            # ahora + el más reciente) -- son varios GB con el estado
            # del optimizador si no se limita, y de todos modos no
            # viven en el repo (ver trainer_output_dir en main()).
            save_total_limit=2,
        )
    else:
        kwargs_entrenamiento.update(eval_strategy="no", save_strategy="no")

    args_entrenamiento = TrainingArguments(**kwargs_entrenamiento)

    callbacks = [registrador]
    if validando:
        # Detiene el entrenamiento si la pérdida de VALIDACIÓN no mejora
        # durante `patience` épocas seguidas -- exactamente la señal de
        # sobreajuste pedida (entrenamiento sigue bajando, validación ya
        # no). Junto con load_best_model_at_end=True de arriba,
        # trainer.train() deja cargado el MEJOR checkpoint al terminar,
        # no el último -- no hace falta elegirlo a mano después.
        callbacks.append(EarlyStoppingCallback(early_stopping_patience=patience))

    trainer = Trainer(
        model=modelo,
        args=args_entrenamiento,
        train_dataset=dataset_train,
        eval_dataset=dataset_val,
        data_collator=default_data_collator,
        callbacks=callbacks,
    )
    trainer.train()

    adapter_dir.mkdir(parents=True, exist_ok=True)
    modelo.save_pretrained(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))
    sufijo_log = " (mejor checkpoint según validación, no necesariamente el último)" if validando else ""
    print(f"Adaptador LoRA guardado en {adapter_dir}{sufijo_log}")

    # Formato del log: si no hubo validación (prueba de humo), se
    # mantiene el formato original -- lista plana de pérdidas de
    # entrenamiento -- exactamente igual al que ya está committeado en
    # finetuning/lora_prueba/loss_log.json (Sesión 14), para no romper
    # nada que ya lo lea. Con validación, se guarda como dict separando
    # train/eval -- es un archivo nuevo en una ruta nueva, no pisa nada.
    contenido_log = (
        {"train": registrador.historial_train, "eval": registrador.historial_eval}
        if registrador.historial_eval
        else registrador.historial_train
    )
    loss_log_path.write_text(json.dumps(contenido_log, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Curva de pérdida guardada en {loss_log_path}")

    # Liberar el modelo de entrenamiento de memoria antes de recargar desde
    # disco — así la prueba de inferencia de abajo usa de verdad el
    # adaptador guardado en disco, no el objeto que quedó en memoria.
    del trainer, modelo, modelo_base
    gc.collect()

    return registrador


def probar_adapter_recargado(adapter_dir: Path, salidas_path: Path):
    print(f"\nRecargando {MODEL_ID} + adaptador LoRA desde disco ({adapter_dir})...")
    tokenizer, modelo_base = cargar_modelo()
    modelo_ajustado = PeftModel.from_pretrained(modelo_base, str(adapter_dir))
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

    salidas_path.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nGuardado en {salidas_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=SPLITS_DIR_DEFAULT,
        help=(
            "Carpeta con train.json/val.json del generador a usar (ej. "
            "generation/splits/dataset_generador2), para reutilizar este "
            "mismo script con los Generadores 2 y 3 en la Semana 7. "
            f"Default: {SPLITS_DIR_DEFAULT}"
        ),
    )
    parser.add_argument(
        "--todos",
        action="store_true",
        help=(
            "Entrenamiento completo: TODOS los ejemplos de train.json, con "
            "validación sobre val.json y selección del mejor checkpoint "
            "(EarlyStoppingCallback). Sin esta bandera: prueba de humo "
            f"({N_EJEMPLOS_PRUEBA} ejemplos, sin validación)."
        ),
    )
    parser.add_argument(
        "--epocas",
        type=int,
        default=None,
        help=f"Épocas (default: {EPOCAS_PRUEBA} en prueba de humo, límite superior {EPOCAS_COMPLETO_MAX} con --todos)",
    )
    parser.add_argument(
        "--patience",
        type=int,
        default=PATIENCE_DEFAULT,
        help=f"Épocas sin mejora en pérdida de validación antes de detener, solo con --todos (default: {PATIENCE_DEFAULT})",
    )
    args = parser.parse_args()

    train_path = args.dataset_dir / "train.json"
    if not train_path.exists():
        print(f"ERROR: no existe {train_path}")
        return 1

    sufijo = "generador1" if args.dataset_dir == SPLITS_DIR_DEFAULT else args.dataset_dir.name.removeprefix("dataset_")

    if args.todos:
        val_path = args.dataset_dir / "val.json"
        if not val_path.exists():
            print(f"ERROR: no existe {val_path} (--todos necesita validación sobre val.json)")
            return 1
        n_ejemplos = None
        epocas = args.epocas or EPOCAS_COMPLETO_MAX
        out_dir = FINETUNING_DIR / "checkpoints" / sufijo
        # Los checkpoints INTERMEDIOS del Trainer (uno por época, con
        # estado del optimizador) nunca van dentro del repo -- pesan
        # mucho más que el adaptador final y no aportan nada una vez
        # elegido el mejor (ver docstring del módulo).
        trainer_output_dir = Path(tempfile.mkdtemp(prefix="entrenar_lora_trainer_"))
    else:
        val_path = None
        n_ejemplos = N_EJEMPLOS_PRUEBA
        epocas = args.epocas or EPOCAS_PRUEBA
        # Con el dataset por default (Generador 1) la salida va en
        # "lora_prueba" (la carpeta que ya existe en el repo desde la Sesión
        # 14, con resultados reales ya committeados). Para cualquier otro
        # generador (Semana 7+), la salida va en una carpeta con su propio
        # nombre (ej. lora_prueba_generador2) para no sobrescribir resultados
        # de una corrida anterior con otro dataset.
        if args.dataset_dir == SPLITS_DIR_DEFAULT:
            out_dir = FINETUNING_DIR / "lora_prueba"
        else:
            out_dir = FINETUNING_DIR / f"lora_prueba_{sufijo}"
        trainer_output_dir = out_dir / "checkpoints"

    adapter_dir = out_dir / "adapter"
    loss_log_path = out_dir / "loss_log.json"
    salidas_path = out_dir / "salidas_con_adapter.json"

    registrador = entrenar(
        train_path, val_path, adapter_dir, loss_log_path, trainer_output_dir, n_ejemplos, epocas, args.patience
    )
    if not registrador.historial_train:
        print("ERROR: no se registró ninguna pérdida de entrenamiento.")
        return 1
    probar_adapter_recargado(adapter_dir, salidas_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
