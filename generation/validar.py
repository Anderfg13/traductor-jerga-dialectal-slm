"""
generation/validar.py

Filtro automático de calidad para un dataset sintético consolidado
(por ejemplo generation/dataset_generador1.json, salida de
consolidar.py). Aplica 4 reglas; dos DESCARTAN la variante (no entra
al dataset limpio) y dos la MARCAN COMO SOSPECHOSA (se queda en el
dataset limpio, pero con un campo extra para que alguien la revise a
mano) — la elección de cuáles reglas descartan y cuáles solo marcan
está explicada en cada regla abajo.

REGLA 1 — longitud (DESCARTA): menos de 3 palabras o más de
LONGITUD_MAX_PALABRAS (40) en `texto_dialectal`. Existe porque una
variante de 1-2 palabras no es una oración de uso real con contexto
(viola el requisito 2 de generation/prompt_derivacion.md), y una
"variante" desproporcionadamente larga suele ser una alucinación del
generador (texto repetido, la instrucción completa filtrándose a la
salida, etc.) — en ningún caso es aprovechable para entrenar. El
umbral de 40 se fijó mirando la distribución real del dataset del
Generador 1 (máximo real: 26 palabras, percentil 99: 25), dejando
margen de sobra sin ser tan alto que deje pasar una alucinación.

REGLA 2 — casi idéntica a la semilla, sin variación real (DESCARTA):
si `texto_dialectal` normalizado (minúsculas, sin puntuación) tiene una
similitud >= UMBRAL_SIMILITUD_SEMILLA (0.8) contra `texto_original` de
la semilla. Existe porque el propósito entero de la derivación
(generation/prompt_derivacion.md, Sesión 6) es generar contextos de uso
reales, no repetir la semilla con un signo de puntuación distinto; una
variante así no aporta señal nueva de entrenamiento. Se descarta (no
se marca solo como sospechosa) porque no hay ambigüedad: si es
prácticamente la semilla, no cumplió su propósito, punto.

REGLA 3 — idioma inesperado (MARCA COMO SOSPECHOSA, no descarta): se
espera que `texto_dialectal` esté en español y `traduccion` en inglés;
se usa un conteo de palabras frecuentes de cada idioma (sin depender de
una librería externa de detección de idioma, que no está en
requirements.txt) y se exige al menos 2 coincidencias claras del
idioma "equivocado" para evitar falsos positivos con oraciones cortas
o palabras ambiguas entre idiomas (ej. "no"). Se marca en vez de
descartar porque es una heurística aproximada: puede tener falsos
positivos, y una variante con mezcla real de idioma (code-switching,
frecuente en jerga) podría ser válida — mejor que la revise una
persona a que se pierda de forma automática.

REGLA 4 — duplicada dentro del dataset (DESCARTA): mismo
`texto_dialectal` normalizado (minúsculas, espacios colapsados) ya
visto antes en el dataset. Existe para no entrenar dos veces sobre el
mismo ejemplo exacto, lo que sesgaría el entrenamiento hacia esa
variante. `consolidar.py` ya dedupea variantes exactas al construir el
dataset, así que en la práctica esta regla casi no encuentra nada aquí,
pero se deja como red de seguridad para datasets de otros generadores
que no pasen por ese mismo proceso.

Si el total descartado (reglas 1, 2 y 4) supera DESCARTE_MAX_PORC
(20%) del dataset, el script lo advierte claramente en el reporte y en
consola en vez de escribir los archivos de salida en silencio — un
descarte tan alto sugeriría que la plantilla de derivación necesita
ajustes, no que hay que aplicar el filtro y seguir.

Uso:
    python generation/validar.py [ruta_dataset] [ruta_semillas...]

Por defecto usa generation/dataset_generador1.json y todas las
semillas conocidas (seeds/ejemplos.json, seeds/lote_01.json,
seeds/lote_02.json que existan).

Salidas:
    generation/dataset_generador1_limpio.json
    generation/reporte_filtrado.md
"""

import difflib
import json
import re
import sys
from collections import Counter
from pathlib import Path

GENERATION_DIR = Path(__file__).resolve().parent
SEEDS_DIR = GENERATION_DIR.parent / "seeds"

LONGITUD_MIN_PALABRAS = 3
LONGITUD_MAX_PALABRAS = 40
UMBRAL_SIMILITUD_SEMILLA = 0.8
DESCARTE_MAX_PORC = 20.0

ES_STOP = {
    "que", "de", "la", "el", "en", "y", "a", "los", "las", "un", "una",
    "es", "se", "lo", "le", "su", "por", "con", "para", "al", "del",
    "me", "te", "si", "ya", "muy", "mas", "más", "pues", "tu", "mi",
    "este", "esta", "como", "porque", "esto", "eso", "sin", "sobre",
}
EN_STOP = {
    "the", "a", "an", "is", "are", "of", "to", "and", "in", "you",
    "it", "that", "this", "for", "with", "on", "was", "be", "have",
    "has", "i", "my", "your", "not", "just", "but", "so",
}


def normalizar(texto: str) -> str:
    texto = texto.lower().strip()
    texto = re.sub(r"[¡!¿?.,;:\"'—–-]", "", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto


def contar_stopwords(texto: str, stopset: set) -> tuple[int, int]:
    palabras = re.findall(r"[a-záéíóúñü']+", texto.lower())
    coincidencias = sum(1 for p in palabras if p in stopset)
    return coincidencias, len(palabras)


def cargar_semillas() -> dict:
    semillas = {}
    for nombre in ("ejemplos.json", "lote_01.json", "lote_02.json"):
        ruta = SEEDS_DIR / nombre
        if ruta.exists():
            for s in json.loads(ruta.read_text(encoding="utf-8")):
                semillas[s["id"]] = s
    return semillas


def revisar_variante(variante: dict, semilla: dict | None, vistos: set) -> tuple[str, str]:
    """Devuelve (estado, razon). estado es 'ok', 'sospechosa' o 'descartada'."""
    texto = variante.get("texto_dialectal", "")
    traduccion = variante.get("traduccion", "")
    n_palabras = len(texto.split())

    if n_palabras < LONGITUD_MIN_PALABRAS:
        return "descartada", f"muy corta ({n_palabras} palabras, mínimo {LONGITUD_MIN_PALABRAS})"
    if n_palabras > LONGITUD_MAX_PALABRAS:
        return "descartada", f"muy larga ({n_palabras} palabras, máximo {LONGITUD_MAX_PALABRAS})"

    if semilla is not None:
        ratio = difflib.SequenceMatcher(
            None, normalizar(semilla["texto_original"]), normalizar(texto)
        ).ratio()
        if ratio >= UMBRAL_SIMILITUD_SEMILLA:
            return "descartada", f"casi idéntica a la semilla original (similitud {ratio:.2f})"

    clave = normalizar(texto)
    if clave in vistos:
        return "descartada", "duplicada exacta dentro del dataset"

    en_en_texto, _ = contar_stopwords(texto, EN_STOP)
    es_en_texto, _ = contar_stopwords(texto, ES_STOP)
    if en_en_texto >= 2 and en_en_texto > es_en_texto:
        return "sospechosa", "texto_dialectal parece estar en inglés, no en español"

    es_en_traduccion, _ = contar_stopwords(traduccion, ES_STOP)
    en_en_traduccion, _ = contar_stopwords(traduccion, EN_STOP)
    if es_en_traduccion >= 2 and es_en_traduccion > en_en_traduccion:
        return "sospechosa", "traduccion parece estar en español, no en inglés"

    return "ok", ""


def main() -> int:
    dataset_path = Path(sys.argv[1]) if len(sys.argv) > 1 else GENERATION_DIR / "dataset_generador1.json"
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    semillas = cargar_semillas()

    limpio = []
    vistos = set()
    descartadas = []
    sospechosas = []

    for variante in dataset:
        semilla = semillas.get(variante.get("seed_id"))
        estado, razon = revisar_variante(variante, semilla, vistos)

        if estado == "descartada":
            descartadas.append((variante, razon))
            continue

        vistos.add(normalizar(variante["texto_dialectal"]))
        if estado == "sospechosa":
            sospechosas.append((variante, razon))
            variante = {**variante, "sospechosa": True, "razon_sospecha": razon}
        limpio.append(variante)

    total = len(dataset)
    n_descartadas = len(descartadas)
    porcentaje_descartado = (n_descartadas / total * 100) if total else 0.0

    razones = Counter(razon.split(" (")[0] for _, razon in descartadas)

    out_path = GENERATION_DIR / f"{dataset_path.stem}_limpio.json"
    reporte_path = GENERATION_DIR / "reporte_filtrado.md"

    alerta = porcentaje_descartado > DESCARTE_MAX_PORC

    if not alerta:
        out_path.write_text(json.dumps(limpio, ensure_ascii=False, indent=2), encoding="utf-8")

    lineas = [
        "# Reporte de filtrado automático",
        "",
        f"Dataset de entrada: `{dataset_path.name}` ({total} variantes)",
        "",
        f"- **Aprobadas (incluidas en el dataset limpio):** {len(limpio)} ({100 - porcentaje_descartado - (len(sospechosas)/total*100 if total else 0):.1f}% del total sin contar sospechosas por separado)",
        f"- **Marcadas como sospechosas (se quedan en el dataset limpio, revisar a mano):** {len(sospechosas)}",
        f"- **Descartadas:** {n_descartadas} ({porcentaje_descartado:.1f}% del total)",
        "",
        "## Razones de descarte",
        "",
    ]
    if razones:
        for razon, cuenta in razones.most_common():
            lineas.append(f"- {razon}: {cuenta}")
    else:
        lineas.append("- (ninguna variante fue descartada)")

    lineas += ["", "## Razones de sospecha", ""]
    razones_sospecha = Counter(razon.split(",")[0] for _, razon in sospechosas)
    if razones_sospecha:
        for razon, cuenta in razones_sospecha.most_common():
            lineas.append(f"- {razon}: {cuenta}")
    else:
        lineas.append("- (ninguna variante fue marcada como sospechosa)")

    lineas += ["", "## Ejemplos descartados", ""]
    for variante, razon in descartadas[:10]:
        lineas.append(f"- `{variante.get('seed_id')}` ({razon}): \"{variante.get('texto_dialectal')}\"")

    lineas += ["", "## Ejemplos sospechosos", ""]
    for variante, razon in sospechosas[:10]:
        lineas.append(f"- `{variante.get('seed_id')}` ({razon}): \"{variante.get('texto_dialectal')}\" -> \"{variante.get('traduccion')}\"")

    if alerta:
        lineas += [
            "",
            "## ALERTA",
            "",
            f"El descarte ({porcentaje_descartado:.1f}%) supera el límite de "
            f"{DESCARTE_MAX_PORC}% definido como criterio de calidad. **No se "
            f"escribió `{out_path.name}`** — esto puede significar que la "
            "plantilla de derivación necesita ajustes. Revisar antes de "
            "aplicar el filtro final.",
        ]

    reporte_path.write_text("\n".join(lineas) + "\n", encoding="utf-8")

    print(f"Total: {total} | aprobadas: {len(limpio) - len(sospechosas)} | sospechosas: {len(sospechosas)} | descartadas: {n_descartadas} ({porcentaje_descartado:.1f}%)")
    print(f"Reporte: {reporte_path}")
    if alerta:
        print(f"ALERTA: descarte > {DESCARTE_MAX_PORC}%, no se escribió {out_path.name}")
        return 1
    print(f"Dataset limpio: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
