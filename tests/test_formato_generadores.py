"""
tests/test_formato_generadores.py

Confirma que los registros que produce generation/generar_sintetico.py
tienen la MISMA estructura (mismos campos, mismos tipos) para los tres
generadores, y que todos recibieron el MISMO prompt por semilla. Sin
esto, una diferencia entre generadores podría deberse a un artefacto del
formato y no al modelo (PI1).

Se verifica sobre los datos reales de generation/raw/generadorN/ (no con
datos simulados). Compara en dos niveles:
  1. el registro crudo guardado por el script (campos del registro);
  2. la respuesta del modelo ya parseada (campos de cada variante).

    python -m pytest tests/test_formato_generadores.py -v
    python tests/test_formato_generadores.py sem-007 sem-018 sem-006   # tabla legible

Es la prueba de aceptación del Generador 2: las mismas 3 semillas de
prueba del Generador 1 deben dar el mismo formato.
"""

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "generation"))

from consolidar import limpiar_json, reparar_comilla_faltante  # noqa: E402

SEMILLAS_PRUEBA = ["sem-007", "sem-018", "sem-006"]  # las 3 usadas para probar el Generador 1
CAMPOS_REGISTRO = {"seed_id", "generador", "modelo", "timestamp_utc", "prompt", "respuesta_cruda"}
CAMPOS_VARIANTE = {"texto_dialectal", "traduccion", "registro", "contexto_uso"}
NOMBRES = {1: "groq", 2: "cohere", 3: "google"}


def _registro(g, seed_id):
    ruta = RAIZ / "generation" / "raw" / f"generador{g}" / f"{seed_id}.json"
    if not ruta.exists():
        pytest.skip(f"falta {ruta}")
    return json.loads(ruta.read_text(encoding="utf-8"))


def _parsear(registro):
    crudo = limpiar_json(registro["respuesta_cruda"])
    try:
        return json.loads(crudo, strict=False)
    except json.JSONDecodeError:
        return json.loads(reparar_comilla_faltante(crudo), strict=False)


def _tipos(d):
    return {k: type(v).__name__ for k, v in d.items()}


@pytest.mark.parametrize("seed_id", SEMILLAS_PRUEBA)
@pytest.mark.parametrize("g", [2, 3])
def test_registro_crudo_igual_al_del_generador_1(g, seed_id):
    base, otro = _registro(1, seed_id), _registro(g, seed_id)
    assert set(otro) == CAMPOS_REGISTRO, f"campos distintos en generador {g}: {set(otro) ^ CAMPOS_REGISTRO}"
    assert _tipos(otro) == _tipos(base), f"tipos distintos: {_tipos(otro)} vs {_tipos(base)}"
    assert otro["generador"] == NOMBRES[g]
    assert otro["prompt"] == base["prompt"], "el prompt enviado difiere entre generadores"


@pytest.mark.parametrize("seed_id", SEMILLAS_PRUEBA)
@pytest.mark.parametrize("g", [1, 2, 3])
def test_respuesta_parseada_tiene_la_estructura_esperada(g, seed_id):
    salida = _parsear(_registro(g, seed_id))
    assert set(salida) == {"seed_id", "variantes"}
    assert salida["seed_id"] == seed_id
    assert 5 <= len(salida["variantes"]) <= 8, f"{len(salida['variantes'])} variantes (se piden 5 a 8)"
    for v in salida["variantes"]:
        assert set(v) == CAMPOS_VARIANTE, f"campos de variante distintos: {set(v) ^ CAMPOS_VARIANTE}"
        assert all(isinstance(x, str) and x.strip() for x in v.values()), f"valor vacío o no-string: {v}"


@pytest.mark.parametrize("g", [1, 2, 3])
def test_dataset_consolidado_tiene_los_mismos_campos_y_tipos(g):
    """El resultado final de consolidar.py (lo que se entrena) es idéntico
    en estructura para los tres generadores, y ningún campo queda vacío.
    Cubre el caso real de Gemini que escribió {"informal": "informal"} en
    vez de {"registro": "informal"} (2 de 625 variantes)."""
    ruta = RAIZ / "generation" / f"dataset_generador{g}.json"
    if not ruta.exists():
        pytest.skip(f"falta {ruta}")
    dataset = json.loads(ruta.read_text(encoding="utf-8"))
    esperado = {"seed_id", "dialecto_region", "registro_original_semilla", "texto_dialectal", "traduccion",
                "registro", "contexto_uso", "generador", "modelo"}
    for v in dataset:
        assert set(v) == esperado, f"{v['seed_id']}: campos {set(v) ^ esperado}"
        assert all(isinstance(x, str) and x.strip() for x in v.values()), f"{v['seed_id']}: valor vacío o no-string"
    assert {v["generador"] for v in dataset} == {NOMBRES[g]}


def test_mismo_prompt_para_todas_las_semillas_de_los_tres_generadores():
    """Sobre las 100 semillas: el prompt guardado es idéntico entre generadores."""
    base = RAIZ / "generation" / "raw" / "generador1"
    comparadas = 0
    for ruta in sorted(base.glob("*.json")):
        p1 = json.loads(ruta.read_text(encoding="utf-8"))["prompt"]
        for g in (2, 3):
            otra = RAIZ / "generation" / "raw" / f"generador{g}" / ruta.name
            if otra.exists():
                assert json.loads(otra.read_text(encoding="utf-8"))["prompt"] == p1, f"{ruta.name}: prompt distinto en generador {g}"
                comparadas += 1
    assert comparadas > 0


if __name__ == "__main__":
    ids = sys.argv[1:] or SEMILLAS_PRUEBA
    for sid in ids:
        print(f"== {sid}")
        for g in (1, 2, 3):
            r = _registro(g, sid)
            s = _parsear(r)
            v = s["variantes"]
            print(f"  gen{g} {r['modelo']:24} campos_registro={sorted(r)==sorted(CAMPOS_REGISTRO)} "
                  f"variantes={len(v)} campos_variante={sorted(v[0])==sorted(CAMPOS_VARIANTE)} "
                  f"tipos={sorted(set(_tipos(v[0]).values()))}")
