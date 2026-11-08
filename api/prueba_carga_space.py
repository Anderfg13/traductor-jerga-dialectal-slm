"""
api/prueba_carga_space.py

Prueba de carga contra el Space DESPLEGADO en Hugging Face (Gradio +
ZeroGPU, Sesión 26), con el modelo real -- a diferencia de
`api/prueba_carga.py` (Sesión 30), que mide solo la capa de API con una
traducción simulada. Ver `docs/pruebas_carga.md` para metodología y
resultados.

La API de Gradio es de dos pasos: POST /gradio_api/call/traducir
devuelve un event_id, y GET /gradio_api/call/traducir/<event_id> es un
stream de eventos que termina en `event: complete` (con el resultado) o
`event: error`. La latencia reportada es el tiempo completo de ambos
pasos, de extremo a extremo.

Uso:
    python api/prueba_carga_space.py --niveles 5 20 50

Sin token, el Space aplica la cuota diaria de ZeroGPU para clientes
anónimos (se agota con muy pocas solicitudes). Para repetir la prueba
con más cuota: `export HF_TOKEN=...` antes de correrla (nunca se
escribe en el código).
"""

import argparse
import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor

import httpx

URL_DEFAULT = "https://andry891-traductor-jerga-dialectal.hf.space"
_TOKEN = os.environ.get("HF_TOKEN")  # opcional: más cuota de ZeroGPU que un cliente anónimo
HEADERS = {"Authorization": f"Bearer {_TOKEN}"} if _TOKEN else {}
TEXTO = "Que chimba de parche, nos vemos mas tarde bacano"


def _una_solicitud(url: str, timeout: float) -> dict:
    inicio = time.monotonic()
    try:
        r = httpx.post(
            f"{url}/gradio_api/call/traducir",
            json={"data": [TEXTO, "Andina"]},
            headers=HEADERS,
            timeout=timeout,
        )
        if r.status_code != 200:
            return {"estado": f"http_{r.status_code}", "seg": time.monotonic() - inicio, "detalle": r.text[:150]}
        event_id = r.json()["event_id"]
        with httpx.stream("GET", f"{url}/gradio_api/call/traducir/{event_id}", headers=HEADERS, timeout=timeout) as s:
            evento, cuerpo = None, ""
            for linea in s.iter_lines():
                if linea.startswith("event:"):
                    evento = linea.split(":", 1)[1].strip()
                elif linea.startswith("data:") and evento in ("complete", "error"):
                    cuerpo = linea.split(":", 1)[1].strip()
                    break
        return {"estado": evento or "sin_evento", "seg": time.monotonic() - inicio, "detalle": cuerpo[:150]}
    except httpx.TimeoutException:
        return {"estado": "timeout", "seg": time.monotonic() - inicio, "detalle": ""}
    except httpx.RequestError as e:
        return {"estado": "error_conexion", "seg": time.monotonic() - inicio, "detalle": type(e).__name__}


def correr_nivel(url: str, n: int, timeout: float) -> dict:
    inicio = time.monotonic()
    with ThreadPoolExecutor(max_workers=n) as pool:
        resultados = list(pool.map(lambda _: _una_solicitud(url, timeout), range(n)))
    duracion = time.monotonic() - inicio

    ok = [r for r in resultados if r["estado"] == "complete"]
    fallos = [r for r in resultados if r["estado"] != "complete"]
    lat_ok = [r["seg"] for r in ok]
    estados = {}
    for r in fallos:
        estados[r["estado"]] = estados.get(r["estado"], 0) + 1
    return {
        "n": n,
        "ok": len(ok),
        "fallos": len(fallos),
        "estados_fallo": estados,
        "ejemplo_fallo": fallos[0]["detalle"] if fallos else "",
        "lat_prom": round(statistics.mean(lat_ok), 2) if lat_ok else None,
        "lat_mediana": round(statistics.median(lat_ok), 2) if lat_ok else None,
        "lat_max": round(max(lat_ok), 2) if lat_ok else None,
        "duracion_total": round(duracion, 2),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--url", default=URL_DEFAULT)
    p.add_argument("--niveles", type=int, nargs="+", default=[5, 20, 50])
    p.add_argument("--timeout", type=float, default=300.0)
    p.add_argument("--pausa", type=float, default=10.0, help="segundos entre niveles")
    a = p.parse_args()

    print("calentamiento (1 solicitud, no cuenta en los niveles)...")
    w = _una_solicitud(a.url, a.timeout)
    print(f"  estado={w['estado']} seg={w['seg']:.2f} {w['detalle']}")

    print(f"{'nivel':>5} | {'ok':>3} | {'fallos':>6} | {'prom(s)':>8} | {'mediana':>8} | {'max(s)':>7} | {'total(s)':>8} | fallos por tipo")
    for i, n in enumerate(a.niveles):
        if i:
            time.sleep(a.pausa)
        r = correr_nivel(a.url, n, a.timeout)
        print(
            f"{r['n']:>5} | {r['ok']:>3} | {r['fallos']:>6} | {str(r['lat_prom']):>8} | "
            f"{str(r['lat_mediana']):>8} | {str(r['lat_max']):>7} | {r['duracion_total']:>8} | {r['estados_fallo']}"
        )
        if r["ejemplo_fallo"]:
            print(f"        ejemplo de fallo: {r['ejemplo_fallo']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
