# Banco de preguntas — sustentación de Fase 2 (Sesión 36, actualizado 2026-10-07)

Preguntas que es razonable esperar del profesor, dado lo que la
retroalimentación de la Fase 1 ya mostró que revisa de cerca
(presupuesto, alcance, validación de datos, independencia del conjunto
de prueba), más los huecos reales que este mismo equipo documentó sin
esconder. Cada respuesta cita dónde está la evidencia — no hay que
memorizar cifras, solo saber dónde mirar.

**Regla para todas las respuestas**: decir lo que los datos sostienen y
nada más. Si la respuesta honesta es "no lo medimos", se dice así. Una
respuesta que suena mejor que la evidencia es peor que "todavía no lo
sabemos".

Quién responde primero (sugerido, según quién hizo cada parte; se puede
cambiar): **Anderson** — despliegue, API, latencia, contenedor;
**Mariana** — métricas, evaluación, paper; **Paula** — datos, semillas,
generadores, evaluadores humanos.

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
> conjunto de entrenamiento — ninguna variante de esas semillas de
> prueba estuvo en entrenamiento. Aun así son 8 ejemplos: es una
> primera señal, no una conclusión. (`finetuning/curva_final_generador1.md`,
> Sección de Resultados del paper.)

**"¿Por qué Mexicana empeoró en BLEU si el modelo en general mejoró?"**
> Con solo 2 ejemplos de Mexicana en la muestra, es más probable que
> sea ruido estadístico que un efecto real — pero lo decimos así
> explícitamente en el paper en vez de ocultarlo o inventar una
> explicación sin evidencia. Es una pregunta abierta, no una que
> tengamos respondida todavía.

## Sobre el despliegue, el modelo y la latencia (nuevo en esta actualización)

**"¿Por qué eligieron Hugging Face Spaces para desplegar?"**
> Porque era la única opción gratuita que nos daba GPU real: ZeroGPU
> asigna una GPU solo durante cada generación, sin costo. Descartamos
> Render (la capa gratuita no tiene memoria suficiente para un modelo
> de 3B), Railway (sin capa gratuita permanente en 2026) y AWS Academy
> (la sesión se apaga sola a los 40 minutos y los créditos se comparten
> con el resto del curso). Hospedar con Docker en Spaces pasó a pedir un
> plan de pago, así que el Space usa Gradio, no FastAPI. **El costo de
> esa elección**: dependemos de un tercero y de su cuota gratuita (ver
> la pregunta de cuota más abajo). Es una plataforma para demostrar,
> no para operar con usuarios reales. (`docs/despliegue.md`,
> `BITACORA.md` Sesión 26.)

**"¿Por qué ese modelo en particular, un Qwen2.5 de 3B?"**
> Honestamente: no lo elegimos comparando candidatos entre sí. Nuestro
> candidato principal era Llama 3.2 3B, quedó bloqueado por el acceso
> manual de Meta, y Qwen2.5-3B-Instruct era el siguiente de la lista de
> la Fase 1 y se puede descargar sin trámite. Lo que sí sabemos es que
> cabe en una GPU gratuita de Colab para ajustarlo con LoRA y que, sin
> ajustar, ya traduce el español estándar razonablemente (esa es la
> línea base). **No medimos Gemma 2 2B ni Llama**, así que no podemos
> decir que Qwen sea el mejor candidato; solo que fue el que se pudo
> usar. Cambiar de modelo base es cambiar una constante (`MODEL_ID`) y
> reentrenar.

**"¿Es realista la latencia que midieron para un caso de uso real?"**
> Depende del caso de uso, y hay que separar tres números. Sin GPU, 50-80
> segundos por traducción: inservible para uso interactivo. Con GPU real
> en el Space público, **2.5 segundos para una solicitud individual**:
> aceptable para traducir una frase y leer el resultado, no para
> traducción simultánea en tiempo real. Y **bajo carga no lo sabemos**:
> con el modelo real solo pudimos medir hasta 5 solicitudes simultáneas
> (3 atendidas, 3.59 s de promedio) porque se acabó la cuota gratuita de
> GPU; con 20 y 50 todas fueron rechazadas. Además el límite de 80 tokens
> de salida (`max_new_tokens`) está pensado para frases cortas, no para
> párrafos. (`docs/pruebas_carga.md`, Resultado 3.)

**"¿Soportaría usuarios reales el servicio desplegado hoy?"**
> No. La cuota diaria de GPU gratuita para un cliente anónimo se agotó
> después de unas 4 traducciones, y el Space solo expone traducir y
> salud (no métricas ni retroalimentación, que están en la API
> contenerizada). El servicio no se cae al agotarse la cuota — rechaza
> con un mensaje claro —, pero para usuarios reales haría falta GPU
> propia o un plan de pago. (`docs/pruebas_carga.md`.)

**"¿Por qué no está desplegado el servicio si ya tienen el código?"**
> Sí lo está desde el 7 de octubre de 2026:
> https://andry891-traductor-jerga-dialectal.hf.space. Antes no
> podíamos porque Hugging Face exige 30 días de antigüedad en la cuenta
> para ZeroGPU gratis; esperamos en vez de usar la cuenta de otro
> integrante. El primer build falló al cargar el adaptador bajo ZeroGPU
> y lo corregimos cargándolo en CPU. Lo probamos desde un celular con
> datos móviles, no solo desde la máquina que desplegó. (`docs/despliegue.md`.)

**"Dicen que los datos no salen a una nube de terceros, pero lo desplegaron en Hugging Face."**
> Buena observación, y la distinción importa. Esa ventaja aplica al
> despliegue que controla el cliente (el contenedor Docker, en su
> propia máquina o servidor, sin internet constante). El Space público
> es una demostración alojada en un tercero: ahí las solicitudes sí
> pasan por infraestructura de Hugging Face. Nuestro código no guarda
> ni registra el texto (solo métricas agregadas), pero eso es lo que
> hace nuestro servicio, no lo que haga la plataforma que lo aloja, y
> no verificamos sus políticas. Tampoco medimos todavía que el sistema
> corra sin internet (queda en `docs/hoja_de_ruta_fin_proyecto.md`).

## Sobre lo que falta o está bloqueado

**"¿Dónde está la evaluación humana que mencionan en las métricas de
calidad de la Fase 1?"**
> Todavía no existe una ronda real. Está lista la parte técnica (rúbrica
> 1-5, hojas ciegas por dialecto, cálculo de kappa de Fleiss y Cohen
> verificado contra valores publicados), pero faltan los hablantes
> nativos: mínimo 3 por cada uno de los 5 dialectos. Preferimos decir
> "no disponible" en el paper en vez de presentar un piloto interno
> del equipo como si fuera evaluación humana real. (Sección de
> Resultados del paper, `evaluation/rubrica_humana.md`.)

**"¿Por qué el BLEU/chrF solo cubre 8 de 23 ejemplos del conjunto de
prueba?"**
> Porque son los únicos para los que ya generamos predicción tanto del
> modelo sin ajustar como del ajustado, en esa corrida. Desde entonces
> ampliamos el banco a 100 semillas y rehicimos el reparto, así que
> esas cifras ya no corresponden al conjunto de prueba actual: se
> reemplazan con las de la Fase 3, sobre un test común para todos los
> modelos. Falta correrlo en Colab. (`docs/fase2_resultados_borrador.md`.)

**"¿Qué tan seria es la latencia de 50-80 segundos?"**
> Era el hallazgo más importante de la Fase 2: confirmó que el cuello de
> botella era la falta de GPU y no el diseño del servicio (la capa de
> API responde en milisegundos y aguanta 50 solicitudes concurrentes
> sin errores cuando la traducción es rápida). Con GPU real en el Space
> bajó a 2.5 s por solicitud individual; lo que sigue sin medirse es el
> comportamiento bajo concurrencia con el modelo real.

## Sobre el alcance y la honestidad metodológica

**"¿Por qué el MVP solo cubre un generador y ninguna fusión, si el proyecto se llama justo así?"**
> Decisión de alcance explícita desde la Fase 1: probar el pipeline
> completo de punta a punta con una sola fuente antes de triplicar el
> trabajo. Y una precisión que conviene decir: no es "una técnica de
> fusión", es **ninguna ejecutada todavía**. Desde entonces generamos
> los datos de los generadores 2 y 3 y dejamos escritas y probadas las
> herramientas de fusión (TIES, DARE+TIES, lineal y destilación
> multi-maestro), pero no hemos entrenado ni fusionado ningún modelo
> nuevo, así que no tenemos ningún resultado de PI1 ni de PI2. La
> destilación en particular no se ha corrido nunca con el modelo real.

**"El Generador 3 cambió de modelo, ¿eso no invalida la comparación entre generadores?"**
> Cambió de `gemini-3.6-flash` a `gemini-3.5-flash-lite` porque el nivel
> gratuito del primero permite solo 20 solicitudes por día (100
> semillas habrían tomado 5 días). No la invalida, pero sí la
> condiciona: la versión "lite" es un modelo más pequeño, así que una
> diferencia entre generadores puede deberse a la capacidad del modelo y
> no solo a "qué LLM es". PI1 pregunta justo por el efecto del
> generador, pero con tres generadores no podemos separar esos factores.
> Lo dejamos como limitación en el paper. (`BITACORA.md`, Sesión extra 4.)

**"¿Por qué fusionan con PEFT y no con `mergekit` como propusieron?"**
> Los tres modelos son el mismo modelo base con un adaptador LoRA de la
> misma configuración, y PEFT aplica TIES/DARE directamente sobre los
> adaptadores. `mergekit` obliga a materializar tres modelos completos
> de 3B (unos 18 GB), justo en el límite de Colab gratis. Es una
> desviación del plan que documentamos; las técnicas son las mismas.

**"Encontraron mezcla de dialecto en los datos generados — ¿por qué no
lo arreglaron?"**
> Lo encontramos en un muestreo piloto de validación (un marcador
> rioplatense "che" en una variante etiquetada como andina) y lo
> dejamos documentado como limitación conocida de los filtros
> automáticos actuales, que no detectan ese tipo de error. Es
> exactamente el tipo de hallazgo que la validación de datos está
> pensada para sacar a la luz — que lo hayamos encontrado y
> documentado es la validación funcionando, no fallando.

## Ensayo cronometrado (acción del equipo, no simulable)

Tiempo asignado para la sustentación: ______ min (completar con el dato
del profesor). El guion de demo dura ~2:30 (`docs/guion_demo_fase2.md`).

| Intento | Fecha | Demo (mm:ss) | Preguntas (mm:ss) | Total | ¿Dentro del tiempo? | Qué falló |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |

Dinámica:
1. Ensayo completo con cronómetro y la demo en vivo (ver cuidado de
   cuota en el guion).
2. Quien dirige saca **a ciegas** una pregunta de este banco por
   persona, de las nuevas (despliegue/modelo/latencia/cuota/privacidad/
   generador 3/PEFT/alcance). Cada integrante responde **sin leerla**.
   Marcar abajo quién respondió bien (sin inventar cifras):

   - [ ] Anderson: pregunta ______
   - [ ] Mariana: pregunta ______
   - [ ] Paula: pregunta ______
3. Si alguien no sabe responder, esa pregunta se agrega aquí con la
   respuesta correcta antes del día real, no se ignora.
