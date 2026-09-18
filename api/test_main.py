"""
api/test_main.py

Prueba la capa de API (validación de entrada, códigos de estado, forma
de la respuesta) sin cargar el modelo real de 3B -- requiere
`SKIP_MODEL_LOAD=1` en el entorno (ver docstring de `api/main.py`).

Uso:
    SKIP_MODEL_LOAD=1 python -m pytest api/test_main.py -v
"""

import os

os.environ["SKIP_MODEL_LOAD"] = "1"

from fastapi.testclient import TestClient  # noqa: E402

import api.main as api_main  # noqa: E402


def test_salud_responde_ok():
    with TestClient(api_main.app) as client:
        r = client.get("/salud")
    assert r.status_code == 200
    assert r.json() == {"estado": "ok"}


def test_traducir_sin_modelo_cargado_devuelve_503():
    with TestClient(api_main.app) as client:
        r = client.post("/traducir", json={"texto": "Que chimba"})
    assert r.status_code == 503


def test_traducir_con_modelo_mockeado(monkeypatch):
    api_main.MODELO_ESTADO["tokenizer"] = object()
    api_main.MODELO_ESTADO["modelo"] = object()
    monkeypatch.setattr(api_main, "_generar_traduccion", lambda tok, mod, texto: "MOCK TRANSLATION")
    try:
        with TestClient(api_main.app) as client:
            r = client.post("/traducir", json={"texto": "Que chimba", "dialecto": "Andina"})
        assert r.status_code == 200
        assert r.json() == {"traduccion": "MOCK TRANSLATION", "dialecto": "Andina"}
    finally:
        api_main.MODELO_ESTADO["tokenizer"] = None
        api_main.MODELO_ESTADO["modelo"] = None


def test_texto_vacio_es_rechazado():
    api_main.MODELO_ESTADO["tokenizer"] = object()
    api_main.MODELO_ESTADO["modelo"] = object()
    try:
        with TestClient(api_main.app) as client:
            r = client.post("/traducir", json={"texto": ""})
        assert r.status_code in (400, 422)
    finally:
        api_main.MODELO_ESTADO["tokenizer"] = None
        api_main.MODELO_ESTADO["modelo"] = None


def test_texto_solo_espacios_es_rechazado():
    api_main.MODELO_ESTADO["tokenizer"] = object()
    api_main.MODELO_ESTADO["modelo"] = object()
    try:
        with TestClient(api_main.app) as client:
            r = client.post("/traducir", json={"texto": "   "})
        assert r.status_code == 400
    finally:
        api_main.MODELO_ESTADO["tokenizer"] = None
        api_main.MODELO_ESTADO["modelo"] = None


def test_texto_demasiado_largo_es_rechazado():
    with TestClient(api_main.app) as client:
        r = client.post("/traducir", json={"texto": "a" * 501})
    assert r.status_code == 422


def test_falta_el_campo_texto_es_rechazado():
    with TestClient(api_main.app) as client:
        r = client.post("/traducir", json={})
    assert r.status_code == 422
