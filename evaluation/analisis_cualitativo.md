# Análisis cualitativo de errores (versión preliminar)

**Qué es y qué no es.** La tarea pedía basarse en los comentarios de los
evaluadores humanos (`evaluation/resultados_humanos_pi1.csv`). Ese archivo **no
existe**: no hay evaluadores ni comentarios. Este análisis parte de las salidas
reales del mejor modelo (fusión simple con `mergekit`, 44.2 BLEU / 58.4 chrF,
`evaluation/predicciones/mergekit_linear.json`) frente a sus referencias sobre el
test común. **La clasificación la hizo una sola persona leyendo los casos (el
autor de este análisis), no hablantes nativos**: los sentidos regionales se
tomaron de las referencias del banco de semillas y del conocimiento del autor, y
deben validarse con evaluadores nativos. Cada ejemplo es un caso real del test;
ninguno está inventado.

## Método

1. Se calculó chrF por frase (sacrebleu) para las 174 entradas del test común.
2. Se leyeron a mano las **34 de menor puntaje** (el 20 %; chrF de 4 a 43; la mediana
   de todas es 56) y se clasificó cada una por tipo de error en la categoría que
   mejor la describe.
3. Se calcularon, por dialecto y por expresión, el chrF medio y el porcentaje de
   frases con chrF < 40.

## Categorías de error (34 casos peor puntuados)

| # | Categoría | Casos | % |
|---|---|---|---|
| 1 | Sentido equivocado por polisemia dialectal | 8 | 24 % |
| 2 | Sustitución por otra expresión inglesa más frecuente | 6 | 18 % |
| 3 | Sentido aproximado: pierde matiz o inmediatez | 8 | 24 % |
| 4 | Traducción literal de una comparación o metáfora | 2 | 6 % |
| 5 | Traducción aceptable penalizada por la métrica (artefacto) | 10 | 29 % |

Lectura de conjunto: unos **16 de 34 (47 %) son errores reales de significado**
(categorías 1, 2 y 4), 8 (24 %) conservan el sentido general pero pierden matiz, y
**10 (29 %) no son errores**: el modelo tradujo bien y la métrica lo castiga porque
la referencia usa otras palabras. Un chrF bajo no siempre significa un error.

### 1. Sentido equivocado por polisemia dialectal

La palabra tiene un sentido regional distinto del estándar y el modelo elige otro.

- **"mosca"** (Andina, "alerta"): *"Oiga, mijo, ande mosca por el centro hoy porque la
  cosa está pesada."* → modelo: *"Hey, kid, go out and get yourself a drink around town
  because things are getting serious."* (referencia: *"keep your eyes peeled downtown"*).
  También *"Manténganse mosca en la zona bancaria..."* → *"Stay out of the financial
  district..."* (referencia: *"Stay on guard around the banking district"*) y
  *"Estoy mosca con la situación..."* → *"I'm frustrated with the situation..."*
  (referencia: *"I'm on guard"*).
- **"pedo"** (Mexicana, "borracho"): *"...está bien pedo y me tiene de los dos lados..."*
  → *"it's just so annoying and it's got me in a bind"* (referencia: *"he's really drunk
  and he's holding me from both sides"*).
- **"mala leche"** (Rioplatense): *"Qué mala leche tiene esa mujer, no se le puede decir
  nada."* → *"She's such a snitch, you can't say anything to her."* (referencia:
  *"ill-tempered"*): el modelo inventa un sentido ("soplón") que no aparece.
- **"hacer el bulto"** (Caribeña): *"...algunos jugadores que hacen el bulto..."* →
  *"...players who act like they're doing it all, but..."*, justo lo contrario de la
  referencia (*"just there without really putting in the effort"*).
- Expresión aislada: *"Estar bien pedo"* → *"Be cool"* (referencia: *"To be really drunk"*);
  *"Estar mosca"* → *"To be pissed off"* (referencia: *"on the alert / on guard"*).

### 2. Sustitución por otra expresión inglesa más frecuente

El modelo reconoce una expresión que se parece a una inglesa y la reemplaza.

- **"coger la caña"** (Andina, "picar el anzuelo / caer en la broma"): *"El profe nos dijo
  que habría examen sorpresa y todos cogieron la caña rapidito."* → *"...and we all got
  our act together quickly."* (referencia: *"everyone fell for it right away"*). Aislada:
  *"Coger la caña"* → *"Get your act together"*.
- **"hacerse humo"** aislada → *"To get a buzz, to get high"* (referencia: *"To vanish /
  take off quickly"*).
- **"hacer el bulto"** aislada → *"Pulling a prank"* (referencia: *"To just be there
  without really helping"*).
- *"...no coger la caña es una habilidad..."* → *"...getting good at it is a skill..."*:
  omite la expresión.

### 3. Sentido aproximado: pierde matiz o inmediatez

- **"al tiro"** (Chilena, "enseguida"): *"Lo tengo al tiro, no te preocupes."* → *"I've got it
  covered, don't worry."* (referencia: *"I'll have it ready right away"*); *"Al tiro, jefe."* →
  *"Let's go, boss."* (referencia: *"Right away, boss."*); *"¡Al tiro! No me quedo esperando,
  ya voy."* → *"Let's go! I'm not waiting around..."*. Aislada: *"Al tiro"* → *"On the spot"*.
- **"neta"** (Mexicana, énfasis): *"¿Es neta que cerraron la taquería? Justo venía con
  hambre."* → *"Is it true they closed the taqueria? I just came by with an empty
  stomach."* (referencia: *"Are you for real telling me the taco place is closed? I was so
  hungry."*): correcto pero sin la carga enfática.
- *"No te preocupes, es solo que tengo mala leche hoy."* → *"...I'm in a bad mood today."*
  (referencia: *"I'm just having a bad day and feeling a bit grumpy"*).

### 4. Traducción literal de una comparación o metáfora

- **"salado"** (Caribeña, "con mala racha"): *"Chamo, no me toques que estoy más salado que
  un bacalao hoy."* → *"Bro, don't touch me, I'm as salty as a cod today."* (referencia:
  *"I'm having the worst streak of bad luck today"*). Aislada: *"Estar salado"* → *"Being
  salty"*.

### 5. Traducción aceptable penalizada por la métrica

Son los casos que más importa no confundir con errores.

- *"El testigo clave se hizo humo y ahora no podemos encontrarlo."* → *"The key witness
  disappeared and we can't find him anymore."* (referencia: *"The key witness has vanished,
  and we're unable to locate him."*): correcto, chrF 36.
- *"Al llegar al despacho, el abogado se hizo humo..."* → *"...he disappeared, and the meeting
  was put on hold."*: correcto, chrF 34.
- *"Si van a rematar la fiesta por la 85, anden mosca porque la policía anda rondando."* →
  *"...be careful because the police are patrolling."*: correcto, chrF 40.
- *"¡Neta que ya me tienes harto con tus mentiras!"* → *"Damn, you've really got me fed up
  with your lies!"*: sentido correcto, chrF 29.

## Por expresión y por dialecto

Frases del test común (mergekit lineal). Cada dialecto tiene 1 o 2 expresiones, por
lo que **no se puede separar "fallar en un dialecto" de "fallar en esa expresión"**.

| Dialecto | n | chrF medio por frase | % de frases con chrF < 40 |
|---|---|---|---|
| Mexicana | 40 | 64.9 | 10 % |
| Caribeña | 39 | 55.8 | 13 % |
| Andina | 38 | 53.8 | 16 % |
| Rioplatense | 38 | 57.0 | 21 % |
| Chilena | 19 | 52.6 | 26 % |

| Expresión (semilla) | Dialecto | chrF medio |
|---|---|---|
| "al tiro" (sem-092) | Chilena | 52.6 |
| "coger la caña" (sem-067) | Andina | 52.7 |
| "hacer el bulto" (sem-053) | Caribeña | 53.7 |
| "estar mosca" (sem-019) | Andina | 54.9 |
| "mala leche" (sem-078) | Rioplatense | 55.9 |
| "estar salado" (sem-012) | Caribeña | 58.0 |
| "hacerse humo" (sem-079) | Rioplatense | 58.1 |
| "estar bien pedo" (sem-088) | Mexicana | 61.2 |
| "neta" (sem-042) | Mexicana | 68.5 |

Las expresiones aisladas ("oro", n = 9) puntúan un chrF medio de **14.3**, frente a
**59.7** de las oraciones con contexto. Parte de esa brecha es de formato: las
referencias de esas 9 entradas son glosas con alternativas ("To vanish / take off
quickly"), que la métrica castiga aunque la traducción sea razonable.

## Qué sugiere (con cautela)

- Los errores reales se concentran en **expresiones polisémicas regionales**
  ("mosca", "pedo", "mala leche", "coger la caña", "hacer el bulto", "hacerse humo"): el
  modelo las confunde con el sentido estándar o con una expresión inglesa de
  apariencia parecida.
- Dar contexto (la frase completa) ayuda: las expresiones aisladas son las peor
  traducidas; en oraciones, varios errores desaparecen.
- Chilena aparece como el dialecto con más frases bajas (26 %), pero es **una sola
  expresión** ("al tiro"): no se puede atribuir al dialecto.
- Un chrF bajo no es sinónimo de error: casi un tercio de los peores casos eran
  traducciones aceptables. Es otra razón para la evaluación humana.

## Limitaciones

- Un solo lector; clasificación subjetiva en los casos de frontera (p. ej., entre
  "sentido aproximado" y "sustitución"). Sin acuerdo entre anotadores.
- Solo el 20 % peor puntuado de un modelo; no se analizaron los otros modelos ni
  los aciertos.
- 9 expresiones en total (9 semillas de prueba): las categorías describen estas 9
  expresiones, no el comportamiento general del modelo.
- Sin comentarios de evaluadores humanos: cuando existan, este análisis debe
  rehacerse con sus calificaciones y comentarios (ver `docs/hoja_de_ruta_fin_proyecto.md`).
