"""
generation/comparar_generadores.py

Tabla comparativa de los tres generadores sintéticos: el primer insumo
real para PI1. Una fila por generador con cantidad de ejemplos, porcentaje
filtrado y tiempo/costo aproximado de generación, más estadísticas
descriptivas de los datos. No llama a ninguna API salvo con
`--medir-latencia`.

    python generation/comparar_generadores.py                    # usa las latencias guardadas
    python generation/comparar_generadores.py --medir-latencia   # hace 3 llamadas reales por generador

Salidas: generation/comparacion_generadores.md y
generation/latencias_generadores.json (última medición).

Sobre tiempo y costo (importante, para no leer la tabla de más):
  - Tiempo: NO se guardó el tiempo de las corridas reales (se pausaron,
    se reanudaron y alguna se colgó). Por eso se MIDE aparte: 3 llamadas
    reales por generador sobre las mismas 3 semillas (sem-006, sem-007,
    sem-018) y se reporta la mediana por llamada; el total para 100
    semillas es esa mediana x 100, una estimación de generación
    secuencial SIN contar reintentos por límite de tasa.
  - Costo: los tres se usaron en capa gratuita, así que el costo en
    dinero fue 0. Se reporta cuántas llamadas se gastaron y los tokens
    aproximados (caracteres / 4; es una aproximación, no el conteo del
    proveedor). No se calcula un "costo si fuera de pago" porque no
    verificamos tarifas vigentes.
"""

import argparse
import json
import re
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

GEN = Path(__file__).resolve().parent
sys.path.insert(0, str(GEN))

NOMBRES = {1: "Groq `openai/gpt-oss-20b`", 2: "Cohere `command-r-08-2024`", 3: "Google `gemini-3.5-flash-lite`"}
SEMILLAS_MEDICION = ["sem-006", "sem-007", "sem-018"]
LATENCIAS = GEN / "latencias_generadores.json"


def medir_latencias() -> dict:
    import generar_sintetico as gs

    semillas = {s["id"]: s for s in gs.cargar_semillas([1, 2])}
    resultado = {}
    for g in (1, 2, 3):
        cliente = gs.crear_cliente(g)
        tiempos = []
        for sid in SEMILLAS_MEDICION:
            inicio = time.monotonic()
            gs.llamar_con_reintentos(g, cliente, gs.construir_prompt(semillas[sid]), 3, 2.0)
            tiempos.append(time.monotonic() - inicio)
        resultado[str(g)] = {"segundos": [round(t, 2) for t in tiempos], "mediana": round(statistics.median(tiempos), 2)}
        print(f"G{g}: {resultado[str(g)]}")
    LATENCIAS.write_text(json.dumps(resultado, indent=1), encoding="utf-8")
    return resultado


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--medir-latencia", action="store_true")
    a = p.parse_args()

    if a.medir_latencia:
        lat = medir_latencias()
    elif LATENCIAS.exists():
        lat = json.loads(LATENCIAS.read_text(encoding="utf-8"))
    else:
        lat = {}

    datos = []
    for g in (1, 2, 3):
        crudo = json.loads((GEN / f"dataset_generador{g}.json").read_text(encoding="utf-8"))
        limpio = json.loads((GEN / f"dataset_generador{g}_limpio.json").read_text(encoding="utf-8"))
        raws = [json.loads(r.read_text(encoding="utf-8")) for r in sorted((GEN / "raw" / f"generador{g}").glob("*.json"))]
        por_semilla = Counter(v["seed_id"] for v in crudo)
        textos = Counter(v["texto_dialectal"].strip().lower() for v in limpio)
        che = sum(1 for v in limpio if v["dialecto_region"] != "Rioplatense" and re.search(r"\bche\b", v["texto_dialectal"], re.I))
        datos.append(
            {
                "g": g, "crudo": len(crudo), "limpio": len(limpio), "llamadas": len(raws),
                "tok_in": sum(len(r["prompt"]) for r in raws) / 4, "tok_out": sum(len(r["respuesta_cruda"]) for r in raws) / 4,
                "por_semilla": statistics.mean(por_semilla.values()), "rango": (min(por_semilla.values()), max(por_semilla.values())),
                "pal_es": statistics.mean(len(v["texto_dialectal"].split()) for v in limpio),
                "pal_en": statistics.mean(len(v["traduccion"].split()) for v in limpio),
                "reg": Counter(v["registro"] for v in crudo),
                "repetidos": sum(c - 1 for c in textos.values() if c > 1), "che": che,
            }
        )

    L = [
        "# Comparación de los tres generadores sintéticos (primer insumo para PI1)", "",
        "Mismas 100 semillas (`seeds/lote_01` + `lote_02`), misma plantilla de prompt, mismo filtro (`generation/validar.py`). "
        "Generado por `generation/comparar_generadores.py`; leer primero la nota sobre tiempo y costo al final.", "",
        "## Resumen: una fila por generador", "",
        "| Generador | Ejemplos generados | Tras el filtro | Filtrado | Tiempo por llamada | Tiempo estimado, 100 semillas | Costo |",
        "|---|---|---|---|---|---|---|",
    ]
    for d in datos:
        t = lat.get(str(d["g"]))
        por_llamada = f"{t['mediana']:.1f} s (rango {min(t['segundos']):.1f}-{max(t['segundos']):.1f})" if t else "sin medir"
        total = f"~{t['mediana'] * 100 / 60:.0f} min" if t else "sin medir"
        L.append(
            f"| G{d['g']} {NOMBRES[d['g']]} | {d['crudo']} | {d['limpio']} | {d['crudo'] - d['limpio']} "
            f"({100 * (d['crudo'] - d['limpio']) / d['crudo']:.1f} %) | {por_llamada} | {total} | "
            f"$0 (capa gratuita); {d['llamadas']} semillas (sin contar regeneraciones), ~{d['tok_in'] / 1000:.0f}k tokens de entrada y ~{d['tok_out'] / 1000:.0f}k de salida |"
        )

    regs = sorted({k for d in datos for k in d["reg"]})
    L += ["", "## Estadísticas de los datos", "", "| | " + " | ".join(f"G{d['g']}" for d in datos) + " |", "|---|" + "---|" * len(datos)]

    def fila(nombre, fn):
        L.append(f"| {nombre} | " + " | ".join(fn(d) for d in datos) + " |")

    fila("Variantes por semilla (prom., mín-máx)", lambda d: f"{d['por_semilla']:.1f} ({d['rango'][0]}-{d['rango'][1]})")
    fila("Palabras por texto dialectal (prom.)", lambda d: f"{d['pal_es']:.1f}")
    fila("Palabras por traducción (prom.)", lambda d: f"{d['pal_en']:.1f}")
    for r in regs:
        fila(f"Registro `{r}`", lambda d, r=r: f"{100 * d['reg'][r] / d['crudo']:.0f} %")
    fila("Textos repetidos entre semillas", lambda d: str(d["repetidos"]))
    fila("'che' en variantes no rioplatenses (mezcla de dialecto)", lambda d: str(d["che"]))

    L += [
        "", "## Cómo leerla para PI1", "",
        "- **El filtro casi no distingue generadores** (0.3 % vs 0 %): solo mira vacíos, duplicados, longitud, parecido a la semilla e idioma. "
        "La diferencia de calidad entre generadores tendrá que salir de los modelos entrenados con cada uno, no de esta tabla.",
        "- **Mezcla de dialecto**: G1 tiene variantes con \"che\" en dialectos que no son rioplatenses; G2 y G3 no. Es un indicio con una "
        "heurística de un solo marcador y pocos casos, no una conclusión.",
        "- **Registro**: G2 produce más registro formal y menos jerga que G1 y G3, con el mismo prompt.",
        "- G3 es un modelo \"lite\", más pequeño que los otros dos: una diferencia entre generadores no se puede atribuir solo a \"qué LLM es\".",
        "- Los tres tienen tamaño comparable (589 / 632 / 625), así que el tamaño del dataset no es una variable de confusión grande.",
        "", "## Nota sobre tiempo y costo", "",
        "El tiempo de las corridas reales no se guardó (se pausaron, se reanudaron y la de Cohere se colgó una vez), así que el tiempo "
        "por llamada se midió aparte con 3 llamadas reales por generador (`sem-006`, `sem-007`, `sem-018`) y el total es esa mediana x 100: "
        "una estimación de generación secuencial **sin contar reintentos por límite de tasa**, que en la práctica alargaron mucho la "
        "corrida (Google lite permite 15 por minuto; Cohere trial fue lento). Con solo 3 mediciones es una referencia gruesa. "
        "El costo en dinero fue 0 porque los tres usan capa gratuita; los tokens son aproximados (caracteres / 4). No se calculó un "
        "costo \"si fuera de pago\" porque no se verificaron tarifas vigentes.", "",
    ]
    texto = "\n".join(L)
    (GEN / "comparacion_generadores.md").write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
