# Diapositivas 11 a 14: guion de 6 minutos y banco de preguntas

Para exponer las diapositivas 11 a 14 del deck (*Evaluación técnica y arquitectónica*, *Lo que dicen los números*, *Métricas de negocio*, *Para cerrar*). Tiempo asignado: **6 minutos + 2 de holgura** para todo el grupo. Las cifras salen de `paper/main.tex` y de los archivos de `evaluation/`, `docs/` y `merging/` citados en cada respuesta.

## 0. Antes de ensayar: cuatro ajustes a las diapositivas

Revisé el texto de las 14 diapositivas contra el repositorio. Todo cuadra salvo esto; conviene corregirlo o, al menos, decirlo bien en voz alta:

1. **Diapositiva 13, "Sin datos expuestos: ninguna solicitud se guarda ni sale a la nube de un tercero".** Es cierto del código (`api/main.py` nunca escribe el texto a disco ni a un log) y de una instalación propia de la organización. **No es cierto del demo público**, que corre en Hugging Face, un tercero. Dilo así: "si la organización lo corre en su infraestructura, el texto no sale; el demo público corre en Hugging Face". Igual en "Sin terceros en producción".
2. **Diapositiva 12, "Fusión (el modelo final) 44.2 / 58.4".** Esos números son de la fusión con `mergekit`. El servicio desplegado usa el adaptador `peft_cat_norm` (la misma fusión simple hecha con PEFT), que dio 43.5-43.6 de BLEU y 58.1-58.2 de chrF. Son equivalentes (la diferencia no se distingue), pero si te preguntan "¿ese es el modelo que está en el Space?", la respuesta exacta es: "es la misma fusión simple; el desplegado es la versión con PEFT, 43.6".
3. **Diapositiva 9 (no es tuya, pero avísale a quien la presente): "Probado con hasta 50 solicitudes a la vez".** En la prueba real al Space, con 50 concurrentes solo se atendieron 33 (de 75 intentadas en total se atendieron 53), porque se agotó la cuota gratuita de GPU, no por fallo del código (`docs/pruebas_carga.md`). Decir "hasta 50" sin eso puede sonar a que las 50 funcionaron.
4. **Diapositiva 12, 47 % / 24 % / 29 %.** Es la clasificación de **una sola persona**, de los 34 casos peor puntuados (`evaluation/analisis_cualitativo.md`). Dilo en voz alta: te quita un punto de ataque fácil.

## 1. Guion (≈ 6:00)

Habla a ~140 palabras por minuto; el guion está escrito para eso. Los tiempos son objetivo: si vas atrasada, recorta lo marcado como *(recortable)*.

### Diapositiva 11: Cuatro capas, cada una verificada (1:20)

> Paso a la evaluación técnica y de arquitectura. Diseñamos el sistema en **cuatro capas**, y de cada una puedo decir qué tiene y cómo lo comprobamos.
>
> **Empresarial:** quién lo usaría y por qué lo preferiría a Google Translate o DeepL. **Datos:** 100 expresiones de semilla, tres generadores, validación automática, y un reparto por semilla —no por frase— para que ninguna expresión de prueba aparezca en el entrenamiento. **Aplicación:** una API REST con FastAPI: traducir, salud, métricas y retroalimentación. **Tecnología:** Qwen2.5 de 3 mil millones de parámetros con LoRA, y todo el cómputo pesado en Colab gratis.
>
> Y lo que más quiero destacar es la tabla de abajo, por una palabra: **verificado**. *(Señala la tabla.)* Latencia: 2.5 segundos con GPU en el servicio público. Seguridad: el límite es de 10 solicitudes por minuto por cliente, y lo probamos con carga concurrente real: pasan exactamente 10 y el resto recibe un error 429. Privacidad: el servicio nunca guarda el texto; lo comprobamos con una prueba automática que manda un texto marcador y confirma que no aparece en las métricas ni en los logs. Y disponibilidad: si algo falla por dentro, responde un error genérico y nunca expone el detalle interno.

*Transición:* "Eso es cómo está construido. Ahora, ¿qué tan bien traduce?"

### Diapositiva 12: Lo que dicen los números, y lo que no (1:50)

> Medimos con dos métricas, **BLEU y chrF**, que comparan la traducción del modelo con una de referencia: más alto, más parecido. El modelo base sin ajustar saca **37.0** de BLEU; el mejor modelo individual, **42.3**; y la fusión, **44.2**. O sea: ajustar ayuda, y fusionar es al menos tan bueno como el mejor individual y como reentrenar con todo junto, pero la diferencia entre ellos es pequeña.
>
> Y aquí está la advertencia, que además está en la diapositiva: son **174 frases, pero salen de solo 9 expresiones**. Es una muestra chica, así que hablamos de **señales, no de certezas**.
>
> Abajo, ¿qué falla exactamente? Revisamos a mano los 34 casos peor puntuados. **47 %** son errores reales de significado: por ejemplo, el modelo traduce "estar mosca", que es estar alerta, como estar molesto. **24 %** conservan el sentido pero pierden el matiz. Y el dato que más nos importó: **29 %, casi un tercio, eran traducciones válidas** que la métrica castigó por usar otras palabras. Por eso BLEU y chrF no bastan y falta evaluación humana, que sigue pendiente. Esta clasificación la hizo una sola persona, así que es preliminar.

*(Opcional, 40 s: demo en vivo aquí, ver sección 2. Si lo haces, recorta el segundo párrafo.)*

*Transición:* "Con eso vemos si traduce bien. Pero a quien decide, además, le importa otra cosa."

### Diapositiva 13: Métricas de negocio (1:20)

> Cambio de pregunta: no si traduce bien, sino **si vale la pena adoptarlo**. Costo: **cero**; todo el proyecto se hizo con capas gratuitas. Tiempo: un adaptador se entrena en **18 a 20 minutos** de GPU, y fusionar los tres toma de segundos a unos 20 minutos. Personalizar para un cliente nuevo mueve **15 megas**, no 6 gigas, porque solo se cambia el adaptador. Y sobre los datos: el código nunca guarda las solicitudes, y si una organización lo corre en su propia infraestructura, el texto no sale a un tercero, ni necesita internet una vez descargados los pesos. *(El demo público sí corre en Hugging Face, que es un tercero; lo aclaro para no sobreprometer.)*
>
> Frente a DeepL: **44.2 contra 44.4** de BLEU, empatados, y un poco por debajo en chrF. O sea que no ganamos en calidad; el argumento es privacidad, personalización y costo. Y por honestidad: esto **no es un caso de negocio completo**, porque no tenemos un cliente real con quien calcular volumen ni ingresos.

### Diapositiva 14: Para cerrar (1:10)

> Cierro con tres preguntas que van más allá de si traduce bien. **Ética:** un modelo que falla sin avisar que está inseguro puede ser peor que no tener traductor, porque da una falsa sensación de certeza; nosotros no medimos la incertidumbre de cada traducción, y eso es una limitación ética, no solo técnica. **Organizacional:** ¿quién firma usar esto en una conversación que puede terminar en una sala de urgencias o en una corte? Nuestra posición: **asiste a una persona, no decide sola.** **Filosófica:** el modelo no aprendió de hablantes reales, sino de variantes que otra IA generó a partir de 100 semillas humanas; es una aproximación, no acceso directo a un fenómeno humano, y por eso la evaluación humana importa tanto.
>
> Y la idea final: automatizar no quita la necesidad de que alguien entienda lo suficiente del sistema para notar que algo salió mal y corregirlo. Ese sigue siendo nuestro trabajo. Gracias; quedamos atentos a sus preguntas.

**Total: 1:20 + 1:50 + 1:20 + 1:10 = 5:40**, con ~20 s de colchón. Si haces la demo (+0:40) quedas en ~6:20: recorta la segunda mitad del párrafo de limitaciones de la diapositiva 12 o la frase de Hugging Face de la 13.

## 2. Mostrar el proyecto funcionando (opcional, 40 s)

Lo natural es dentro de la diapositiva 12, justo antes de "qué falla": una frase que funciona y una que falla, para que el comité vea los dos lados.

1. Abre **antes de empezar** la pestaña `https://andry891-traductor-jerga-dialectal.hf.space` (ya cargada).
2. Frase que funciona (ya probada): *"Che, estoy remando con el sueldo que me dan."* → "Hey, I'm struggling to make ends meet with the salary they give me."
3. Frase que puede fallar: una con "mosca" o "mala leche", por ejemplo *"Estoy mosca con ese tipo, no me gusta su actitud."* **Pruébala hoy una sola vez para saber qué sale con el modelo desplegado**: con la fusión de `mergekit` salió "I'm fed up with that guy", y la referencia es "I'm on my guard". No asumas el resultado.
4. **Cuidado con la cuota de GPU gratuita:** no hagas más de 1-2 pruebas hoy, y no repitas pruebas de carga. Primera solicitud tras un rato dormido puede tardar más.
5. **Plan B:** grabar hoy un video corto de una traducción real y tenerlo listo por si la cuota se agota o falla la red.

## 3. Banco de preguntas (con respuesta lista)

Responde corto y con la fuente. Si no se sabe, di "eso no lo medimos". Está ordenado por diapositiva y al final hay preguntas del tipo "¿por qué esto y no lo otro?".

### Arquitectura (diapositiva 11)

**¿Por qué cuatro capas?**
> Separan decisiones: qué problema de negocio se resuelve, con qué datos, con qué servicio y con qué tecnología. Cada capa se puede cambiar sin rehacer las demás. Es el marco de arquitectura empresarial del curso. (Paper, Sección 6.)

**¿Cómo verificaron el límite de 10 solicitudes por minuto?**
> Con una prueba de carga concurrente real: 5, 20 y 50 solicitudes al mismo tiempo. Pasaron exactamente 10 por ventana de 60 s y el resto recibió 429 con `Retry-After`, sin excepciones sin controlar. (`docs/pruebas_carga.md`.) Ojo: esa prueba fue contra la API local, no contra el Space.

**¿Cómo verificaron que no se guarda el texto?**
> Una prueba automática manda un texto marcador y comprueba que no aparece en `/metricas` ni en ningún log. Además, el código no tiene ninguna llamada de escritura de texto de solicitudes (`api/main.py`). Lo que no controlamos es lo que registre la infraestructura de Hugging Face en el demo público.

**¿Por qué FastAPI?**
> Es ligero, valida entradas con tipos y genera documentación automática; encaja con un servicio de un solo modelo. No hay una razón profunda más allá de ser el estándar práctico en Python para esto.

**¿Qué pasa si el modelo falla en medio de una solicitud?**
> Responde un 500 con un mensaje genérico y el servicio sigue funcionando; nunca se expone el traceback. Lo verificamos simulando el fallo. (Paper, Tabla de escenarios.)

**¿Esto escala a muchos usuarios?**
> No con lo que hay desplegado: el Space usa una GPU gratuita compartida con cuota diaria. En la prueba de 50 concurrentes se atendieron 33 y el resto falló por cuota, no por el código. La capa de API sí soportó 50 concurrentes sin errores cuando se aisló del modelo. Para producción haría falta una GPU dedicada o un contenedor propio.

**¿Qué tan rápido es?**
> 2.5 s por traducción en el Space con GPU; 46-65 s en una CPU sin GPU sin cuantizar; ~28 s con cuantización int8 en CPU (prueba de 3 frases). (`evaluation/pi3_portabilidad.md`.)

**¿Y cuando el Space está dormido?**
> La primera solicitud tarda más porque hay que despertar el servicio. No medimos esa cifra con rigor; no la inventamos.

**¿Por qué LoRA y no entrenar el modelo completo?**
> Porque solo teníamos GPUs gratuitas de Colab (T4), donde entrenar los 3 mil millones de parámetros completos no cabe. LoRA entrena solo 3.69 millones (0.12 %), cada adaptador pesa ~15 MB y se pueden fusionar y cambiar por cliente. Entrenamos con r=8 y alpha=16.

**¿Por qué Qwen2.5-3B y no Llama, o uno más grande?**
> Llama 3.2 pedía aprobación manual de Meta y no llegó a tiempo; Qwen2.5-3B ya estaba entre los candidatos de la Fase 1 y cabe en una T4. Uno más grande habría mejorado probablemente la calidad, pero no cabría en el cómputo gratuito. No probamos otro modelo base, y lo declaramos como limitación.

**¿Por qué un modelo pequeño y no usar la API de GPT o Gemini directamente?**
> Por privacidad (el texto no sale), por poder correr sin internet, por costo por llamada y por poder personalizarlo por cliente. Los LLM grandes traducen mejor (3-4 puntos de BLEU por encima en nuestra prueba); el argumento no es calidad, es control.

**¿Por qué Colab para todo el cómputo?**
> Ninguna máquina del equipo tiene GPU usable: un solo paso de entrenamiento tardó 80-95 minutos en CPU y a las 10 horas solo se había hecho el 5 % de una prueba. Colab gratuito (T4) lo hace en 18-20 minutos.

### Métricas y resultados (diapositiva 12)

**¿Qué son BLEU y chrF?**
> Comparan la traducción del modelo con una de referencia, de 0 a 100. BLEU cuenta coincidencias de palabras y frases cortas; chrF, de letras, así que perdona más las variaciones pequeñas. Miden parecido con la referencia, no si la traducción es buena.

**¿Por qué usar dos?**
> Se complementan: BLEU es estricta con palabras exactas y chrF tolera cambios de forma. Si las dos coinciden en una conclusión, es más confiable.

**¿Cómo midieron? ¿Contra qué?**
> Un test común de 174 frases de 9 expresiones, el mismo para todos los modelos, con las mismas métricas (sacrebleu). Las 9 expresiones nunca se usaron para entrenar: el reparto es por semilla, no por frase.

**¿Por qué el reparto es por semilla y no por frase?**
> Para evitar fuga de datos: si una expresión tuviera variantes en entrenamiento y otras en prueba, el modelo la habría visto y el resultado se inflaría.

**¿Es significativa la diferencia entre 42.3 y 44.2?**
> Apenas: el intervalo de confianza de 95 % por *bootstrap* sobre semillas apenas excluye el cero en BLEU y no se distingue en chrF. Por eso decimos "al menos igual", no "claramente mejor".

**¿Qué es el intervalo de confianza?**
> El rango donde razonablemente cae la diferencia real si hubiéramos elegido otras 9 expresiones. Si incluye 0, no podemos decir quién es mejor.

**¿Por qué solo 9 expresiones de prueba?**
> Porque el banco es de 100 semillas y repartimos 81 entrenamiento, 10 validación y 9 prueba. Es la mayor limitación estadística del proyecto; ampliarla requiere más semillas verificadas por humanos.

**¿Las referencias son confiables?**
> No del todo: 165 de las 174 las escribió un LLM; solo 9 son humanas. Por eso la evaluación humana es necesaria.

**¿Qué errores comete exactamente?**
> Confunde expresiones polisémicas regionales ("mosca", "pedo", "mala leche", "coger la caña") con su sentido estándar o con una expresión inglesa parecida. De los 34 peores casos: 47 % error de significado, 24 % pierden matiz, 29 % aceptables mal puntuadas. (`evaluation/analisis_cualitativo.md`; un solo lector.)

**¿Qué hacen con esos errores?**
> Hoy los documentamos. Como siguiente paso, con más datos dirigidos a esas expresiones y evaluación con hablantes nativos, se podría seguir afinando el modelo; no está hecho.

**¿Qué es la fusión de modelos y por qué funciona?**
> Se combinan los pesos de los adaptadores de los tres generadores en uno solo, en vez de reentrenar con todos los datos. Promediar los parámetros mezcla lo aprendido de cada fuente. Que funcione con estos datos es un resultado empírico; no investigamos a fondo por qué.

**¿Qué técnica de fusión usaron y por qué?**
> Probamos cuatro (promedio simple, TIES, DARE+TIES y destilación) y quedaron en 43.7-44.2 BLEU, sin diferencias distinguibles. Elegimos el promedio simple porque es el más barato y el más fácil de explicar.

**¿Cuál es la diferencia entre fusionar y entrenar con todos los datos juntos?**
> Entrenar con la mezcla tomó unos 52 minutos y dio 42.4 BLEU; fusionar toma de segundos a ~20 minutos y dio hasta 44.2. Ojo: la fusión parte de tres adaptadores que ya costaron ~57 minutos de entrenamiento.

**¿Qué fue el error del 35.3?**
> Al principio promediamos con los pesos por defecto de PEFT, que **suman** en vez de promediar, y el resultado quedó por debajo del modelo base (35.3). Pensamos que era por unos "términos cruzados", lo investigamos y resultó ser un error nuestro de configuración. Con los pesos normalizados dio 43.6. (`merging/analisis_lineal_peft.md`.)

**¿Por qué la destilación no ayudó?**
> Los "maestros" eran nuestros propios adaptadores, tan débiles como el estudiante, y costó 95 minutos. No mejoró frente a la fusión simple: −0.6 BLEU, intervalo que incluye 0.

**¿Hay sobreajuste?**
> Sí tiende a haberlo: en todos los entrenamientos la mejor época fue la primera y después empeora la validación; la parada temprana conserva siempre la primera.

**¿Y la cuantización?**
> La medimos con bitsandbytes en GPU: 8 bits pierde 0.9 BLEU (6.17 → 3.40 GB); 4 bits (nf4) pierde 1.6 BLEU y ocupa 2.01 GB. Dato contraintuitivo: int8 resultó más lento que fp16. (`evaluation/pi3_cuantizacion_calidad.md`.)

### Negocio (diapositiva 13)

**¿Es realmente cero costo?**
> Cero en dinero (capas gratuitas). No cuenta el tiempo del equipo (5-8 horas semanales por persona) ni los límites de cuota. Para operar a escala habría costos de GPU o servidor.

**Si queda empatado con DeepL, ¿por qué alguien lo usaría?**
> No por calidad, sino por privacidad (puede correr dentro de la infraestructura del cliente), por poder funcionar sin internet, por personalizarlo con 15 MB por cliente y por poder auditar qué datos lo entrenaron. DeepL queda mejor en chrF.

**¿Cuál es el modelo de negocio, cuántos clientes, cuántos ingresos?**
> No lo sabemos: no hay un cliente real con quien calibrar volumen ni ingresos, y no vamos a inventar una proyección. Lo que presentamos es evidencia medida de los diferenciadores técnicos.

**¿Se puede usar comercialmente? ¿Y la licencia?**
> **Riesgo real que no verificamos del todo:** el modelo base Qwen2.5-3B parece estar bajo la *Qwen Research License*, que podría limitar el uso comercial. Antes de afirmar uso comercial habría que revisar el archivo LICENSE del repositorio oficial o pedir licencia a Alibaba. Tampoco revisamos formalmente los términos de uso de las APIs que generaron los datos (Groq, Cohere, Google).

**¿Quién mantiene esto? La jerga cambia.**
> Es un punto válido: un modelo entrenado hoy con 100 semillas envejece desde el día del despliegue. Adoptarlo exige reentrenar y revalidar periódicamente; con adaptadores de 15 MB, es barato hacerlo.

**¿Por qué dicen "sin datos expuestos" si el demo corre en Hugging Face?**
> Porque hablamos del diseño: el código no guarda el texto, y una organización puede correrlo en su propia infraestructura. El demo público sí corre en Hugging Face, que es un tercero; no controlamos sus registros.

**¿Y los 20 minutos para "un modelo útil"?**
> Es el tiempo de GPU de un adaptador individual en una T4 de Colab (18-20 min). No incluye preparar las semillas ni generar los datos.

### Ética y cierre (diapositiva 14)

**¿Qué pasa si el modelo se equivoca en un hospital o una corte?**
> Por eso nuestra posición es que asiste a una persona y no decide sola: debe haber un humano en el circuito en cualquier contexto de alto riesgo. Además, hoy el modelo no comunica su propia incertidumbre por traducción, y eso es una limitación ética que declaramos.

**¿Por qué no miden la incertidumbre por traducción?**
> No estaba en el alcance y requiere un diseño propio (por ejemplo, calibración de probabilidades o varias muestras). Queda como trabajo futuro.

**¿Los datos tienen sesgos o estereotipos?**
> Posiblemente: las variantes las generó un LLM, y no hubo revisión por nativos más allá de las 9 referencias humanas. Además cubrimos solo 5 dialectos.

**¿Cómo manejan el contenido ofensivo?**
> No hay filtro: el modelo traduce jerga vulgar sin advertir. Lo declaramos como limitación y como política pendiente.

**¿El banco de semillas se hizo con consentimiento de hablantes?**
> Es jerga auténtica curada con el conocimiento del equipo, no un corpus recolectado con consentimiento explícito de hablantes pagados. Su trazabilidad se detiene en nosotros. (Paper, Sección 10.)

**¿El modelo "entiende" la jerga?**
> No lo afirmamos. Aprendió de variantes sintéticas que otro LLM generó y se evaluó, mayormente, contra referencias que otro LLM escribió: es una aproximación a un fenómeno humano. Por eso falta la evaluación humana.

**¿Qué sería lo primero que harían con más tiempo?**
> La evaluación humana con hablantes nativos (3 por dialecto), ampliar el test de 9 expresiones, repetir entrenamientos para medir la variación y probar traductores comerciales adicionales.

### Preguntas de "¿por qué esto y no lo otro?"

**¿Por qué tres generadores y no uno?**
> Para poder responder PI1 (¿importa qué modelo genera los datos?). Si usábamos uno solo, no habría con qué comparar. Son de familias distintas (Groq/gpt-oss, Cohere, Google).

**¿Por qué datos sintéticos y no reales?**
> No existe un conjunto grande de jerga latinoamericana con traducción al inglés (buscamos). Escribir uno a mano exigiría muchos hablantes. Partimos de 100 semillas humanas y las expandimos con LLM.

**¿Por qué no usar un diccionario de jerga o recuperación de definiciones (RAG)?**
> Es una alternativa razonable y complementaria, y podría reducir errores en las expresiones conocidas, pero no la probamos. Nuestro objetivo de investigación era el ajuste fino y la fusión.

**¿Por qué solo español→inglés?**
> Por alcance de la Fase 1. El sentido inverso exigiría otros datos y otra evaluación.

**¿Por qué no un modelo más grande como GPT-4?**
> Por costo, privacidad y portabilidad. Los grandes traducen mejor, pero el punto del proyecto es qué se puede lograr con un modelo pequeño y gratuito, y la fusión permite combinar fuentes sin reentrenar.

**¿Qué los diferencia de Google Translate o DeepL?**
> En calidad, DeepL queda empatado en BLEU y algo mejor en chrF; Google Translate no lo medimos (exige cuenta de facturación). La diferencia es el control: privacidad, offline, personalización y auditabilidad.

**¿Por qué creen que las métricas automáticas no bastan?**
> Porque miden parecido con una referencia: casi un tercio de los "errores" que revisamos eran traducciones válidas con otras palabras.

**¿Qué cambiarían si empezaran de nuevo?**
> Conseguiríamos antes los evaluadores nativos y más semillas de prueba, y revisaríamos desde el inicio las licencias del modelo base y de los datos.

## 4. Números para tener a mano

| Dato | Valor | Fuente |
|---|---|---|
| Base / mejor individual / fusión | 37.0 / 42.3 / 44.2 BLEU; 53.9 / 57.9 / 58.4 chrF | `evaluation/comparacion_completa_pi2.md` |
| Fusión desplegada (PEFT, `peft_cat_norm`) | 43.5-43.6 BLEU; 58.1-58.2 chrF | `evaluation/pi3_cuantizacion_calidad.md` |
| Test común | 174 frases, 9 expresiones; 165 referencias de un LLM, 9 humanas | `evaluation/test_comun.json` |
| Semillas | 100 (81 entrenamiento, 10 validación, 9 prueba) | `seeds/split_semillas.json` |
| Variantes generadas | 589 (Groq), 632 (Cohere), 625 (Google) | `generation/` |
| Adaptador / modelo base | 14.8 MB / 6.17 GB | `evaluation/pi3_portabilidad.md` |
| Entrenamiento | 18-20 min por adaptador, ~52 min la mezcla (T4) | `finetuning/curva_final_*.md` |
| Fusionar | de 13 s a ~20 min; destilación 95 min | `docs/fase3_costos_y_futuro_borrador.md` |
| Error del promedio | 35.3 sumando; 43.6 promediando | `merging/analisis_lineal_peft.md` |
| DeepL | 44.4 BLEU / 61.4 chrF | `evaluation/comparacion_pi3_comerciales.md` |
| LLM grandes | 48.0 y 47.7 BLEU (120B y 27B) | `docs/resultados_pi3.md` |
| Cuantización | fp16 43.6 / int8 42.7 / nf4 42.1 BLEU; 6.17 / 3.40 / 2.01 GB | `evaluation/pi3_cuantizacion_calidad.md` |
| Latencia | 2.5 s Space; 46-65 s CPU; ~28 s CPU int8 (3 frases) | `evaluation/pi3_portabilidad.md` |
| Límite de tasa | 10 solicitudes / 60 s por cliente | `docs/pruebas_carga.md` |
| Errores (34 peores) | 47 % significado / 24 % matiz / 29 % aceptables | `evaluation/analisis_cualitativo.md` |
| Costo | $0 en dinero | `docs/fase3_costos_y_futuro_borrador.md` |
