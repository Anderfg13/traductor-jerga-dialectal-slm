# Pruebas de carga/latencia (Sesión 30)

## Metodología

Herramienta: script propio (`api/prueba_carga.py`), `ThreadPoolExecutor`
mandando N solicitudes **concurrentes** a `POST /traducir` contra un
proceso `uvicorn` real (no `TestClient`), midiendo código de respuesta
y latencia por solicitud. Niveles probados: **5, 20 y 50 concurrentes**,
tal como pedía la sesión.

**Por qué con traducción simulada y no el modelo real**: el modelo de
3B en esta máquina (sin GPU) tarda 50-80s por solicitud, medido en las
Sesiones 25 y 27. Correr 50 solicitudes concurrentes contra el modelo
real habría saturado la máquina durante varios minutos solo para esta
prueba, sin medir nada que no supiéramos ya (el cuello de botella es
la falta de GPU, no el código del servicio). En su lugar, el servicio
se levantó con `SKIP_MODEL_LOAD=1` y una traducción simulada de 0.3s
de duración (`MOCK_TRANSLATION_TEXT`/`MOCK_TRANSLATION_DELAY_SEG`,
agregados a `api/main.py` en esta sesión) — esto aísla la pregunta que
sí depende del código del servicio: **¿el rate limiting, las métricas
y el manejo de concurrencia se comportan bien bajo carga real?**, sin
depender del hardware.

## Resultado 1: el límite de tasa por default SÍ protege contra ráfagas

Primera corrida, con el límite de tasa por default de la Sesión 28
(**10 solicitudes/60s por IP**), niveles 5 → 20 → 50 corridos en
secuencia contra el mismo servicio (la ventana de 60s es acumulativa
entre niveles, porque todas las solicitudes salen de la misma IP):

| Nivel | 200 (éxito) | 429 (rate limited) | Errores | Latencia prom. | Latencia máx. |
|---|---|---|---|---|---|
| 5 | 5 | 0 | 0 | 0.694s | 0.705s |
| 20 | 5 | 15 | 0 | 0.692s | 0.989s |
| 50 | 0 | 50 | 0 | 1.051s | 1.30s |

Las primeras 10 solicitudes en total (5 del nivel 1 + 5 del nivel 2)
pasan; el resto, dentro de la misma ventana de 60s, recibe `429` —
exactamente el comportamiento que la Sesión 28 diseñó y probó por
unidad, ahora confirmado bajo carga real concurrente, no solo con
`pytest`. **Conclusión**: con la configuración por default, este
servicio rechaza de forma predecible cualquier ráfaga que supere 10
solicitudes/minuto por cliente — es una protección real, no solo
documentada.

## Resultado 2: capacidad de concurrencia de la capa de API (límite de tasa desactivado)

Segunda corrida, en un proceso nuevo, con
`RATE_LIMIT_MAX_SOLICITUDES=100000` (efectivamente sin límite) para
aislar la pregunta de concurrencia pura:

| Nivel | 200 (éxito) | Errores | Latencia promedio | Latencia máxima |
|---|---|---|---|---|
| 5 | 5 | 0 | 0.707s | 0.729s |
| 20 | 20 | 0 | 0.939s | 1.038s |
| 50 | 50 | 0 | 1.298s | 1.61s |

**0% de errores en los tres niveles**, incluyendo 50 solicitudes
concurrentes. La latencia promedio sube de forma moderada con la
concurrencia (0.71s → 0.94s → 1.30s) — esperable, dado que Python
libera el GIL durante el `sleep` simulado pero el *threadpool* de
`uvicorn`/Starlette tiene un límite de hilos worker por default; no
hay caída del servicio ni degradación catastrófica hasta 50
concurrentes.

## Limitación importante de esta prueba (no se oculta)

Esta prueba mide la capacidad de concurrencia de la **capa de API**
(FastAPI, threading, rate limiting), no la del sistema completo con el
modelo real. Con el modelo de 3B cargado de verdad, cada llamada a
`_generar_traduccion` es una operación de cómputo intensivo (CPU o
GPU) sobre el **mismo objeto de modelo cargado una sola vez** — a
diferencia del `sleep` simulado (que sí libera el GIL y permite
solapamiento real), múltiples generaciones concurrentes sobre el mismo
modelo probablemente **se serializan** en la práctica (compartiendo la
misma GPU/CPU), no corren en paralelo de verdad. Medir la capacidad de
concurrencia real del sistema completo requiere GPU (Colab, o el
despliegue de la Sesión 26, todavía bloqueado hasta ~2026-10-02) y
queda como trabajo pendiente — este documento no reporta un número de
"solicitudes concurrentes que el sistema completo puede manejar" con
el modelo real, porque no se pudo medir honestamente sin ese entorno.

## Cómo reproducir

```bash
# Terminal 1
SKIP_MODEL_LOAD=1 MOCK_TRANSLATION_TEXT="mock" MOCK_TRANSLATION_DELAY_SEG=0.3 \
    RATE_LIMIT_MAX_SOLICITUDES=100000 python -m uvicorn api.main:app --port 8000

# Terminal 2
python api/prueba_carga.py --url http://127.0.0.1:8000 --niveles 5 20 50
```
