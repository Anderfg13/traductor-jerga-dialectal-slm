# Estado del proyecto y qué falta (para leer primero)

Última actualización: 2026-10-10. Escrito para que cualquiera del equipo (Paula, Mariana, Anderson) pueda ponerse al día en 10 minutos sin leer toda la bitácora. El detalle y los comandos están en `docs/hoja_de_ruta_fin_proyecto.md`; esta hoja es el resumen.

## 1. Qué es el proyecto, en tres líneas

Un traductor de jerga y dialectos latinoamericanos del español al inglés. Se ajusta un modelo pequeño (Qwen2.5-3B + LoRA) con datos sintéticos de tres LLM (Groq, Cohere, Google), se fusionan los tres modelos resultantes y se despliega el servicio en Hugging Face. Preguntas de investigación: **PI1** ¿importa qué LLM genera los datos? **PI2** ¿fusionar los modelos iguala o supera al mejor individual y a entrenar con todo junto? **PI3** ¿el modelo pequeño es portable y competitivo?

## 2. Qué ya está hecho

- Los tres datasets sintéticos, los cuatro adaptadores (3 individuales + mezcla), todas las fusiones (PEFT, mergekit, TIES/DARE) y la destilación, todos evaluados sobre el mismo test común (174 entradas, 9 semillas).
- Servicio desplegado y probado (`docs/despliegue.md`); pruebas, contenedor y observabilidad de la Fase 2.
- El paper compila (`paper/main.tex`, 20 páginas) con resultados, limitaciones, costos y trabajo futuro.
- Borradores, guion de sustentación, banco de preguntas y figuras (`docs/fase3_*_borrador.md`, `docs/guion_sustentacion_final.md`, `docs/banco_preguntas_final.md`, `docs/figuras/`).
- Comparaciones de PI3: contra LLM grandes, contra DeepL y un juez automático exploratorio (`evaluation/`).

## 3. Resultados en cinco líneas (BLEU / chrF, test común)

| Modelo | BLEU | chrF |
|---|---|---|
| Base sin ajustar | 37.0 | 53.9 |
| Mejor individual (Generador 3) | 42.3 | 57.9 |
| Entrenar con la mezcla | 42.4 | 57.2 |
| Fusión simple (mergekit) | 44.2 | 58.4 |
| Destilación | 43.9 | 58.3 |

- Ajustar ayuda; entre los ajustados (incluida la fusión) casi no hay diferencias distinguibles: son solo 9 semillas de prueba.
- Fusionar es mucho más barato que reentrenar y rinde igual o algo mejor; la técnica de fusión importa poco, pero hay que promediar, no sumar (sumar dio 35.3).
- DeepL queda empatado en BLEU (44.4) y algo arriba en chrF (61.4). Los LLM grandes (120B y 27B) quedan ~3.5 BLEU por encima del modelo pequeño.
- **Cuidado al presentar:** no hay evaluación humana todavía, la mayoría de las referencias las escribió un LLM, y el test es de 9 expresiones. Estas cautelas son parte de los resultados.

## 4. Qué falta, en orden de importancia

### A. Evaluación humana (lo que más bloquea PI1)
Sin esto no hay kappa ni respuesta completa a PI1.
1. Conseguir **3 evaluadores nativos por dialecto** (Caribeña, Andina, Rioplatense, Mexicana, Chilena = 15) y anotarlos en `evaluation/evaluadores.csv` con un ID (E1, E2...), no con nombre.
2. Calibrar la rúbrica entre dos del equipo (5 ejemplos; `evaluation/rubrica_humana.md`).
3. Mandar a cada evaluador **solo** su hoja (`evaluation/evaluacion_humana/hojas/<Dialecto>.csv`) con el texto de `evaluation/mensaje_evaluadores_pi1.md`. **No compartir el repositorio ni la clave.**
4. **Guardar `evaluation/evaluacion_humana/clave_modelos.json` en un lugar seguro** (no está en git; si se pierde, la ronda no se puede interpretar).
5. Guardar las hojas devueltas en `evaluation/evaluacion_humana/respuestas/<Dialecto>__<ID>.csv` y avisar. Desde ahí, el análisis (kappa, puntaje por modelo, actualización del paper) lo corre quien tenga a Claude: ver `docs/hoja_de_ruta_fin_proyecto.md`, tabla "Cuando me pases X, yo hago Y".

### B. Revisión del paper y los borradores
- Que Mariana y Paula revisen Resultados y Conclusiones de `paper/main.tex` (se reescribieron; reemplazan lo integrado en la Sesión 35) y confirmen que los borradores `docs/fase3_*_borrador.md` **no exageran ni minimizan** (esa confirmación es humana).
- Que alguien que no lo haya visto lo lea completo y anote referencias rotas o partes confusas.

### C. Sustentación
- Averiguar el tiempo asignado y anotarlo en `docs/banco_preguntas_final.md` y `docs/guion_sustentacion_final.md`.
- Ensayo cronometrado con las tres personas y la demo en vivo; cada integrante responde sin leer al menos una pregunta del banco.
- Grabar el video del Plan B (30–40 s de una solicitud real al Space).
- **No gastar la cuota de GPU del Space antes de la demo.**

### D. Una corrida de Colab pendiente
- Abrir `merging/cuantizacion_colab.ipynb` con GPU T4 y correrlo entero (~20 min); pasar el `resultados_cuantizacion.zip` que descarga. Mide cuánta calidad se pierde al cuantizar el modelo a 8 y 4 bits.

### E. Entrega
- Confirmar la numeración de sesiones de `BITACORA.md` (la "Sesión 48" de Mariana choca con las de Anderson; varios números se pusieron por inferencia).
- Decidir si se hace el merge o PR de `develop` a `main` (no se ha hecho).
- Opcional: Google Translate (pide cuenta de facturación; se descartó), token de HF para cambiar la duración de `@spaces.GPU` en el Space.

## 5. Extras (después de cerrar lo anterior)

- **Seguir afinando el modelo fusionado** y medir contra la fusión simple: plan en `docs/extra_finetuning_continuo.md`. Probablemente haga falta **datos nuevos**: no existe un dataset listo de jerga latinoamericana con inglés (búsqueda hecha, resumida en ese archivo).
- **Semillas nuevas** (`seeds/lote_03.json`, ids `sem-101` en adelante): checkpoint pendiente. Idea: buscar candidatas en fuentes públicas (sin copiar publicaciones de redes sociales), el equipo las aprueba o corrige, y un tercio se reserva como segundo conjunto de prueba, que resolvería la mayor limitación estadística.
- Destilar con LLM grandes (gpt-oss-120b, qwen3.8-27b) como maestros: descrito en la conversación, aún no en un documento.

## 6. Reglas del repositorio que hay que respetar

- Commits en formato Conventional Commits (`feat:`, `fix:`, `docs:`). **No agregar coautoría de Claude** en este repo.
- Todo commit que toque archivos del proyecto necesita una entrada real en `BITACORA.md` (el hook de `.githooks/` lo exige: `git config core.hooksPath .githooks` una vez por clon).
- Cómputo pesado (entrenar, fusionar con mergekit, evaluar todo el test) siempre en **Google Colab**, nunca en las máquinas locales.
- Las claves van solo en `.env` (nunca en git ni en el chat). Plantilla: `.env.example`.
- No inventar resultados: lo que no se corrió se deja como "No disponible" o pendiente.

## 7. Dónde está cada cosa

| Quiero... | Mirar |
|---|---|
| Entender la estructura | `README.md` |
| La lista completa de pendientes con comandos | `docs/hoja_de_ruta_fin_proyecto.md` |
| Las cifras y su fuente | `evaluation/comparacion_completa_pi2.md`, `docs/resultados_fase3.md`, `docs/resultados_pi3.md` |
| Los errores del modelo con ejemplos | `evaluation/analisis_cualitativo.md` |
| Limitaciones, riesgos y costos | `docs/fase3_limitaciones_borrador.md`, `docs/fase3_costos_y_futuro_borrador.md` |
| Qué se hizo y cuándo | `BITACORA.md` |
| El paper | `paper/main.tex` y `paper/main.pdf` |
