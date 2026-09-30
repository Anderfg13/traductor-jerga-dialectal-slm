# Banco de preguntas — sustentación de Fase 2 (Sesión 36)

Preguntas que es razonable esperar del profesor, dado lo que la
retroalimentación de la Fase 1 ya mostró que revisa de cerca
(presupuesto, alcance, validación de datos, independencia del conjunto
de prueba), más los huecos reales que este mismo equipo documentó sin
esconder. Cada respuesta cita dónde está la evidencia — no hay que
memorizar cifras, solo saber dónde mirar.

## Sobre lo que ya está hecho

**"¿Por qué no usaron Llama 3.2, si era su candidato principal?"**
> El acceso a Llama 3.2 en HuggingFace requiere aprobación manual de
> Meta, y no se resolvió a tiempo. Usamos Qwen2.5-3B-Instruct, que ya
> estaba entre los candidatos declarados en la Fase 1 — no es un
> cambio de rumbo técnico, es un bloqueo externo. (`BITACORA.md`,
> Sesión 13; Sección de Arquitectura del paper.)

**"¿Cómo saben que el modelo mejoró y no que se sobreajustó a esos 8
ejemplos?"**
> Justo detectamos sobreajuste real durante el entrenamiento completo
> (la pérdida de validación subió desde la época 2) y el propio
> mecanismo de entrenamiento se detuvo ahí, quedándose con el mejor
> checkpoint de validación, no el último. La comparación de BLEU/chrF
> es sobre el conjunto de prueba, separado por semilla completa del
> conjunto de entrenamiento — ninguna variante de esas 8 semillas de
> prueba estuvo en entrenamiento. (`finetuning/curva_final_generador1.md`,
> Sección de Resultados del paper.)

**"¿Por qué Mexicana empeoró en BLEU si el modelo en general mejoró?"**
> Con solo 2 ejemplos de Mexicana en la muestra, es más probable que
> sea ruido estadístico que un efecto real — pero lo decimos así
> explícitamente en el paper en vez de ocultarlo o inventar una
> explicación sin evidencia. Es una pregunta abierta, no una que
> tengamos respondida todavía.

## Sobre lo que falta o está bloqueado

**"¿Por qué no está desplegado el servicio si ya tienen el código?"**
> Porque Hugging Face exige que la cuenta usada tenga más de 30 días
> de antigüedad para la excepción gratuita de GPU (ZeroGPU), y la
> nuestra la cumple hasta el 2 de octubre. Confirmamos que es
> exactamente esa la causa (no falta técnica) probando en la pantalla
> real de creación del Space. El código y la documentación de
> despliegue ya están listos y probados localmente, solo falta ese
> requisito de tiempo. (`docs/despliegue.md`, `BITACORA.md` Sesión 26.)

**"¿Dónde está la evaluación humana que mencionan en las métricas de
calidad de la Fase 1?"**
> Todavía no existe una ronda real — preparamos toda la
> infraestructura (rúbrica, formulario de reclutamiento, hoja de
> seguimiento) pero reclutar hablantes nativos reales de 5 dialectos
> distintos toma tiempo que no hemos tenido todavía. Preferimos decir
> "no disponible" en el paper en vez de presentar un piloto interno
> del equipo como si fuera evaluación humana real. (Sección de
> Resultados del paper, `evaluation/rubrica_humana.md`.)

**"¿Por qué el BLEU/chrF solo cubre 8 de 23 ejemplos del conjunto de
prueba?"**
> Porque son los únicos para los que ya generamos predicción tanto del
> modelo sin ajustar como del ajustado. Completar el resto es solo
> inferencia (mucho más barato que entrenar), pero igual requiere
> cargar el modelo de 3B, y seguimos la misma política de hacer eso en
> GPU/Colab, no en la máquina local. Es un paso pendiente concreto, no
> una limitación permanente.

**"¿Qué tan seria es la latencia de 50-80 segundos?"**
> Es el hallazgo más importante de esta fase en cuanto a lo que falta:
> confirma que el cuello de botella es la falta de GPU, no el diseño
> del servicio (la capa de API en sí responde en milisegundos, y
> aguanta 50 solicitudes concurrentes sin errores cuando la traducción
> en sí es rápida). Por eso el despliegue con GPU real es la prioridad
> inmediata, no una mejora opcional.

## Sobre el alcance y la honestidad metodológica

**"¿Por qué solo un generador y ninguna fusión todavía, si el proyecto
se llama justo así?"**
> Decisión de alcance explícita desde la Fase 1: construir y probar el
> pipeline completo de punta a punta con una sola fuente antes de
> triplicar el trabajo con 3 generadores y 2 técnicas de fusión. Está
> declarado así desde el principio, no es un recorte de último
> momento por falta de tiempo.

**"Encontraron mezcla de dialecto en los datos generados — ¿por qué no
lo arreglaron?"**
> Lo encontramos en un muestreo piloto de validación (un marcador
> rioplatense "che" en una variante etiquetada como andina) y lo
> dejamos documentado como limitación conocida de los filtros
> automáticos actuales, que no detectan ese tipo de error. Es
> exactamente el tipo de hallazgo que la validación de datos está
> pensada para sacar a la luz — que lo hayamos encontrado y
> documentado es la validación funcionando, no fallando.

## Ensayo (acción del equipo, no simulable)

1. Cada integrante repasa las preguntas de su propia área (datos,
   entrenamiento, infraestructura) en voz alta, sin leer.
2. Un ensayo completo de la sustentación con cronómetro, incluyendo el
   guion de demo (`docs/guion_demo_fase2.md`).
3. Si alguien no sabe responder algo en el ensayo, esa pregunta se
   agrega a este banco antes del día real, no se ignora.
