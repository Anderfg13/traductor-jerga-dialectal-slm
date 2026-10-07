"""
tests/test_integracion_e2e.py

Prueba de integración end-to-end (Sesión 31): confirma que las 6
etapas de la cadena completa del servicio están conectadas de punta a
punta, en un solo flujo:

  1. Cliente manda una solicitud a POST /traducir.
  2. Pasa por validación y rate limiting (Sesión 28) sin ser rechazada
     (y la validación SÍ rechaza una entrada inválida: está conectada).
  3. El modelo ajustado genera la traducción.
  4. Se registra la métrica (latencia por dialecto, Sesión 29).
  5. La respuesta llega al cliente con `solicitud_id`.
  6. El endpoint de retroalimentación (POST /retroalimentacion) funciona
     y GET /metricas refleja la solicitud y la retroalimentación.

Dos modos, MISMA lógica (`verificar_cadena`):

  - pytest (en proceso, generación mockeada -- rápido, sin GPU):
        python -m pytest tests/test_integracion_e2e.py -v
  - contra un servicio REAL corriendo (modelo ajustado de verdad):
        python tests/test_integracion_e2e.py --url http://127.0.0.1:8000
    Sale con código 0 si las 6 etapas pasan y 1 si alguna falla,
    nombrando la etapa. No asume estado limpio: compara métricas antes
    y después (el servicio real puede tener tráfico previo).

Cada aserción dice QUÉ etapa se rompió y qué se esperaba, para que un
fallo señale el eslabón exacto y no un error genérico.

Limitación: solo la API FastAPI (`api/main.py`) expone /metricas y
/retroalimentacion. El Space de Hugging Face (`api/space/`) solo tiene
traducir y salud, así que las etapas 4-6 no se pueden verificar ahí.
"""

import argparse
import sys

import httpx

TEXTO = "Que chimba de parche, nos vemos mas tarde bacano"
DIALECTO = "Andina"


class EtapaRota(AssertionError):
    """Una etapa de la cadena falló; el mensaje empieza con 'Etapa N'."""


def _exigir(condicion, etapa, mensaje):
    if not condicion:
        raise EtapaRota(f"[Etapa {etapa} ROTA] {mensaje}")


def _dialecto(metricas, nombre):
    return metricas.get("por_dialecto", {}).get(nombre, {})


def verificar_cadena(client, traduccion_esperada=None, log=print):
    """Corre las 6 etapas con `client` (TestClient o httpx.Client).

    traduccion_esperada: texto exacto esperado (solo con generación
    mockeada); si es None solo se exige una traducción no vacía.
    Devuelve el dict de evidencia por etapa.
    """
    evidencia = {}

    r = client.get("/salud")
    _exigir(r.status_code == 200, "0", f"/salud no responde 200 (servicio caído o URL incorrecta): {r.status_code}")
    antes = client.get("/metricas")
    _exigir(antes.status_code == 200, 4, f"GET /metricas falló ({antes.status_code}): sin métricas no hay etapa 4 ni 6.")
    antes = antes.json()
    base_sol = _dialecto(antes, DIALECTO).get("solicitudes", 0)
    base_fb = _dialecto(antes, DIALECTO).get("retroalimentacion_total", 0)
    base_total = antes["total_solicitudes"]
    base_validacion = antes["rechazadas_validacion"]

    # --- Etapa 2 (negativa): la validación está conectada y rechaza basura ---
    r_vacio = client.post("/traducir", json={"texto": "   "})
    _exigir(
        r_vacio.status_code == 400,
        2,
        f"la validación no rechazó un texto de solo espacios (esperado 400, llegó {r_vacio.status_code}).",
    )
    log("[OK] Etapa 2a: validación rechaza texto vacío con 400")
    evidencia["2a_validacion"] = r_vacio.status_code

    # --- Etapas 1-2 (positiva): solicitud válida pasa validación y rate limiting ---
    r = client.post("/traducir", json={"texto": TEXTO, "dialecto": DIALECTO})
    _exigir(
        r.status_code == 200,
        "1-2",
        f"/traducir no aceptó una solicitud válida (validación o rate limiting bloqueando de más, "
        f"o modelo no cargado). Respuesta: {r.status_code} {r.text[:200]}",
    )
    log("[OK] Etapa 1-2: solicitud válida aceptada (validación + rate limiting) -> 200")
    cuerpo = r.json()

    # --- Etapa 3: el modelo generó una traducción ---
    traduccion = cuerpo.get("traduccion")
    _exigir(isinstance(traduccion, str) and traduccion.strip(), 3, f"no se devolvió una traducción no vacía: {cuerpo}")
    if traduccion_esperada is not None:
        _exigir(traduccion == traduccion_esperada, 3, f"traducción inesperada: {traduccion!r} != {traduccion_esperada!r}")
    _exigir(cuerpo.get("dialecto") == DIALECTO, 3, f"el dialecto no se propagó a la respuesta: {cuerpo.get('dialecto')!r}")
    log(f"[OK] Etapa 3: el modelo generó la traducción -> {traduccion!r}")
    evidencia["3_traduccion"] = traduccion

    # --- Etapa 5: la respuesta trae solicitud_id utilizable ---
    solicitud_id = cuerpo.get("solicitud_id")
    _exigir(solicitud_id, 5, f"la respuesta no trae solicitud_id, no se podrá dar retroalimentación: {cuerpo}")
    log(f"[OK] Etapa 5: la respuesta llegó al cliente con solicitud_id={solicitud_id}")
    evidencia["5_solicitud_id"] = solicitud_id

    # --- Etapa 4: la métrica de ESTA solicitud quedó registrada (deltas) ---
    despues = client.get("/metricas").json()
    _exigir(despues["total_solicitudes"] == base_total + 2, 4, (
        f"total_solicitudes no subió en 2 (vacía + válida): {base_total} -> {despues['total_solicitudes']}"))
    _exigir(despues["rechazadas_validacion"] == base_validacion + 1, 4, (
        f"rechazadas_validacion no subió en 1: {base_validacion} -> {despues['rechazadas_validacion']}"))
    m = _dialecto(despues, DIALECTO)
    _exigir(m.get("solicitudes", 0) == base_sol + 1, 4, f"no se registró la solicitud en por_dialecto[{DIALECTO!r}]: {m}")
    _exigir(m.get("latencia_promedio_seg") is not None, 4, f"no se registró latencia para el dialecto {DIALECTO!r}: {m}")
    log(f"[OK] Etapa 4: métrica registrada (solicitudes +1, latencia prom. {m['latencia_promedio_seg']} s)")
    evidencia["4_metrica"] = m

    # --- Etapa 6a: el endpoint de retroalimentación funciona ---
    r_fb = client.post("/retroalimentacion", json={"solicitud_id": solicitud_id, "es_correcta": True})
    _exigir(r_fb.status_code == 200, 6, f"POST /retroalimentacion falló: {r_fb.status_code} {r_fb.text[:200]}")
    _exigir(r_fb.json() == {"registrada": True}, 6, f"/retroalimentacion no confirmó el registro: {r_fb.json()}")
    log("[OK] Etapa 6a: POST /retroalimentacion confirmó el registro")

    # --- Etapa 6b: /metricas refleja la retroalimentación ---
    final = client.get("/metricas").json()
    mf = _dialecto(final, DIALECTO)
    _exigir(mf.get("retroalimentacion_total", 0) == base_fb + 1, 6, f"/metricas no reflejó la retroalimentación: {mf}")
    _exigir(mf.get("tasa_retroalimentacion_positiva") is not None, 6, f"falta tasa_retroalimentacion_positiva: {mf}")
    log(f"[OK] Etapa 6b: /metricas refleja la retroalimentación (tasa positiva {mf['tasa_retroalimentacion_positiva']})")
    evidencia["6_metricas_final"] = mf

    # --- Privacidad: ningún texto individual aparece en /metricas ---
    _exigir("Que chimba" not in str(final), 6, "FUGA DE PRIVACIDAD: el texto original apareció en /metricas.")
    _exigir(traduccion not in str(final), 6, "FUGA DE PRIVACIDAD: la traducción apareció en /metricas.")
    log("[OK] Privacidad: /metricas no expone el texto ni la traducción")
    return evidencia


# ----------------------------------------------------------------------
# Modo pytest: en proceso, con la generación mockeada
# ----------------------------------------------------------------------


def _app_en_proceso():
    import os

    os.environ["SKIP_MODEL_LOAD"] = "1"
    import api.main as api_main

    return api_main


def _limpiar_estado(api_main):
    api_main._rate_limit_historial.clear()
    for clave in api_main.METRICAS:
        api_main.METRICAS[clave] = 0
    api_main.METRICAS_POR_DIALECTO.clear()
    api_main._solicitudes_pendientes_feedback.clear()


def _correr_en_proceso(api_main, generar):
    from unittest.mock import patch

    from fastapi.testclient import TestClient

    _limpiar_estado(api_main)
    api_main.MODELO_ESTADO["tokenizer"] = "mock"
    api_main.MODELO_ESTADO["modelo"] = "mock"
    try:
        with TestClient(api_main.app) as client, patch.object(api_main, "_generar_traduccion", generar):
            return verificar_cadena(client, traduccion_esperada="That's awesome, buddy!", log=lambda _: None)
    finally:
        api_main.MODELO_ESTADO["tokenizer"] = None
        api_main.MODELO_ESTADO["modelo"] = None
        _limpiar_estado(api_main)


def test_cadena_completa_traducir_metricas_retroalimentacion():
    api_main = _app_en_proceso()
    evidencia = _correr_en_proceso(api_main, lambda tok, mod, texto: "That's awesome, buddy!")
    assert evidencia["3_traduccion"] == "That's awesome, buddy!"


def test_si_se_rompe_el_registro_de_metricas_falla_en_la_etapa_4(monkeypatch):
    """Criterio de calidad: un eslabón roto se reporta con su etapa."""
    import pytest

    api_main = _app_en_proceso()
    monkeypatch.setattr(api_main, "_registrar_latencia", lambda dialecto, segundos: None)
    with pytest.raises(EtapaRota, match=r"Etapa 4 ROTA"):
        _correr_en_proceso(api_main, lambda tok, mod, texto: "That's awesome, buddy!")


def test_si_se_rompe_la_retroalimentacion_falla_en_la_etapa_6(monkeypatch):
    import pytest

    api_main = _app_en_proceso()
    monkeypatch.setattr(api_main, "_registrar_retroalimentacion", lambda solicitud_id, es_correcta: False)
    with pytest.raises(EtapaRota, match=r"Etapa 6 ROTA"):
        _correr_en_proceso(api_main, lambda tok, mod, texto: "That's awesome, buddy!")


# ----------------------------------------------------------------------
# Modo servicio real
# ----------------------------------------------------------------------


def main() -> int:
    p = argparse.ArgumentParser(description="E2E contra un servicio FastAPI real.")
    p.add_argument("--url", required=True, help="p. ej. http://127.0.0.1:8000")
    p.add_argument("--timeout", type=float, default=300.0, help="segundos (el modelo en CPU tarda 60-90 s)")
    a = p.parse_args()
    print(f"E2E contra {a.url}")
    try:
        with httpx.Client(base_url=a.url, timeout=a.timeout) as client:
            verificar_cadena(client)
    except EtapaRota as e:
        print(f"[FALLO] {e}")
        return 1
    except httpx.RequestError as e:
        print(f"[FALLO] Etapa 0: no se pudo conectar a {a.url} ({type(e).__name__}: {e})")
        return 1
    print("RESULTADO: las 6 etapas pasaron.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
