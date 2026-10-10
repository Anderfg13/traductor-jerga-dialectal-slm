# Banco de preguntas — sustentación final (Fase 3)

Complementa `docs/banco_preguntas_fase2.md` (preguntas de datos, despliegue y
Fase 2, que siguen vigentes). Mismas reglas: decir lo que los datos sostienen y
nada más; "no lo medimos" es una respuesta válida. Cada respuesta cita la fuente.

**Tiempo asignado a la sustentación:** NO CONOCIDO (anotarlo aquí cuando se sepa).
**Ensayo cronometrado:** pendiente (humano).

## Resultados y fusión

**"¿La fusión es mejor que el mejor modelo individual?"**
> En BLEU la fusión simple (44.2) queda unos 2 puntos por encima del mejor individual (42.3), con un intervalo que apenas excluye 0; en chrF no se distingue. Así que "al menos igual", no "mejor". (`evaluation/comparacion_completa_pi2.md`, sección 4.)

**"¿Y frente a entrenar con todos los datos juntos?"**
> Las fusiones superan a la mezcla en BLEU (+1.3 a +1.9) y, en chrF, solo la fusión simple lo hace con claridad. Fusionar costó de 13 s a ~20 min; reentrenar, ~52 min. Ojo: la fusión parte de tres adaptadores que ya costaron ~57 min.

**"¿Qué técnica de fusión recomiendan?"**
> Con estos datos no importa cuál: simple, TIES, DARE+TIES y destilación quedan en 43.7-44.2 BLEU sin diferencias distinguibles. Recomendamos la simple por ser la más barata. Lo que sí importa es promediar y no sumar (sumar dio 35.3).

**"La destilación costó 95 minutos, ¿valió la pena?"**
> No con esta evidencia: −0.6 BLEU [−2.5, +1.0] y −0.1 chrF frente a la fusión simple. Es un resultado negativo que dejamos reportado. (`merging/fusion_destilacion.md`.)

**"¿Por qué falló el promedio con PEFT al principio?"**
> Pensamos que eran términos cruzados; lo aislamos y era una configuración equivocada: se sumaban los adaptadores con pesos 1.0. Con pesos 1/3 da 43.6, igual que el promedio exacto (43.5) y que mergekit (44.2). Corregimos nuestra propia hipótesis. (`merging/analisis_lineal_peft.md`.)

**"¿Cuántos datos de prueba usaron? ¿Es significativo?"**
> 174 entradas de 9 semillas. Los intervalos (bootstrap por semilla) son amplios y hicimos muchas comparaciones sin corrección. Por eso solo afirmamos lo que los intervalos sostienen. Es la mayor limitación estadística.

## Evaluación humana (PI1)

**"¿El generador de datos importa?"**
> Con métricas automáticas hay una respuesta parcial (`evaluation/comparacion_pi1_automatica.md`). La evaluación humana ciega está diseñada y lista pero **no se ha ejecutado**: no hay evaluadores ni kappa. No tenemos respuesta completa a PI1. (`evaluation/analisis_pi1.md`.)

**"¿Por qué confiar en BLEU/chrF si las referencias son de otro LLM?"**
> No confiamos del todo: 165 de las 174 referencias son sintéticas y solo 9 son humanas. Además, el análisis cualitativo muestra que casi un tercio de los casos peor puntuados eran traducciones aceptables. Por eso la evaluación humana es necesaria.

**"¿Cómo evitan sesgos en la evaluación humana?"**
> Hojas por dialecto, traducciones A/B/C en orden aleatorio, traducciones idénticas unificadas, clave de modelos fuera del repositorio con hash SHA-256 publicado, y kappa de Fleiss/Cohen ponderado. (`docs/evaluacion_humana_pi1.md`.)

## Errores y limitaciones

**"¿Qué errores comete el modelo?"**
> Principalmente expresiones polisémicas regionales ("mosca", "pedo", "mala leche", "coger la caña"): elige el sentido estándar o una expresión inglesa parecida. De los 34 peores casos, ~47 % son errores de significado, ~24 % pierden matiz y ~29 % son aceptables. Clasificación de un solo lector, no nativo. (`evaluation/analisis_cualitativo.md`.)

**"¿Funciona igual para todos los dialectos?"**
> No lo sabemos: cada dialecto tiene 1-2 expresiones en el test, así que no se separa dialecto de expresión. Chilena tiene más frases bajas (26 %) pero es una sola expresión.

**"¿Qué pasa con contenido ofensivo o estereotipos?"**
> Parte de la jerga es vulgar y el modelo la traduce sin advertir; no hay filtro propio. Los datos son de LLM y podrían reproducir estereotipos. Es una limitación documentada. (`docs/fase3_limitaciones_borrador.md`.)

**"¿Qué errores propios cometieron?"**
> Corridas de Colab con un adaptador viejo (descartadas), la hipótesis de los términos cruzados, afirmar que la destilación superaba a la mezcla y decir que los adaptadores "memorizaban". Están en la bitácora con su corrección.

## Portabilidad, costos y comparaciones

**"¿Puede correr sin internet y en un computador normal?"**
> Sí sin internet (0 intentos de conexión con sockets bloqueados); en CPU tarda 46-65 s por traducción (28 s con int8, probado en 3 frases). Con GPU ~2 s. Necesita ~7 GB de RAM sin cuantizar. (`evaluation/pi3_portabilidad.md`.)

**"¿La cuantización mantiene la calidad?"**
> No lo medimos: solo 3 frases, sin comparación limpia. La medición completa va a Colab. Respuesta honesta: no sabemos.

**"¿Cómo se compara con un modelo grande o con Google Translate?"**
> Frente a LLMs grandes: significativamente por debajo de gpt-oss-120b y qwen3.8-27b (−3.4 a −3.9 BLEU), no distinguible de command-r y gemini-lite, por encima de gpt-oss-20b; con sesgo de circularidad. Google Translate/DeepL **no se comparó** (faltan claves). (`docs/resultados_pi3.md`.)

**"¿Cuánto costó?"**
> $0 en dinero. Tiempo de GPU en Colab T4: ~20/19/18 min por individual, ~52 min la mezcla, 13 s-20 min fusionar, 95 min destilar. (`docs/fase3_costos_y_futuro_borrador.md`.)

**"¿Qué harían con más tiempo?"**
> Evaluación humana nativa, más semillas de prueba, varias corridas por modelo, referencias humanas, traductores comerciales, cuantización de 4 bits.

## Para ensayar

- [ ] Cada integrante responde sin leer al menos una de estas preguntas.
- [ ] Cronometrar las respuestas: ninguna debería pasar de 45 s.
