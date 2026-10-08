"""
evaluation/pi3_portabilidad.py

PI3 (portabilidad): mide con números el tamaño del modelo y de los
adaptadores, la memoria al cargarlo, la latencia en CPU y, sobre todo, si
el sistema funciona SIN internet una vez descargados los pesos.

Prueba "sin red": el proceso de trabajo (`--trabajador`) arranca con
HF_HUB_OFFLINE=1 y TRANSFORMERS_OFFLINE=1 y, además, con TODA conexión de
red bloqueada a nivel de sockets (cualquier `connect`, `getaddrinfo` o
`create_connection` se cuenta y falla). Carga el modelo base y el adaptador
desde la caché local de Hugging Face y traduce 3 frases. Si el contador de
intentos de conexión es 0 y las traducciones salen, el sistema no necesita
internet para ejecutar.

Los pesos ya deben estar descargados en la caché de Hugging Face (el primer
arranque sí necesita internet para bajarlos, una sola vez).

    python evaluation/pi3_portabilidad.py            # corre todo y escribe evaluation/pi3_portabilidad.md
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EVAL = Path(__file__).resolve().parent
ADAPTER = RAIZ / "finetuning" / "checkpoints" / "generador3" / "adapter"
FRASES = ["Che, estoy remando con el sueldo que me dan.", "No hay bronca, ahorita te marco.", "Estar hecho percha después de tanto laburar."]


def trabajador():
    """Se ejecuta en un proceso aparte con la red bloqueada."""
    import socket

    intentos = {"n": 0, "ejemplos": []}

    def bloquear(*a, **k):
        intentos["n"] += 1
        if len(intentos["ejemplos"]) < 3:
            intentos["ejemplos"].append(str(a)[:80])
        raise OSError("RED BLOQUEADA por la prueba de portabilidad")

    socket.socket.connect = bloquear
    socket.socket.connect_ex = bloquear
    socket.create_connection = bloquear
    socket.getaddrinfo = bloquear

    sys.path.insert(0, str(RAIZ / "finetuning"))
    import psutil
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    import probar_baseline

    proc = psutil.Process()
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(probar_baseline.MODEL_ID)
    modelo = AutoModelForCausalLM.from_pretrained(probar_baseline.MODEL_ID, dtype=torch.bfloat16, device_map="cpu")
    modelo = PeftModel.from_pretrained(modelo, str(ADAPTER))
    modelo.eval()
    carga = time.time() - t0
    rss_carga = proc.memory_info().rss / 1e9

    salidas, lat = [], []
    for f in FRASES:
        t1 = time.time()
        salidas.append(probar_baseline.traducir(tok, modelo, f))
        lat.append(time.time() - t1)
    print(json.dumps({"intentos_de_conexion": intentos["n"], "ejemplos_de_intento": intentos["ejemplos"],
                      "segundos_de_carga": round(carga, 1), "ram_tras_cargar_gb": round(rss_carga, 2),
                      "ram_pico_tras_generar_gb": round(proc.memory_info().rss / 1e9, 2),
                      "traducciones": salidas, "latencias_s": [round(x, 1) for x in lat]}, ensure_ascii=False))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--trabajador", action="store_true")
    a = p.parse_args()
    if a.trabajador:
        trabajador()
        return 0

    cache = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub" / "models--Qwen--Qwen2.5-3B-Instruct" / "snapshots"
    snap = next(cache.iterdir())
    pesos_base = sum(f.stat().st_size for f in snap.glob("*.safetensors"))
    adaptador = (ADAPTER / "adapter_model.safetensors").stat().st_size
    mezcla_ad = (RAIZ / "finetuning" / "checkpoints" / "mezcla" / "adapter" / "adapter_model.safetensors").stat().st_size

    env = {**os.environ, "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "PYTHONUTF8": "1"}
    print("Ejecutando la prueba sin red (carga del modelo en CPU y 3 traducciones; tarda unos minutos)...", flush=True)
    r = subprocess.run([sys.executable, str(Path(__file__)), "--trabajador"], capture_output=True, text=True, env=env, encoding="utf-8")
    linea = next((l for l in r.stdout.splitlines()[::-1] if l.startswith("{")), None)
    if r.returncode != 0 or not linea:
        print("FALLO la prueba sin red:\n", r.stderr[-1500:])
        return 1
    d = json.loads(linea)

    L = [
        "# PI3: portabilidad (tamaño, memoria, latencia y funcionamiento sin internet)", "",
        "Generado por `evaluation/pi3_portabilidad.py`. Máquina: CPU, sin GPU (la de desarrollo del equipo).", "",
        "## Tamaño", "",
        "| Pieza | Tamaño |", "|---|---|",
        f"| Modelo base Qwen2.5-3B-Instruct (bfloat16, pesos) | {pesos_base / 1e9:.2f} GB |",
        f"| Adaptador LoRA de un generador (r=8) | {adaptador / 1e6:.1f} MB ({100 * adaptador / pesos_base:.2f} % del base) |",
        f"| Adaptador de la mezcla | {mezcla_ad / 1e6:.1f} MB |",
        "| Parámetros entrenables del adaptador | 3.69 M (0.12 % de ~3.1 B) |",
        "| Un modelo completo ya fusionado con `mergekit` (float16) | ~6.2 GB |", "",
        "Cambiar de \"especialización\" cuesta 14.8 MB (un adaptador) y no otros 6 GB, porque el modelo base se comparte.", "",
        "## Funciona sin internet", "",
        f"- Proceso con `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1` y **toda conexión de red bloqueada** a nivel de sockets "
        f"(se cuenta cualquier `connect`/`getaddrinfo`).",
        f"- **Intentos de conexión durante la carga y la generación: {d['intentos_de_conexion']}**.",
        "- Carga el modelo base y el adaptador desde la caché local y traduce:", "",
        "| Entrada | Traducción | Latencia |", "|---|---|---|",
    ]
    for f, t, s in zip(FRASES, d["traducciones"], d["latencias_s"]):
        L.append(f"| {f} | {t} | {s} s |")
    L += ["",
          f"- Carga \"del modelo\": {d['segundos_de_carga']} s y {d['ram_tras_cargar_gb']} GB de RAM, **pero es engañoso**: los pesos se mapean de forma perezosa desde disco y recién se leen a RAM durante la primera traducción, que por eso es la más lenta. La cifra que importa es la RAM tras generar: **{d['ram_pico_tras_generar_gb']} GB** (el modelo de ~6.2 GB en bfloat16 más activaciones). Hace falta una máquina con al menos ~8 GB de RAM libre.", "",
          "**Limitaciones de esta prueba**: bloquear los sockets dentro del proceso demuestra que el código de carga y generación no necesita red; "
          "no es lo mismo que desconectar físicamente la máquina. Los pesos se descargaron antes (el primer arranque sí necesita internet, una sola vez). "
          "Solo se probó el adaptador del Generador 3 en CPU, no el servicio completo ni la imagen Docker.", "",
          "## Latencia (una solicitud, un texto corto)", "",
          "| Entorno | Latencia | Fuente |", "|---|---|---|",
          f"| CPU local, sin GPU | {min(d['latencias_s'])}-{max(d['latencias_s'])} s (esta prueba); 50-80 s en pruebas anteriores | esta prueba; BITACORA Sesión 25 |",
          "| GPU T4 (Colab), modelo ajustado, una a una sobre 174 entradas | ~1.9 s por entrada (5.6 min / 174) | `finetuning/tiempos_fase3_corrida2.json` |",
          "| GPU compartida (ZeroGPU, Space público), una solicitud | 2.5 s | `docs/despliegue.md` |", "",
          "Sin GPU el modelo de 3B no es interactivo; con una GPU modesta sí. No se evaluó cuantización (int8/int4) ni formatos ligeros (GGUF), que "
          "probablemente acercarían el uso en CPU a algo utilizable: queda como trabajo futuro, no como resultado.", ""]
    texto = "\n".join(L)
    (EVAL / "pi3_portabilidad.md").write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
