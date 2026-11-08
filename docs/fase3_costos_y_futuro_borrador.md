# Costos y trabajo futuro (borrador para el paper)

Solo se incluyen cifras que están registradas en el repositorio. Lo que no se
midió se dice como tal.

## 1. Costos

**Dinero: $0.** Generación sintética con capas gratuitas (Groq, Cohere, Google),
entrenamiento y fusiones en Colab gratuito (T4), despliegue en un Space de Hugging
Face (`docs/presupuesto_tiempo_computo.md`).

**Tiempo de GPU (Colab, Tesla T4)**, de `finetuning/tiempos_fase3_corrida2.json`,
`merging/logs/*.json` y `finetuning/curva_final_*.md`:

| Paso | Tiempo |
|---|---|
| LoRA Generador 1 / 2 / 3 | ~20 / ~19 / ~18 min |
| LoRA sobre la mezcla de los tres datasets | ~52 min |
| Fusión de adaptadores con PEFT (lineal, DARE+TIES, TIES) | 13-24 s |
| Fusión con mergekit (incorporar adaptadores + fusionar) | 466 s + 739 s (lineal) / 1069 s (TIES) |
| Destilación multi-maestro | 5697 s (~95 min) |
| Predicciones sobre el test común (174 entradas) | ~5.6 min por modelo |

**Importante:** las fusiones y la destilación parten de los tres adaptadores individuales ya entrenados (~57 min de T4 en total); sus tiempos NO incluyen ese costo previo. Lectura: fusionar es de 2 a 3 órdenes de magnitud más barato que reentrenar con
la mezcla (13 s - 20 min frente a 52 min), y la destilación es la más cara (95 min)
sin una mejora distinguible sobre la fusión simple (`evaluation/comparacion_completa_pi2.md`).

**Costo de inferencia** (`evaluation/pi3_portabilidad.md`): ~1.9 s por traducción en
T4, ~2.5 s en el Space; en CPU sin cuantizar, 46-65 s.

**Tiempo humano:** 3 integrantes, 5-8 h semanales cada uno
(`docs/presupuesto_tiempo_computo.md`). No se registró el número de llamadas a las
APIs generadoras por separado; los datos resultantes son 589 (G1), 632 (G2) y 625
(G3) variantes (`generation/reporte_filtrado*.md`).

**Costo que no se pagó pero existe:** la evaluación humana nativa (15 evaluadores)
no se ha hecho; sería el mayor costo real en tiempo de coordinación.

## 2. Trabajo futuro

Ordenado por lo que más aumentaría la confianza en los resultados:

1. **Evaluación humana con nativos** (3 por dialecto): cerrar PI1 y validar las
   categorías de error de `evaluation/analisis_cualitativo.md`.
2. **Más semillas de prueba** (hoy 9): la mayor limitación estadística.
3. **Varias corridas por modelo** para medir la variabilidad del entrenamiento.
4. **Referencias humanas** en vez de sintéticas, al menos para un subconjunto
   mayor que las 9 "oro".
5. **Comparación con traductores comerciales** (Google Translate, DeepL), que
   requiere claves de API.
6. **Cuantización** para uso en CPU (`evaluation/pi3_portabilidad.md`) y, con GPU,
   4 bits.
7. **Ablación de la destilación** (pesos α, inicialización) y entender por qué los
   términos cruzados de PEFT no dañan el promedio.
8. **Más dialectos y expresiones**; política de contenido ofensivo y revisión de
   licencias de los datos sintéticos (`docs/fase3_limitaciones_borrador.md`).
9. Portar métricas y retroalimentación al Space.
