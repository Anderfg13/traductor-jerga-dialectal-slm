# Comparación de los tres generadores sintéticos

Mismas 100 semillas (`seeds/lote_01` + `lote_02`), misma plantilla de prompt, mismo filtro (`generation/validar.py`). Generado por `generation/comparar_generadores.py`.

| | G1: Groq (gpt-oss-20b) | G2: Cohere (command-r) | G3: Google (gemini-3.5-flash-lite) |
|---|---|---|---|
| Variantes generadas (crudo) | 589 | 632 | 625 |
| Variantes tras el filtro | 587 | 632 | 625 |
| Descartadas por el filtro | 2 (0.3 %) | 0 (0.0 %) | 0 (0.0 %) |
| Variantes por semilla (prom., mín-máx) | 5.9 (5-7) | 6.3 (6-7) | 6.2 (6-7) |
| Palabras por texto dialectal (prom.) | 14.0 | 12.9 | 15.0 |
| Palabras por traducción (prom.) | 13.2 | 13.3 | 15.5 |
| Registro `formal` | 12 % | 20 % | 7 % |
| Registro `informal` | 58 % | 61 % | 59 % |
| Registro `jerga` | 30 % | 19 % | 33 % |
| Textos repetidos entre semillas | 0 | 0 | 0 |
| 'che' en variantes no rioplatenses | 6 | 0 | 0 |
