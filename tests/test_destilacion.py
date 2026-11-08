"""
tests/test_destilacion.py

Verifica la lógica de merging/destilacion_multimaestro.py con un modelo
DIMINUTO de pesos aleatorios (el modelo real de 3B no es práctico en CPU):
mismo código `perdidas`, mismo mecanismo de varios adaptadores PEFT.

Qué confirma:
  - la pérdida (KL contra el promedio de maestros + CE) es finita;
  - el backward da gradiente SOLO a los parámetros del estudiante;
  - los maestros no cambian tras un paso del optimizador;
  - el estudiante sí cambia (la señal de destilación llega).

    python -m pytest tests/test_destilacion.py -v
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "merging"))
sys.path.insert(0, str(RAIZ / "finetuning"))

import pytest  # noqa: E402
import torch  # noqa: E402
from peft import LoraConfig, get_peft_model  # noqa: E402
from transformers import Qwen2Config, Qwen2ForCausalLM  # noqa: E402

from destilacion_multimaestro import perdidas  # noqa: E402


def _modelo_con_adaptadores():
    torch.manual_seed(0)
    cfg = Qwen2Config(vocab_size=64, hidden_size=32, intermediate_size=64, num_hidden_layers=2,
                      num_attention_heads=4, num_key_value_heads=2, max_position_embeddings=64)
    base = Qwen2ForCausalLM(cfg)
    lora = LoraConfig(r=4, lora_alpha=8, target_modules=["q_proj", "v_proj"], init_lora_weights=False)
    modelo = get_peft_model(base, lora, adapter_name="maestro0")
    modelo.add_adapter("maestro1", lora)
    modelo.add_adapter("estudiante", lora)
    return modelo


def _ejemplo():
    ids = torch.randint(0, 64, (12,))
    etiquetas = ids.clone()
    etiquetas[:6] = -100  # prompt enmascarado, igual que DatasetTraduccion
    return ids, torch.ones(12, dtype=torch.long), etiquetas


def _snapshot(modelo, nombre):
    return {n: p.detach().clone() for n, p in modelo.named_parameters() if f".{nombre}." in n}


def test_solo_el_estudiante_recibe_gradiente_y_cambia():
    modelo = _modelo_con_adaptadores()
    modelo.eval()
    antes_est = _snapshot(modelo, "estudiante")
    antes_m0 = _snapshot(modelo, "maestro0")

    ids, mask, et = _ejemplo()
    perdida, kl, ce = perdidas(modelo, ids, mask, et, ["maestro0", "maestro1"], alfa=0.7)
    assert torch.isfinite(perdida) and kl >= 0 and ce > 0
    perdida.backward()

    con_grad = {n for n, p in modelo.named_parameters() if p.grad is not None and p.grad.abs().sum() > 0}
    assert con_grad, "ningún parámetro recibió gradiente"
    assert all(".estudiante." in n for n in con_grad), f"gradiente fuera del estudiante: {[n for n in con_grad if '.estudiante.' not in n]}"

    opt = torch.optim.AdamW([p for p in modelo.parameters() if p.requires_grad], lr=1e-2)
    opt.step()
    despues_est = _snapshot(modelo, "estudiante")
    despues_m0 = _snapshot(modelo, "maestro0")
    assert any(not torch.equal(antes_est[n], despues_est[n]) for n in antes_est), "el estudiante no cambió"
    assert all(torch.equal(antes_m0[n], despues_m0[n]) for n in antes_m0), "un maestro cambió (debería estar congelado)"


def test_con_alfa_uno_la_perdida_es_solo_la_kl():
    modelo = _modelo_con_adaptadores()
    modelo.eval()
    ids, mask, et = _ejemplo()
    perdida, kl, _ = perdidas(modelo, ids, mask, et, ["maestro0", "maestro1"], alfa=1.0)
    assert perdida.item() == pytest.approx(kl, rel=1e-5)
