"""
tests/test_integracion_e2e.py

Prueba de integración end-to-end (Sesión 31): confirma que las 6
etapas de la cadena completa del servicio están conectadas de punta a
punta, en un solo flujo:

  1. Cliente manda una solicitud a POST /traducir.
  2. Pasa por validación (Sesión 28) y rate limiting (Sesión 28) sin
     ser rechazada.
  3. El modelo ajustado genera la traducción.
  4. Se registra la métrica (latencia por dialecto, Sesión 29).
  5. La respuesta llega al cliente con `solicitud_id`.
  6. El endpoint de retroalimentación (POST /retroalimentacion,
     Sesión 29) funciona, y GET /metricas refleja tanto la solicitud
     como la retroalimentación.

No usa el modelo real (`SKIP_MODEL_LOAD=1` + traducción mockeada) por
la misma razón que el resto de las pruebas de `api/test_main.py`: esta
máquina no tiene GPU y cargar el modelo de 3B para esto tardaría
50-80s solo para levantar el proceso. Lo que SÍ es real aquí es el
camino de código completo -- ninguna pieza está mockeada salvo la
generación del texto de traducción en sí.

Cada etapa tiene su propia aserción con mensaje descriptivo, para que
si algo se rompe, el fallo señale EXACTAMENTE qué eslabón fue --  no
un fallo genérico al final.

Uso:
    SKIP_MODEL_LOAD=1 python -m pytest tests/test_integracion_e2e.py -v
"""

import os

os.environ["SKIP_MODEL_LOAD"] = "1"

from unittest.mock import patch  # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402

import api.main as api_main  # noqa: E402


def _limpiar_estado():
    api_main._rate_limit_historial.clear()
    for clave in api_main.METRICAS:
        api_main.METRICAS[clave] = 0
    api_main.METRICAS_POR_DIALECTO.clear()
    api_main._solicitudes_pendientes_feedback.clear()


def test_cadena_completa_traducir_metricas_retroalimentacion():
    _limpiar_estado()
    api_main.MODELO_ESTADO["tokenizer"] = "mock"
    api_main.MODELO_ESTADO["modelo"] = "mock"

    try:
        with TestClient(api_main.app) as client, patch.object(
            api_main, "_generar_traduccion", lambda tok, mod, texto: "That's awesome, buddy!"
        ):
            # --- Etapa 1-2: solicitud real, pasa validación y rate limiting ---
            r_traducir = client.post("/traducir", json={"texto": "Que chimba, parcero!", "dialecto": "Andina"})
            assert r_traducir.status_code == 200, (
                f"Etapa 1-2 rota: /traducir no aceptó una solicitud válida (validación o rate limiting "
                f"bloqueando de más). Respuesta: {r_traducir.status_code} {r_traducir.text}"
            )

            # --- Etapa 3: el modelo (mockeado) generó una traducción ---
            cuerpo = r_traducir.json()
            assert cuerpo["traduccion"] == "That's awesome, buddy!", "Etapa 3 rota: no se devolvió la traducción generada."
            assert cuerpo["dialecto"] == "Andina", "Etapa 3 rota: el dialecto de la solicitud no se propagó a la respuesta."

            # --- Etapa 5: la respuesta al cliente trae un solicitud_id usable ---
            solicitud_id = cuerpo.get("solicitud_id")
            assert solicitud_id, "Etapa 5 rota: la respuesta no trae un solicitud_id para poder dar retroalimentación después."

            # --- Etapa 4: la métrica de esta solicitud ya quedó registrada ---
            metricas_antes = client.get("/metricas").json()
            assert metricas_antes["total_solicitudes"] == 1, "Etapa 4 rota: total_solicitudes no se incrementó."
            assert metricas_antes["traducciones_exitosas"] == 1, "Etapa 4 rota: traducciones_exitosas no se incrementó."
            assert "Andina" in metricas_antes["por_dialecto"], "Etapa 4 rota: no se registró métrica por dialecto."
            assert metricas_antes["por_dialecto"]["Andina"]["solicitudes"] == 1, (
                "Etapa 4 rota: el contador de solicitudes por dialecto no coincide."
            )
            assert metricas_antes["por_dialecto"]["Andina"]["latencia_promedio_seg"] is not None, (
                "Etapa 4 rota: no se registró latencia para esta solicitud."
            )

            # --- Etapa 6a: el endpoint de retroalimentación funciona ---
            r_feedback = client.post("/retroalimentacion", json={"solicitud_id": solicitud_id, "es_correcta": True})
            assert r_feedback.status_code == 200, f"Etapa 6 rota: POST /retroalimentacion falló ({r_feedback.text})."
            assert r_feedback.json() == {"registrada": True}, "Etapa 6 rota: /retroalimentacion no confirmó el registro."

            # --- Etapa 6b: /metricas refleja la retroalimentación ---
            metricas_despues = client.get("/metricas").json()
            m_andina = metricas_despues["por_dialecto"]["Andina"]
            assert m_andina["retroalimentacion_total"] == 1, "Etapa 6 rota: /metricas no reflejó la retroalimentación recibida."
            assert m_andina["tasa_retroalimentacion_positiva"] == 1.0, (
                "Etapa 6 rota: la tasa de retroalimentación positiva no es la esperada."
            )

            # Ninguna solicitud individual (texto, traducción) debe aparecer expuesta en /metricas.
            assert "Que chimba" not in str(metricas_despues), "Fuga de privacidad: el texto original apareció en /metricas."
            assert "That's awesome" not in str(metricas_despues), "Fuga de privacidad: la traducción apareció en /metricas."
    finally:
        api_main.MODELO_ESTADO["tokenizer"] = None
        api_main.MODELO_ESTADO["modelo"] = None
        _limpiar_estado()
