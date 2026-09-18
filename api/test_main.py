"""
api/test_main.py

Prueba la capa de API (validación de entrada, rate limiting, métricas
agregadas, códigos de estado, forma de la respuesta) sin cargar el
modelo real de 3B -- requiere `SKIP_MODEL_LOAD=1` en el entorno (ver
docstring de `api/main.py`).

Uso:
    SKIP_MODEL_LOAD=1 python -m pytest api/test_main.py -v
"""

import os

os.environ["SKIP_MODEL_LOAD"] = "1"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import api.main as api_main  # noqa: E402


@pytest.fixture(autouse=True)
def _rate_limit_y_metricas_aisladas():
    """Cada prueba parte de cero -- sin esto, pruebas que llaman a
    /traducir varias veces se contaminarían entre sí (todas comparten
    la misma IP de TestClient) y una prueba podría fallar por el
    límite de tasa que dejó otra prueba anterior."""
    api_main._rate_limit_historial.clear()
    for clave in api_main.METRICAS:
        api_main.METRICAS[clave] = 0
    yield
    api_main._rate_limit_historial.clear()
    for clave in api_main.METRICAS:
        api_main.METRICAS[clave] = 0


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
        assert "detail" in r.json()  # mensaje entendible, no un stack trace
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
        assert "vacío" in r.json()["detail"]
    finally:
        api_main.MODELO_ESTADO["tokenizer"] = None
        api_main.MODELO_ESTADO["modelo"] = None


def test_texto_demasiado_largo_es_rechazado():
    with TestClient(api_main.app) as client:
        r = client.post("/traducir", json={"texto": "a" * 501})
    assert r.status_code == 422
    assert "detail" in r.json()


def test_falta_el_campo_texto_es_rechazado():
    with TestClient(api_main.app) as client:
        r = client.post("/traducir", json={})
    assert r.status_code == 422


def test_rate_limit_devuelve_429_tras_exceder_el_limite(monkeypatch):
    """Manda más solicitudes que el límite permitido, en poco tiempo, y
    confirma que las que exceden el límite responden 429 con un
    mensaje claro y un header Retry-After -- prueba de aceptación
    pedida explícitamente."""
    api_main.MODELO_ESTADO["tokenizer"] = object()
    api_main.MODELO_ESTADO["modelo"] = object()
    monkeypatch.setattr(api_main, "_generar_traduccion", lambda tok, mod, texto: "MOCK")
    try:
        with TestClient(api_main.app) as client:
            respuestas = [
                client.post("/traducir", json={"texto": "hola"})
                for _ in range(api_main.RATE_LIMIT_MAX_SOLICITUDES + 3)
            ]

        codigos = [r.status_code for r in respuestas]
        permitidas = codigos[: api_main.RATE_LIMIT_MAX_SOLICITUDES]
        exceso = respuestas[api_main.RATE_LIMIT_MAX_SOLICITUDES :]

        assert permitidas == [200] * api_main.RATE_LIMIT_MAX_SOLICITUDES
        assert all(r.status_code == 429 for r in exceso)
        assert all("Retry-After" in r.headers for r in exceso)
        assert all("detail" in r.json() for r in exceso)  # mensaje entendible, no un stack trace
    finally:
        api_main.MODELO_ESTADO["tokenizer"] = None
        api_main.MODELO_ESTADO["modelo"] = None


def test_rate_limit_no_aplica_a_salud_ni_metricas():
    """/salud y /metricas son operaciones baratas (no tocan el modelo)
    y no deben limitarse -- se pueden llamar más veces que el límite
    de /traducir sin problema."""
    with TestClient(api_main.app) as client:
        for _ in range(api_main.RATE_LIMIT_MAX_SOLICITUDES + 5):
            assert client.get("/salud").status_code == 200
            assert client.get("/metricas").status_code == 200


def test_metricas_solo_expone_contadores_agregados(monkeypatch):
    """Confirma en la práctica (no solo en un comentario) que /metricas
    nunca devuelve el texto de ninguna solicitud -- solo los 4
    contadores agregados documentados."""
    api_main.MODELO_ESTADO["tokenizer"] = object()
    api_main.MODELO_ESTADO["modelo"] = object()
    monkeypatch.setattr(api_main, "_generar_traduccion", lambda tok, mod, texto: "traduccion secreta de prueba")
    texto_enviado = "este texto nunca debe aparecer en /metricas"
    try:
        with TestClient(api_main.app) as client:
            client.post("/traducir", json={"texto": texto_enviado})
            r = client.get("/metricas")

        assert r.status_code == 200
        cuerpo = r.json()
        assert set(cuerpo.keys()) == {
            "total_solicitudes",
            "traducciones_exitosas",
            "rechazadas_validacion",
            "rechazadas_rate_limit",
        }
        assert cuerpo["total_solicitudes"] == 1
        assert cuerpo["traducciones_exitosas"] == 1
        assert texto_enviado not in r.text
        assert "traduccion secreta de prueba" not in r.text
    finally:
        api_main.MODELO_ESTADO["tokenizer"] = None
        api_main.MODELO_ESTADO["modelo"] = None


def test_error_no_previsto_no_expone_traceback(monkeypatch):
    """Si algo interno falla de forma inesperada, la respuesta sigue
    siendo un JSON entendible con código 500 -- nunca un traceback
    crudo expuesto al cliente."""
    api_main.MODELO_ESTADO["tokenizer"] = object()
    api_main.MODELO_ESTADO["modelo"] = object()

    def _reventar(tok, mod, texto):
        raise RuntimeError("fallo interno simulado, con detalles que no deberían salir al cliente")

    monkeypatch.setattr(api_main, "_generar_traduccion", _reventar)
    try:
        with TestClient(api_main.app, raise_server_exceptions=False) as client:
            r = client.post("/traducir", json={"texto": "hola"})
        assert r.status_code == 500
        cuerpo = r.json()
        assert "detail" in cuerpo
        assert "fallo interno simulado" not in r.text
        assert "Traceback" not in r.text
    finally:
        api_main.MODELO_ESTADO["tokenizer"] = None
        api_main.MODELO_ESTADO["modelo"] = None
