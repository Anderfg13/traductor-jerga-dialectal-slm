# Guion de la sustentación final (borrador)

**Tiempo asignado: NO CONOCIDO.** Está armado para ~10 minutos en 6 bloques; si el
tiempo real es otro, se recorta por la columna "prescindible". Cuando se sepa, anotarlo
aquí y en `docs/banco_preguntas_final.md`.

Figuras (generadas por `python evaluation/figuras_sustentacion.py`, en `docs/figuras/`):
`1_resultados_modelos.png`, `2_costo_vs_calidad.png`, `3_errores_cualitativos.png`.
No hay presentación en PowerPoint: las figuras se pegan en las diapositivas del equipo.

| # | Bloque | Tiempo | Quién (sugerido) | Material | Prescindible |
|---|---|---|---|---|---|
| 1 | Problema y qué construimos | 1:00 | Paula | Diapositiva con 2-3 ejemplos de jerga mal traducida | No |
| 2 | Cómo se hizo: datos sintéticos de 3 LLM, LoRA, fusión | 2:00 | Paula / Anderson | Diagrama del pipeline (`docs/diagramas_arquitectura.md`) | Parcial |
| 3 | Resultado 1: fusionar iguala o supera a reentrenar | 2:00 | Mariana | Figura 1 | No |
| 4 | Resultado 2: costo, y qué dice (y no dice) | 1:30 | Mariana | Figura 2 | Sí |
| 5 | Demo en vivo del Space + Plan B | 1:30 | Anderson | URL del Space; video Plan B | No |
| 6 | Limitaciones honestas y trabajo futuro | 1:30 | Todos | Figura 3 + lista corta | No |

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
   BLEU; normalizado, 43.6 (`merging/analisis_lineal_peft.md`).
4. **Qué falla**: expresiones polisémicas regionales ("mosca", "pedo", "mala leche");
   casi un tercio de los peores casos son traducciones aceptables que la métrica castiga
   (`evaluation/analisis_cualitativo.md`; clasificación de un solo lector).
5. **Portabilidad**: 14.8 MB de adaptador sobre un base compartido de 6.17 GB; funciona sin
   red; en CPU 46-65 s (28 s con int8, prueba de 3 frases), en GPU ~2 s
   (`evaluation/pi3_portabilidad.md`).

## Qué NO decir

- No decir que "la fusión es mejor que X": decir "no se distingue" salvo donde el
  intervalo excluye 0.
- No decir que PI1 está respondida: **no hay evaluación humana todavía**. Decirlo como
  limitación principal, con el diseño ciego ya listo (`docs/evaluacion_humana_pi1.md`).
- No hablar de generalización a otros dialectos: 9 semillas de prueba.

## Demo (Bloque 5)

Seguir `docs/guion_demo_fase2.md` (Space público, ~2.5 s). **No gastar la cuota de GPU
del Space antes**; tener el video del Plan B (pendiente de grabar) por si la cuota se agotó.
Frase de prueba: "Che, estoy remando con el sueldo que me dan."

## Antes de la sustentación (acciones humanas)

- [ ] Averiguar el tiempo asignado y ajustar la columna "prescindible".
- [ ] Ensayo cronometrado completo y llenar tiempos reales.
- [ ] Grabar el video del Plan B.
- [ ] Armar las diapositivas con las 3 figuras (o pedirme un .pptx: hay que instalar `python-pptx`).
- [ ] Cada integrante responde sin leer al menos una pregunta de `docs/banco_preguntas_final.md`.
