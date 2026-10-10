# Borrador: resultados de PI1 y primera mitad de PI2 (para el paper)

> **Estado.** La mitad de PI2 está lista. La de PI1 tiene solo la parte automática;
> **la humana no existe** (no hay evaluadores). `paper/main.tex` ya trae versiones de
> estas secciones; este borrador parte de ellas y debe mantenerse alineado.
> Confirmar que la interpretación no exagera ni minimiza es una acción del equipo.
> Numeración de sesión por confirmar (hay conflicto con las entradas "48" de la bitácora).

## PI1 — ¿importa qué LLM generó los datos?

Fuente de todas las cifras: `evaluation/comparacion_pi1_automatica.md` y
`evaluation/analisis_bootstrap.md`. Mismo test común (174 entradas, 9 semillas).

| Modelo | BLEU | chrF |
|---|---|---|
| Base sin ajustar | 37.0 | 53.9 |
| LoRA Generador 1 (Groq) | 42.2 | 57.5 |
| LoRA Generador 2 (Cohere) | 40.7 | 55.3 |
| LoRA Generador 3 (Google lite) | 42.3 | 57.9 |

Redacción propuesta: ajustar con datos sintéticos mejora al base con cualquiera de los
tres generadores. Entre generadores, el de Cohere queda por debajo en chrF (G1 − G2:
+2.3 [+0.2, +4.2]; G3 − G2: +2.7 [+0.8, +5.3]), mientras G1 y G3 no se distinguen
(−0.5 [−2.4, +1.1]); en BLEU no se distingue ninguno. **Cautela**: 9 semillas de prueba,
cada generador sale favorecido con las referencias de su propio LLM, y con solo las 9
referencias humanas (n = 9) no se puede concluir nada. **Falta** la evaluación humana
ciega y el kappa (`evaluation/analisis_pi1.md`, sección humana "No disponible"): cuando
exista, este párrafo debe decir si coincide o contradice a las métricas.

## PI2 (primera mitad) — fusión simple

Fuente: `evaluation/comparacion_fusion_simple.md`, `evaluation/comparacion_completa_pi2.md`,
`merging/fusion_simple.md`, `merging/analisis_lineal_peft.md`.

| Modelo | BLEU | chrF |
|---|---|---|
| Mejor individual (G3) | 42.3 | 57.9 |
| Entrenar sobre la mezcla | 42.4 | 57.2 |
| Fusión simple, mergekit | 44.2 | 58.4 |
| Promedio PEFT, pesos 1/3 | 43.6 | 58.1 |
| Promedio exacto PEFT cat, 1/3 | 43.5 | 58.1 |
| Promedio PEFT con pesos 1.0 (suma) | 35.3 | 51.5 |

Redacción propuesta: la fusión simple iguala al mejor individual y a la mezcla; en BLEU
parece superarlos por 1.8-2 puntos, con un intervalo que apenas excluye 0. **Resultado
distinto a lo esperado, que debe decirse:** la fusión con PEFT falló al principio (35.3 BLEU);
atribuimos el fallo a términos cruzados, pero el aislamiento lo refutó: era sumar con pesos 1.0.
Normalizando, se recupera 43.6.
