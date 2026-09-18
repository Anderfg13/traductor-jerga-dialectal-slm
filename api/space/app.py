"""
api/space/app.py

Servicio de traducción desplegado en **Hugging Face Spaces** (SDK
Gradio + hardware **ZeroGPU**) — versión de despliegue del mismo
servicio de `api/main.py` (FastAPI), reescrita como Gradio porque:

  - Hospedar un Space con SDK Docker (lo que necesitaría FastAPI tal
    cual) pasó a requerir un plan PRO de pago en 2026 (cambio de
    política de Hugging Face).
  - Los Spaces de Gradio con hardware ZeroGPU SÍ son gratis para
    cuentas personales (hasta 2 Spaces), y corren en GPU real por los
    segundos exactos que dura cada generación — sin costo. De paso
    resuelve la latencia de 50-80s por solicitud que se midió en CPU
    local (`BITACORA.md`, Sesión 25): en GPU debería bajar a pocos
    segundos.

Reutiliza la MISMA lógica de traducción que
`finetuning/probar_baseline.py` y `api/main.py` — mismo
`SYSTEM_PROMPT`, mismo formato de prompt (`apply_chat_template`,
system+user, `add_generation_prompt=True`, `max_new_tokens=80`,
`do_sample=False`). No se reinventa el prompt aquí.

Requisito técnico de ZeroGPU (ver documentación oficial de HF): el
modelo se tiene que cargar a nivel de MÓDULO (no dentro de una
función) — fuera de una función decorada con `@spaces.GPU`, CUDA corre
en modo emulado (sin GPU real todavía asignada), así que
`.to("cuda")` a nivel de módulo es seguro aunque no haya GPU real en
ese instante. Solo la función que genera texto lleva el decorador
`@spaces.GPU`, que le pide a Hugging Face una GPU real por los
segundos que dura la llamada y la libera al terminar.

El adaptador LoRA (`api/space/adapter/`) es una COPIA de
`finetuning/checkpoints/generador1/adapter/` (Sesión 19) — duplicada
a propósito (son ~15MB, no vale la pena complicar el despliegue con
rutas cruzadas) para que este directorio sea autocontenido: es
exactamente lo que se sube al repositorio del Space en Hugging Face,
sin arrastrar el resto del proyecto.

Uso local (sin GPU real ni ZeroGPU — para probar que la app arranca
antes de subirla; `@spaces.GPU` no hace nada fuera de un Space real,
así que corre en CPU, lento pero funcional, igual que `api/main.py`):
    pip install gradio spaces torch transformers peft
    python api/space/app.py

Despliegue real: ver `docs/despliegue.md` para el paso a paso completo
(crear el Space, subir estos archivos, configurar el hardware).
"""

from pathlib import Path

import gradio as gr
import spaces
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"
ADAPTER_DIR = Path(__file__).resolve().parent / "adapter"

SYSTEM_PROMPT = (
    "Traduce del español al inglés la frase que te dé el usuario. "
    "Responde ÚNICAMENTE con la traducción al inglés, sin explicaciones "
    "ni texto adicional."
)

print(f"Cargando {MODEL_ID} + adaptador desde {ADAPTER_DIR}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
modelo_base = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.bfloat16)
modelo = PeftModel.from_pretrained(modelo_base, str(ADAPTER_DIR))
modelo.to("cuda" if torch.cuda.is_available() else "cpu")
modelo.eval()
print("Modelo listo.")


@spaces.GPU(duration=30)  # tope generoso; una traducción real tarda pocos segundos en GPU
def _generar(texto: str) -> str:
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
    texto_generado = tokenizer.decode(salida[0][entrada["input_ids"].shape[1] :], skip_special_tokens=True)
    return texto_generado.strip()


def traducir(texto: str, dialecto: str = ""):
    texto = (texto or "").strip()
    if not texto:
        raise gr.Error("El texto no puede estar vacío.")
    if len(texto) > 500:
        raise gr.Error("El texto no puede superar 500 caracteres.")
    return _generar(texto)


def salud():
    return "ok"


with gr.Blocks(title="Traductor de jerga/dialectos del español") as demo:
    gr.Markdown(
        "# Traductor de jerga y dialectos del español → inglés\n"
        "Modelo: Qwen2.5-3B-Instruct + adaptador LoRA (Generador 1, Sesión 19)."
    )
    with gr.Row():
        texto_in = gr.Textbox(label="Texto en español", placeholder="Ej: ¡Que chimba, parcero!")
        dialecto_in = gr.Textbox(label="Dialecto (opcional, informativo)", placeholder="Ej: Andina")
    salida_out = gr.Textbox(label="Traducción")
    boton = gr.Button("Traducir")
    boton.click(fn=traducir, inputs=[texto_in, dialecto_in], outputs=salida_out, api_name="traducir")

    # Botón oculto solo para exponer un endpoint de salud vía la API de
    # Gradio (equivalente a GET /salud en api/main.py) -- no hace falta
    # que sea visible en la interfaz humana.
    salud_out = gr.Textbox(visible=False)
    salud_btn = gr.Button(visible=False)
    salud_btn.click(fn=salud, inputs=None, outputs=salud_out, api_name="salud")

if __name__ == "__main__":
    demo.launch()
