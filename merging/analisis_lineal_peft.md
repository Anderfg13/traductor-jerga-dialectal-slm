# Aislar por qué el promedio simple con PEFT salió mal

Generado por `merging/analisis_lineal_peft.py` con los adaptadores reales de los generadores 1, 2 y 3 (`144` matrices objetivo; `s = alpha/r = 2`). **No requiere inferencia**: compara las actualizaciones de pesos.

## Qué compara

- **ideal** = promedio de las tres actualizaciones `(D1+D2+D3)/3` (lo que hace `mergekit` lineal, con normalización).
- **PEFT w=1** = lo que corrimos: pesos 1.0 por adaptador, sin normalizar. PEFT promedia por separado A y B, así que el producto es la suma de los 9 pares `B_i A_j`: 3 diagonales (la suma de las actualizaciones, o sea 3 veces el promedio) y 6 cruzados.
- **PEFT w=1/3** = el mismo método con pesos normalizados.

## Resultados (promedio sobre todas las matrices)

| Magnitud | Valor |
|---|---|
| Norma de PEFT w=1 / norma del ideal | **4.74** (si fuera exactamente la suma sin cruzados sería 3.00) |
| Coseno entre PEFT w=1 y el ideal | 0.635 |
| Energía de los 6 términos cruzados, relativa a la suma de las actualizaciones | 1.222 |
| Energía de los términos cruzados (con w=1/3), relativa al ideal | 1.222 |
| Error relativo de PEFT w=1/3 frente al ideal | 1.222 |
| Coseno entre PEFT w=1/3 y el ideal | 0.635 |
| Coseno entre las matrices A de dos adaptadores distintos | 0.000 |

## Por tipo de matriz

| Matriz | Escala PEFT w=1 / ideal | Coseno w=1 | Error relativo w=1/3 | Energía cruzada vs. ideal |
|---|---|---|---|---|
| k_proj | 4.83 | 0.622 | 1.261 | 1.261 |
| o_proj | 4.64 | 0.661 | 1.163 | 1.163 |
| q_proj | 4.83 | 0.611 | 1.276 | 1.276 |
| v_proj | 4.68 | 0.647 | 1.190 | 1.190 |
## Resultado posterior: qué causaba el fallo (experimento con inferencia)

Este análisis de pesos hacía sospechar de los términos cruzados (energía 1.22 veces la de la señal). El experimento `merging/aislar_lineal_peft_colab.ipynb` lo **refutó**: PEFT `linear` con pesos normalizados a 1/3 (conserva los cruzados) dio 43.6 BLEU / 58.1 chrF y PEFT `cat` con pesos 1/3 (promedio exacto, sin cruzados) 43.5 / 58.1, indistinguibles entre sí y +8.5 BLEU por encima del original con pesos 1.0. **La causa era la escala (sumar en vez de promediar)**, no los términos cruzados. Ver `merging/fusion_simple.md` y `evaluation/analisis_bootstrap_aislar_lineal.md`.

