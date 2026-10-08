"""
paper/auditar_tex.py

Revisión estática de main.tex antes de entregar: figuras/tablas con
\\caption y \\label, \\ref sin \\label, \\cite sin \\bibitem (y al revés) y
marcas de texto sin terminar. Complementa la compilación (que ya avisa
de referencias indefinidas) con lo que LaTeX no marca: p. ej. un
\\bibitem que nadie cita.

    python paper/auditar_tex.py
"""

import re
import sys
from pathlib import Path

s = Path(__file__).resolve().parent.joinpath("main.tex").read_text(encoding="utf-8")
problemas = []

for env in ("figure", "table"):
    for m in re.finditer(r"\\begin\{%s\*?\}(.*?)\\end\{%s\*?\}" % (env, env), s, re.S):
        cuerpo = m.group(1)
        titulo = (re.search(r"\\caption\{(.{0,50})", cuerpo) or [None, "(sin caption)"])[1]
        ok = "\\caption" in cuerpo and "\\label" in cuerpo
        print(f"{env:7} caption+label {'OK ' if ok else 'FALTA'} | {titulo}")
        if not ok:
            problemas.append(f"{env} sin caption o label: {titulo}")

labels = set(re.findall(r"\\label\{([^}]*)\}", s))
refs = set(re.findall(r"\\(?:ref|autoref|pageref|eqref)\{([^}]*)\}", s))
print("\n\\ref sin \\label:", sorted(refs - labels) or "ninguno")
print("\\label sin ningún \\ref:", sorted(labels - refs) or "ninguno")
problemas += [f"ref sin label: {x}" for x in sorted(refs - labels)]

citas = set()
for grupo in re.findall(r"\\cite\w*\{([^}]*)\}", s):
    citas |= {x.strip() for x in grupo.split(",")}
bibs = set(re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]*)\}", s))
print("\\cite sin \\bibitem:", sorted(citas - bibs) or "ninguno")
print("\\bibitem sin ningún \\cite:", sorted(bibs - citas) or "ninguno")
problemas += [f"cita sin bibitem: {x}" for x in sorted(citas - bibs)]

marcas = re.compile(r"TODO|XXX|FIXME|[Ll]orem|por completar|a completar|\[\.\.\.\]")
hallazgos = [(m.group(0), s[max(0, m.start() - 60) : m.end() + 60].replace("\n", " ")) for m in marcas.finditer(s)]
print("\nmarcas de texto sin terminar:", hallazgos or "ninguna")
problemas += [f"marca: {h[0]}" for h in hallazgos]

print("\nPROBLEMAS:", problemas or "ninguno")
sys.exit(1 if problemas else 0)
