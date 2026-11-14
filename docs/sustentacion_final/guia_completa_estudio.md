# Guía completa del proyecto (para ti sola)

Esta es la versión "todo en un solo lugar", pensada para que puedas estudiar sin
tener que abrir quince archivos del repositorio. Está escrita en lenguaje simple,
pero sin recortar los números reales — todas las cifras salen de `paper/main.tex`
y de los archivos de `evaluation/` y `docs/` que ya existen en el repo, nada está
inventado para que suene mejor.

Está organizada así:
1. El problema, en una frase
2. Qué construyeron (el pipeline completo, explicado paso a paso)
3. Las 3 preguntas de investigación y sus respuestas reales
4. Glosario: cada palabra rara, explicada
5. Los resultados importantes, en español sencillo
6. Cómo funciona la demo en vivo
7. Lo que todavía no se sabe (límites honestos)
8. Banco de preguntas difíciles, con respuesta lista
9. Qué decir y qué NO decir
10. Estado actual del proyecto

---

## 1. El problema, en una frase

**Los traductores automáticos (Google Translate, DeepL, ChatGPT) funcionan bien
con el español "de libro", pero fallan con la jerga y los dialectos regionales**
— traducen literal y cambian o invierten el significado.

Ejemplo real y documentado (no inventado): en 1980, a un paciente en Florida le
tradujeron "intoxicado" como *intoxicated* (borracho) en vez de *poisoned*
(envenenado). Lo trataron por una sobredosis cuando en realidad tenía una
hemorragia cerebral. Quedó cuadripléjico. El hospital pagó 71 millones de
dólares de indemnización. Esto no es un caso aislado: hay estudios que muestran
que las expresiones dialectales son una fuente recurrente de errores "críticos"
(los que invierten el sentido) en traducción automática, incluso hoy.

**Lo que ustedes construyeron**: un traductor especializado en jerga y dialectos
del español (5 variantes: caribeña, andina, rioplatense, mexicana, chilena) al
inglés, usando un modelo de lenguaje **pequeño** (no uno gigante como GPT),
especializado con técnicas de ajuste fino baratas.

---

## 2. Qué construyeron: el pipeline completo, paso a paso

Piensa en esto como una línea de producción con 6 estaciones. Cada una depende
de la anterior.

### Estación 1 — Banco de semillas
100 expresiones reales de jerga/dialecto, curadas por el equipo, cada una con:
su traducción de referencia, su dialecto, su registro (formal/informal/jerga),
y una nota de contexto cultural. Es la "materia prima".

### Estación 2 — Generación sintética (3 generadores)
No existen bases de datos grandes de "jerga en español ↔ inglés" ya hechas, así
que el equipo le pidió a **tres modelos de lenguaje grandes distintos** que
tomaran cada semilla y la expandieran en 5-8 "variantes" (la misma expresión
usada en frases distintas, por gente distinta, en tonos distintos):

- **Generador 1 = Groq** (modelo `openai/gpt-oss-20b`)
- **Generador 2 = Cohere** (modelo `command-r-08-2024`)
- **Generador 3 = Google** (modelo `gemini-3.5-flash-lite`)

⚠️ **Punto de confusión frecuente**: "Generador" ≠ "el modelo que van a entrenar".
Los generadores son los que **fabrican los datos de entrenamiento** (son LLMs
grandes, usados solo para esto). El modelo que de verdad se entrena y se
despliega es uno **distinto y mucho más pequeño**: Qwen2.5-3B-Instruct.

Resultado: miles de frases de entrenamiento, una tanda por cada generador.

### Estación 3 — Ajuste fino con LoRA (4 modelos entrenados)
Se entrenó un modelo pequeño (**Qwen2.5-3B-Instruct**, de Alibaba, 3 mil
millones de parámetros) **cuatro veces**, cada vez con datos de una fuente
distinta:
- Uno con los datos del Generador 1
- Uno con los del Generador 2
- Uno con los del Generador 3
- Uno con la mezcla de los tres juntos

No se reentrenó el modelo completo (eso costaría muchísimo cómputo). Se usó
**LoRA** (*Low-Rank Adaptation*): el modelo base se queda congelado, intacto, y
solo se entrena un "parche" pequeñito (un *adaptador*) que se le suma encima.
Ese adaptador pesa **~15 MB**, frente a los **~6.17 GB** del modelo base — o
sea, el 0.24% del tamaño. Por eso cambiar de especialización es barato: no hay
que mover 6 GB, solo 15 MB.

### Estación 4 — Fusión de modelos (PI2)
Una vez que había 3 adaptadores individuales (uno por generador), la pregunta
era: ¿se puede combinar el conocimiento de los tres en **un solo modelo**, sin
tener que reentrenar desde cero con todos los datos juntos? Se probaron varias
técnicas:
- **TIES** y **DARE+TIES** (recortan y combinan los adaptadores con cuidado,
  resolviendo conflictos entre ellos)
- **Promedio simple** (promediar los tres adaptadores)
- Las mismas técnicas pero con una herramienta externa llamada **mergekit**,
  que en vez de combinar los "parches" pequeños, combina los **modelos
  completos ya fusionados** (6 GB cada uno)
- **Destilación multi-maestro**: en vez de promediar pesos, se entrena un
  modelo nuevo para que "imite" a los tres adaptadores a la vez

### Estación 5 — Cuantización (comprimir el modelo)
Para que el modelo ocupe menos espacio y corra más rápido en hardware modesto,
se probó **cuantizar** (reducir la precisión numérica de los pesos): de 16 bits
(normal) a 8 bits y a 4 bits. Es parecido a comprimir una foto: pierdes algo de
calidad, pero el archivo pesa mucho menos.

### Estación 6 — Despliegue (el servicio real)
Todo esto no se quedó en un script de laboratorio: se construyó un **servicio
real**, con una API (forma estándar en que un programa le habla a otro por
internet), seguridad básica, y lo subieron a un servidor público gratuito
(**Hugging Face Spaces**, con GPU gratis llamada **ZeroGPU**) para que cualquiera
pueda probarlo desde un navegador.

---

## 3. Las 3 preguntas de investigación — y sus respuestas reales

### PI1: ¿Importa qué LLM genera los datos de entrenamiento?

**Respuesta corta: señal débil de que sí, pero no está confirmada del todo.**

Los adaptadores del Generador 1 (Groq) y el Generador 3 (Google) salieron
prácticamente iguales entre sí. El del Generador 2 (Cohere) salió un poco peor
en una de las dos métricas (chrF), pero no en la otra (BLEU). Una hipótesis sin
confirmar: Cohere generó un tono más formal y menos jerga con el mismo prompt
(20% formal / 19% jerga, contra 12%/30% de Groq y 7%/33% de Google).

**Lo que falta para responder esto de verdad: la evaluación humana** (con
hablantes nativos reales calificando traducciones a ciegas). Eso todavía no se
ha hecho — es el pendiente más importante del proyecto ahora mismo.

### PI2: ¿Fusionar los modelos iguala o supera al mejor individual (y a
entrenar con todo junto)?

**Respuesta corta: sí, fusionar es al menos tan bueno, y mucho más barato.**

Todas las técnicas de fusión que funcionaron quedaron muy parecidas entre sí
(43.7 a 44.2 de BLEU — una métrica de calidad de traducción, más abajo se
explica). No hay una "ganadora" clara entre TIES, DARE+TIES, mergekit o
destilación — las diferencias entre ellas son tan chiquitas que podrían ser
ruido estadístico.

Lo que **sí** se puede afirmar con más confianza: fusionar los tres
adaptadores superó claramente al adaptador entrenado con **la mezcla completa**
de los tres datasets juntos — y fusionar toma segundos o minutos, mientras que
reentrenar con todo junto toma ~52 minutos de GPU.

**Un hallazgo honesto e interesante — el error que se convirtió en lección**:
al principio, promediar los adaptadores con PEFT dio un resultado **peor que
no haber ajustado nada** (35.3 de BLEU, contra 37.0 del modelo base). El equipo
pensó que el problema era técnico (algo llamado "términos cruzados"). Al
investigar a fondo, resultó ser un error de configuración propio: estaban
**sumando** los tres adaptadores (pesos de 1.0 cada uno) en vez de
**promediarlos** (pesos de 1/3 cada uno). Corregido eso, el resultado subió a
43.6 — en línea con las demás técnicas. Esto es un ejemplo real de cómo
funciona la ciencia: una hipótesis falló, se investigó, se encontró la causa
real, y se corrigió. Es bueno para contar en la sustentación, no hay que
ocultarlo.

**La destilación (la técnica más cara, ~95 minutos de GPU) no mejoró el
resultado** frente a TIES (que toma ~24 segundos). Con esta evidencia, no vale
la pena el costo extra.

### PI3: ¿El modelo pequeño es portable y competitivo frente a sistemas de
propósito general?

**Respuesta corta: portable, sí claramente. Competitivo, solo a medias.**

- **Portable**: sí. El adaptador pesa 15 MB. El sistema corre completamente
  sin internet una vez que los pesos ya están descargados (se verificó
  bloqueando literalmente todas las conexiones de red del proceso: cero
  intentos de conexión). En una computadora sin GPU tarda 46-65 segundos por
  traducción (lento, pero funciona); con una GPU, ~2 segundos.
- **Competitivo frente a LLMs grandes que NO ayudaron a generar los datos**
  (gpt-oss-120b, qwen3.8-27b): el modelo pequeño queda claramente **por
  debajo** (unos 3.5-4 puntos de BLEU menos). Pero recorre más de la mitad del
  camino entre el modelo base sin ajustar y esos modelos gigantes, usando una
  fracción de su tamaño.
- **Frente a DeepL** (un traductor comercial dedicado): el modelo pequeño
  queda prácticamente empatado en BLEU (44.2 vs 44.4) pero un poco por debajo
  en chrF (58.4 vs 61.4). Es decir: un modelo de 3B entrenado con datos
  sintéticos y gratis llega al nivel de un producto comercial, pero no lo
  supera.
- Google Translate **no se comparó** — no se usó porque pedía una cuenta de
  facturación, y el equipo decidió no incurrir en ese costo.

---

## 4. Glosario — cada palabra rara, explicada en una línea

- **LLM** (*Large Language Model*): un modelo de lenguaje grande, tipo
  ChatGPT/Gemini. Se usan aquí solo como "generadores de datos", no como el
  producto final.
- **SLM** (*Small Language Model*): un modelo de lenguaje pequeño. Es el que sí
  se entrena y se despliega (Qwen2.5-3B).
- **Qwen2.5-3B-Instruct**: el modelo base elegido. "Qwen" es la familia de
  modelos de Alibaba, "2.5" la versión, "3B" son 3 mil millones de parámetros,
  "Instruct" significa que ya viene afinado para seguir instrucciones (no es
  un modelo "en bruto"). Se eligió en vez de Llama 3.2 3B porque el acceso a
  Llama en HuggingFace necesita aprobación manual de Meta, que nunca llegó —
  no fue una decisión técnica, fue un bloqueo externo.
- **LoRA** (*Low-Rank Adaptation*): técnica de ajuste fino barata. En vez de
  reentrenar los miles de millones de parámetros del modelo, se congela el
  modelo entero y solo se entrena un "parche" pequeño encima.
- **Adaptador**: el "parche" que entrena LoRA. Es el archivo chiquito (~15 MB)
  que, sumado al modelo base, le da la especialización.
- **r (rango) y alpha**: dos números de configuración de LoRA. `r=8` controla
  qué tan "grande" es el parche (más grande = más capacidad, pero más pesado).
  `alpha` controla cuánto "peso" tiene ese parche sobre el resultado final; una
  regla práctica común es poner `alpha = 2×r`.
- **Fusión de modelos (*model merging*)**: combinar varios modelos/adaptadores
  ya entrenados en uno solo, sin tener que reentrenar desde cero.
- **TIES / DARE**: dos técnicas de fusión que, antes de combinar los
  adaptadores, limpian y resuelven conflictos entre ellos (en vez de solo
  promediar a lo bruto).
- **mergekit**: una herramienta externa que hace fusión, pero trabajando sobre
  modelos *completos* (6 GB) en vez de solo los adaptadores (15 MB).
- **Destilación**: en vez de combinar pesos directamente, se entrena un modelo
  nuevo para que aprenda a "imitar" lo que dicen varios modelos "maestros" a
  la vez.
- **Cuantización**: comprimir los números que forman el modelo (de 16 bits a 8
  u 4 bits) para que ocupe menos espacio y sea más rápido, a cambio de un
  poquito de calidad.
- **BLEU y chrF**: dos formas automáticas de medir "qué tan parecida" es una
  traducción a la traducción de referencia. BLEU compara palabras completas;
  chrF compara trocitos de letras (más tolerante a pequeñas variaciones de
  forma). Van de 0 a 100 aproximadamente, más alto = mejor. Ninguna de las dos
  mide si se conservó el *tono* o la *intención* — por eso hace falta
  evaluación humana además.
- **Intervalo de confianza (IC 95%)**: un rango de valores donde probablemente
  está el número real. Si el intervalo incluye el 0, significa "no podemos
  afirmar con confianza que hay una diferencia real" — aunque los promedios se
  vean distintos.
- **API**: la forma en que un programa le habla a otro por internet (en este
  caso, cómo tu navegador le pide al servicio que traduzca algo).
- **FastAPI / uvicorn**: FastAPI es el "lenguaje" en que está escrito el
  servicio (en Python); uvicorn es el programa que de verdad escucha en un
  puerto de red y recibe las solicitudes.
- **Hugging Face Spaces / ZeroGPU**: la plataforma gratuita donde está
  desplegado el servicio público. ZeroGPU es GPU real, gratis, que se asigna
  solo durante cada traducción (no está prendida todo el tiempo).

---

## 5. Los resultados importantes, en español sencillo

### Tabla principal (BLEU / chrF, sobre 174 frases de prueba, 9 expresiones
distintas)

| Modelo | BLEU | chrF | Qué significa |
|---|---|---|---|
| Base, sin ajustar | 37.0 | 53.9 | El Qwen2.5 "de fábrica", sin entrenar en jerga |
| Generador 1 (Groq) | 42.2 | 57.5 | Mejora clara sobre el base |
| Generador 2 (Cohere) | 40.7 | 55.3 | Mejora, pero un poco menos |
| Generador 3 (Google) | 42.3 | 57.9 | Mejora clara, el mejor individual |
| Mezcla de los tres | 42.4 | 57.2 | Entrenar con todo junto — parecido a los individuales |
| **Fusión simple (mergekit)** | **44.2** | **58.4** | La mejor fusión, el "modelo final" del proyecto |
| Fusión TIES | 43.7 | 58.2 | Muy parecida a la simple |
| Destilación | 43.9 | 58.3 | Cara (95 min) y no mejora a las demás |

**Cómo leer esto en una frase**: ajustar el modelo sí ayuda (sube de 37 a ~42),
fusionar ayuda un poquito más (sube a ~44), y entre las técnicas de fusión casi
no hay diferencia real.

### Los errores más comunes (análisis cualitativo)

Un integrante del equipo revisó a mano los 34 peores casos. Encontró:
- **47%** son errores de significado real: el modelo confunde una expresión
  regional con su sentido "estándar" (ej.: "mosca" como "alerta" en vez de su
  sentido regional, "pedo" como "borracho" sin el matiz correcto).
- **24%** conservan el sentido pero pierden el tono/matiz (ej.: "al tiro" lo
  traduce como "let's go" cuando debería ser algo más urgente como "right
  away").
- **29%** son en realidad traducciones aceptables que la métrica automática
  castigó solo porque usan palabras distintas a la referencia — es decir, casi
  un tercio de los "peores casos" no son errores de verdad.

Esto es importante: significa que BLEU/chrF por sí solos **subestiman** la
calidad real del modelo, y es otra razón de por qué hace falta evaluación
humana.

### La prueba de carga (¿aguanta muchos usuarios a la vez?)

Se probó mandarle 5, 20 y 50 solicitudes al mismo tiempo al servicio público.
Con 5, las 5 se atendieron bien. Con 20 y 50, solo una parte se atendió — pero
**no porque el sistema fallara**, sino porque la cuota gratis de GPU (5 minutos
al día) se agotó a mitad de la prueba. Lo importante: se confirmó que el
servicio atiende las solicitudes **en paralelo** (varias a la vez), no una por
una — si fuera uno por uno, atender 15 solicitudes habría tardado 45-60
segundos; en la prueba tardó solo 6.

---

## 6. Cómo funciona la demo en vivo

- URL pública: `https://andry891-traductor-jerga-dialectal.hf.space`
- Hoy en día sirve el **modelo fusionado** (el bueno, de los tres generadores
  combinados), no un modelo individual.
- Si nadie lo usa por un rato, "se duerme" (para ahorrar recursos gratis) y la
  primera solicitud después de eso tarda ~20 segundos extra en "despertarlo".
  Es normal, no es un error.
- La cuota de GPU gratis es muy limitada (minutos al día), así que **no se debe
  probar mucho el día de la sustentación** — practicar el flujo como máximo
  1-2 veces antes, y tener listo el plan B (un video grabado de una traducción
  real) por si la cuota se agota justo en el momento de presentar.
- Frase de ejemplo ya probada y que funciona bien: *"Che, estoy remando con el
  sueldo que me dan."* → *"Hey, I'm struggling to make ends meet with the
  salary they give me."*

---

## 7. Lo que todavía NO se sabe (límites honestos — decirlos es parte de
hacer buena ciencia, no un defecto)

- **No hay evaluación humana todavía.** Está todo diseñado y listo (rúbrica,
  hojas ciegas por dialecto, cálculo de acuerdo entre evaluadores), pero
  faltan evaluadores reales. Sin esto, PI1 no tiene respuesta completa.
- **El conjunto de prueba es chico**: solo 9 expresiones distintas (174 frases
  en total, porque cada expresión se usa en varias oraciones). Eso hace que los
  intervalos de confianza sean anchos.
- **Una sola corrida de cada modelo** — no se repitió el entrenamiento varias
  veces para ver cuánto varía por azar.
- **La mayoría de las referencias (165 de 174) las escribió un LLM**, no una
  persona — solo 9 son humanas, del banco de semillas original.
- **Un solo modelo base** probado (Qwen2.5-3B); no se sabe si otro modelo base
  daría resultados distintos.
- **No hay filtro de contenido ofensivo**: el modelo traduce jerga vulgar sin
  avisar, porque no se entrenó con eso como objetivo.
- **No se cubren todos los dialectos del español** — solo 5 (caribeña,
  andina, rioplatense, mexicana, chilena); el español peninsular y otras
  variantes caribeñas (Cuba, Puerto Rico) quedaron fuera a propósito, porque
  el equipo no tenía forma de conseguir evaluadores nativos de esas regiones.

---

## 8. Banco de preguntas difíciles — con respuesta ya lista

**"¿El generador de datos importa de verdad?"**
> Con las métricas automáticas hay una señal débil (Cohere salió un poco peor
> en una métrica, no en la otra). Pero la respuesta de verdad depende de la
> evaluación humana, que todavía no se hizo. Hoy no tenemos una respuesta
> completa a esa pregunta.

**"¿La fusión es mejor que el mejor modelo individual?"**
> En BLEU, la fusión simple (44.2) queda unos 2 puntos por encima del mejor
> individual (42.3), pero el intervalo de confianza apenas excluye el cero —
> o sea, "al menos igual de buena", no "claramente mejor". En chrF no hay
> diferencia que se pueda afirmar con confianza.

**"¿Qué técnica de fusión recomiendan?"**
> Con estos datos, no importa cuál: todas quedan muy parecidas (43.7 a 44.2
> BLEU). Recomendamos la más simple porque es la más barata. Lo que sí importa
> es hacerlo bien: promediar, no sumar (sumar sin querer dio un resultado peor
> que no entrenar nada).

**"La destilación tardó 95 minutos, ¿valió la pena?"**
> No, con esta evidencia: no mejoró frente a la fusión simple, que toma
> segundos. Es un resultado negativo honesto, y lo reportamos así.

**"¿Por qué falló el promedio al principio?"**
> Pensamos que era un problema técnico de PEFT (algo llamado "términos
> cruzados"). Al investigar, resultó ser un error nuestro: estábamos sumando
> los adaptadores en vez de promediarlos. Corregido, el resultado mejoró
> muchísimo (de 35.3 a 43.6 de BLEU).

**"¿Cuántos datos de prueba usaron? ¿Es suficiente?"**
> 174 frases, pero de solo 9 expresiones distintas. Es la limitación
> estadística más grande del proyecto — los intervalos de confianza son
> anchos porque la muestra es chica.

**"¿Por qué confiar en BLEU/chrF si las referencias las escribió un LLM?"**
> No confiamos del todo: 165 de 174 referencias son sintéticas. Además, el
> análisis mostró que casi un tercio de los "peores casos" eran en realidad
> traducciones aceptables mal puntuadas. Por eso insistimos en que hace falta
> evaluación humana.

**"¿Cómo evitan sesgos en la evaluación humana que van a hacer?"**
> Cada hoja es por dialecto, las traducciones se muestran en orden aleatorio
> (A/B/C) sin decir qué modelo las hizo, traducciones idénticas se unifican
> para no repetir, y la clave de qué modelo es cuál se guarda fuera del
> repositorio con un hash público para poder demostrar después que no se
> alteró.

**"¿Qué errores comete el modelo?"**
> Sobre todo confunde expresiones con doble sentido regional ("mosca", "pedo",
> "mala leche") con su sentido más común/estándar. Casi un tercio de los casos
> que parecían "errores" en realidad eran traducciones válidas mal puntuadas
> por la métrica.

**"¿Funciona igual para todos los dialectos?"**
> No lo sabemos con certeza: cada dialecto tiene solo 1-2 expresiones en el
> conjunto de prueba, así que no se puede separar "el dialecto es difícil" de
> "esa expresión en particular es difícil".

**"¿Qué pasa con contenido ofensivo?"**
> El modelo traduce jerga vulgar sin avisar — no tiene un filtro propio. Es
> una limitación que declaramos abiertamente, no la escondemos.

**"¿Puede correr sin internet, en una computadora normal?"**
> Sí, sin internet, una vez que ya se descargaron los pesos (verificado
> bloqueando literalmente la red). En una computadora sin GPU tarda 46-65
> segundos por traducción — lento, pero funciona. Necesita unos 7 GB de RAM
> libres.

**"¿La cuantización mantiene la calidad?"**
> Sí la medimos (no es un "no sabemos"): comprimir a 8 bits pierde menos de 1
> punto de BLEU, a 4 bits pierde 1.6 puntos, pero ocupa un tercio de la
> memoria. Es un compromiso razonable si hiciera falta correrlo en hardware
> más modesto.

**"¿Cómo se compara con un modelo grande o con traductores comerciales?"**
> Frente a LLMs grandes que no ayudaron a generar los datos: claramente por
> debajo (3-4 puntos de BLEU menos), pero recorre más de la mitad del camino
> entre el modelo base y esos gigantes. Frente a DeepL: prácticamente
> empatados en BLEU, un poco por debajo en chrF. Google Translate no se
> comparó (hubiera costado dinero).

**"¿Cuánto costó todo esto?"**
> $0 en dinero — todo con capas gratuitas. En tiempo de GPU (Google Colab,
> gratis): ~18-20 minutos por cada adaptador individual, ~52 minutos para la
> mezcla, de 13 segundos a 20 minutos para fusionar, ~95 minutos para
> destilar.

**"¿Está desplegado de verdad? ¿Funciona?"**
> Sí — servicio público real en Hugging Face Spaces, con GPU gratuita,
> sirviendo el modelo fusionado. Se probó en vivo con traducciones reales y
> con hasta 50 solicitudes simultáneas (limitado solo por la cuota diaria de
> GPU gratis, no por fallas del sistema).

**"¿Qué harían con más tiempo?"**
> Conseguir evaluadores humanos reales, ampliar el conjunto de prueba (hoy
> solo 9 expresiones), repetir entrenamientos para medir variación, conseguir
> más referencias humanas, comparar con más traductores comerciales, y probar
> cuantización a 4 bits con más detalle.

---

## 9. Qué decir y qué NO decir (muy importante)

**NO digas:**
- "La fusión es mejor que X" — di "no se distingue" salvo en los pocos casos
  donde el intervalo de confianza no incluye el cero.
- "Ya respondimos PI1" — **no es cierto todavía**, falta la evaluación humana.
  Dilo como la limitación principal, no la escondas.
- Nada que suene a "funciona igual de bien para todos los dialectos" — el
  conjunto de prueba es muy chico para afirmar eso.
- Que el modelo "no tiene errores" — sí los tiene, y está bien decir cuáles.

**SÍ di:**
- Los números con su intervalo cuando puedas ("44.2, pero el intervalo apenas
  excluye el cero").
- Las limitaciones como parte normal de hacer ciencia, no como algo vergonzoso.
- El error del promedio sin normalizar (35.3 → 43.6) — es una buena historia
  de cómo se investiga y se corrige un error propio.
- Que todo el proyecto costó $0 porque se usaron capas gratuitas de Groq,
  Cohere, Google, Colab y Hugging Face.

---

## 10. Estado actual del proyecto (a hoy)

**Ya está hecho y funcionando:**
- Los 3 generadores de datos, los 4 adaptadores entrenados, las técnicas de
  fusión y la destilación — todos evaluados sobre el mismo conjunto de prueba.
- Cuantización medida con números reales (no solo "probablemente ayudaría").
- Servicio desplegado públicamente, sirviendo el modelo fusionado (el bueno).
- Prueba de carga real hecha (parcial, por la cuota de GPU, pero confirma que
  el sistema funciona en paralelo).
- El paper compila limpio con todos estos resultados.

**Todavía falta:**
1. **Evaluación humana** — el pendiente más importante. Faltan evaluadores de
   los dialectos Andina, Rioplatense y Chilena (Mexicana y Caribeña ya tienen
   candidatos en curso).
2. Que Mariana y tú revisen las secciones de Resultados y Conclusiones del
   paper.
3. Ensayo cronometrado de la sustentación + grabar el video del plan B.
4. Un detalle menor de numeración de sesiones en la bitácora (no afecta nada
   del contenido).

---

*Documento preparado solo para tu estudio personal — todas las cifras están
verificadas contra los archivos reales del repositorio (`paper/main.tex`,
`docs/resultados_pi3.md`, `evaluation/`, `docs/pruebas_carga.md`), no hay
números inventados.*
