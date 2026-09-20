"""
api/prueba_carga.py

Prueba de carga simple: manda N solicitudes CONCURRENTES a un
servicio real corriendo (no `TestClient`, un proceso `uvicorn` de
verdad) y mide latencia y tasa de error/límite de tasa.

Por qué con traducción simulada, no el modelo real: el modelo de 3B en
esta máquina (sin GPU) tarda 50-80s POR SOLICITUD (Sesiones 25/27) --
correr 50 solicitudes concurrentes contra el modelo real saturaría la
máquina durante muchos minutos solo para esta prueba, sin aportar una
medición distinta (el cuello de botella ya se conoce y está
documentado: falta de GPU). Esta prueba mide en cambio lo que SÍ
depende del código del servicio y no del hardware: si el rate
limiting, las métricas y el manejo de concurrencia (locks) se
comportan bien bajo carga real. Ver `docs/pruebas_carga.md` para la
metodología completa y los resultados, incluyendo qué falta medir con
el modelo real cuando haya GPU disponible.

Uso — en una terminal, levantar el servicio con traducción simulada:
    SKIP_MODEL_LOAD=1 MOCK_TRANSLATION_TEXT="mock" MOCK_TRANSLATION_DELAY_SEG=0.3 \
        python -m uvicorn api.main:app --port 8000

En otra terminal, correr la prueba:
    python api/prueba_carga.py --url http://127.0.0.1:8000 --niveles 5 20 50
"""

import argparse
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx


def _una_solicitud(url: str) -> tuple[int, float]:
    inicio = time.monotonic()
    try:
        r = httpx.post(f"{url}/traducir", json={"texto": "Que chimba, parcero!"}, timeout=30.0)
        return r.status_code, time.monotonic() - inicio
    except httpx.RequestError:
        return -1, time.monotonic() - inicio  # -1 = error de conexión, no HTTP


def correr_nivel(url: str, n_concurrentes: int) -> dict:
    with ThreadPoolExecutor(max_workers=n_concurrentes) as pool:
        futuros = [pool.submit(_una_solicitud, url) for _ in range(n_concurrentes)]
        resultados = [f.result() for f in as_completed(futuros)]

    codigos = [c for c, _ in resultados]
    latencias = [t for _, t in resultados]

    return {
        "n": n_concurrentes,
        "exitosas_200": codigos.count(200),
        "rate_limited_429": codigos.count(429),
        "errores_conexion": codigos.count(-1),
        "otros_codigos": [c for c in codigos if c not in (200, 429, -1)],
        "latencia_prom_seg": round(statistics.mean(latencias), 3),
        "latencia_max_seg": round(max(latencias), 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--niveles", type=int, nargs="+", default=[5, 20, 50])
    args = parser.parse_args()

    try:
        r = httpx.get(f"{args.url}/salud", timeout=5.0)
        assert r.status_code == 200
    except Exception as e:
        print(f"ERROR: {args.url}/salud no responde ({e}). ¿Está el servicio corriendo?")
        return 1

    print(f"{'nivel':>6} | {'200':>5} | {'429':>5} | {'err':>4} | {'lat.prom(s)':>12} | {'lat.max(s)':>11}")
    for n in args.niveles:
        r = correr_nivel(args.url, n)
        print(
            f"{r['n']:>6} | {r['exitosas_200']:>5} | {r['rate_limited_429']:>5} | "
            f"{r['errores_conexion']:>4} | {r['latencia_prom_seg']:>12} | {r['latencia_max_seg']:>11}"
        )
        if r["otros_codigos"]:
            print(f"   (códigos inesperados en este nivel: {r['otros_codigos']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
