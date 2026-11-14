# Guion de la sustentación final

**Tiempo asignado: 5 minutos** (syllabus, "Final Delivery": *5-minute committee
defense*). Re-armado para caber en 5:00 exactos en 5 bloques — la versión
anterior estaba pensada para ~10 minutos y ya no aplica.

Figuras (generadas por `python evaluation/figuras_sustentacion.py`, en `docs/figuras/`):
`1_resultados_modelos.png`, `2_costo_vs_calidad.png`, `3_errores_cualitativos.png`.
No hay presentación en PowerPoint: las figuras se pegan en las diapositivas del equipo.

| # | Bloque | Tiempo | Quién (sugerido) | Material | Prescindible |
|---|---|---|---|---|---|
| 1 | Problema y qué construimos | 0:30 | Paula | 1 ejemplo de jerga mal traducida (el caso de Willie Ramírez cabe aquí si da el tiempo) | No |
| 2 | Cómo se hizo: 3 generadores sintéticos, LoRA, fusión | 1:00 | Paula / Anderson | Diagrama del pipeline (Figura 1 del paper) | Parcial |
| 3 | Resultado clave: fusionar iguala o supera a reentrenar, y mucho más barato | 1:00 | Mariana | Figura 1 (`1_resultados_modelos.png`) | No |
| 4 | Demo en vivo del Space + Plan B | 1:30 | Anderson | URL del Space; video Plan B | No |
| 5 | Limitaciones honestas, costo (\$0) y trabajo futuro | 1:00 | Todos | Figura 3 + lista corta | No |

**Total: 5:00.** Si algo se extiende, el primer bloque que se recorta es el 2
(ir directo a "tres LLM generan datos, un modelo pequeño se ajusta y se
fusiona", sin detallar cada paso); el único bloque que nunca se corta es la
demo (4) — es la evidencia de que el prototipo funciona de verdad, no solo
en el paper.

Lo que YA NO entra en el guion oral, pero el comité puede preguntar y hay
que tener la respuesta lista (ver `docs/banco_preguntas_final.md` y el
one-pager, `docs/one_pager_ejecutivo.md`): el detalle de costo y métricas de
negocio, y la discusión de implicaciones éticas/organizacionales/filosóficas
(Sección 10 del paper) — si nadie pregunta por eso directo, se puede mencionar
en 1 frase al cerrar el bloque 5 ("y más allá de lo técnico, el paper discute
a quién puede afectar esto si falla y quién debería ser responsable").

## Mensajes clave (todo con su fuente)

1. **El ajuste ayuda.** Base 37.0 BLEU / 53.9 chrF; los modelos ajustados 42-44 / 57-58
   (`evaluation/comparacion_completa_pi2.md`). Mejora frente al base; entre los ajustados
   los intervalos se solapan (ver figura 1).
2. **Fusionar adaptadores fue al menos tan bueno como reentrenar con todos los datos,
   y mucho más barato** (13 s a ~20 min frente a 52 min), sin contar el entrenamiento
   previo de los tres adaptadores (~57 min). Pero **las técnicas de fusión no se
   distinguen entre sí** (43.7-44.2 BLEU) y la destilación (95 min) no aportó una
   mejora distinguible.
3. **Un error propio que enseñó algo**: promediar con pesos 1.0 en vez de 1/3 daba 35.3
   BLEU; normalizado, 43.6 (`merging/analisis_lineal_peft.md`). Buena respuesta si
   preguntan por errores propios o por el rol del ingeniero de sistemas.
4. **Qué falla**: expresiones polisémicas regionales ("mosca", "pedo", "mala leche");
   casi un tercio de los peores casos son traducciones aceptables que la métrica castiga
   (`evaluation/analisis_cualitativo.md`; clasificación de un solo lector).
5. **Portabilidad**: 14.8 MB de adaptador sobre un base compartido de 6.17 GB; funciona sin
   red; en CPU 46-65 s (28 s con int8, prueba de 3 frases), en GPU ~2 s
   (`evaluation/pi3_portabilidad.md`).
6. **Costo: \$0, todo con capas gratuitas** (`docs/one_pager_ejecutivo.md`,
   Sección 6.2 del paper).

## Qué NO decir

- No decir que "la fusión es mejor que X": decir "no se distingue" salvo donde el
  intervalo excluye 0.
- No decir que PI1 está respondida: **no hay evaluación humana todavía**. Decirlo como
  limitación principal, con el diseño ciego ya listo (`docs/evaluacion_humana_pi1.md`).
- No hablar de generalización a otros dialectos: 9 semillas de prueba.
- No decir que el sistema está "listo para producción" o "listo para decidir solo" en
  un contexto de salud o justicia: la posición del equipo (Sección 10 del paper) es que
  necesita supervisión humana en esos casos, no que los reemplaza.

## Demo (Bloque 4)

Seguir `docs/guion_demo_fase2.md` (Space público, ~2.5 s). **No gastar la cuota de GPU
del Space antes**; tener el video del Plan B (pendiente de grabar) por si la cuota se agotó.
Frase de prueba: "Che, estoy remando con el sueldo que me dan."

## Antes de la sustentación (acciones humanas)

- [x] ~~Averiguar el tiempo asignado~~ — 5 minutos (syllabus).
- [ ] Ensayo cronometrado completo con los 5 bloques y llenar tiempos reales.
- [ ] Grabar el video del Plan B.
- [ ] Armar las diapositivas con las 3 figuras (o pedirme un .pptx: hay que instalar `python-pptx`).
- [ ] Cada integrante responde sin leer al menos una pregunta de `docs/banco_preguntas_final.md`,
      incluida al menos una de la nueva sección de implicaciones éticas/organizacionales/filosóficas.
