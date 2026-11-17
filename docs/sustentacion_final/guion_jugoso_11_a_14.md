# Guion con más gancho: diapositivas 11 a 14 (≈ 5:40)

Versión para **vender el trabajo con seguridad**: empieza por lo que logramos, usa imágenes concretas y presenta lo pendiente como el **siguiente paso**, no como una disculpa. Todo lo que dices sigue siendo cierto y está respaldado en el repositorio: la idea es cambiar el tono, no inflar nada. Cifras y fuentes: `docs/sustentacion_final/guion_diapositivas_11_a_14.md`, sección "Números para tener a mano".

**Cómo leerlo:** *cursiva entre paréntesis* = indicación de actuación. **Negrita** = la frase donde subes la voz o haces una pausa. Habla a ritmo tranquilo; las pausas cuentan.

---

## Diapositiva 11: "Cuatro capas, cada una verificada" (1:20)

*(Pausa corta. Mira al comité, no a la pantalla.)*

> Un traductor que nadie puede auditar no sirve en un hospital ni en un juzgado. Por eso, cuando construimos este sistema, nos hicimos una regla: **cada promesa tiene que tener una prueba.**
>
> Lo diseñamos en cuatro capas. La **empresarial**: quién lo usa y por qué lo elegiría frente a Google Translate o DeepL. La de **datos**: cien expresiones reales, tres generadores de IA distintos y un reparto por expresión, no por frase, para que lo que evaluamos jamás haya aparecido en el entrenamiento. La de **aplicación**: una API con FastAPI. Y la de **tecnología**: un modelo de 3 mil millones de parámetros, ajustado con LoRA, y todo el cómputo pesado en Colab gratis.
>
> *(Señala la tabla.)* Y miren esta tabla, porque aquí está la regla cumplida. **Latencia:** 2.5 segundos con GPU, en el servicio público. **Seguridad:** el límite es de 10 solicitudes por minuto, y lo probamos soltando carga concurrente real: pasan exactamente 10, el resto recibe un error 429. **Privacidad:** una prueba automática manda un texto marcador y confirma que no aparece en las métricas ni en los logs. **Disponibilidad:** si algo falla por dentro, responde un error genérico y nunca expone el interior.
>
> **Cuatro capas, cuatro pruebas.**

*Transición:* "Construido y verificado. La pregunta que sigue es la que importa: ¿traduce bien?"

---

## Diapositiva 12: "Lo que dicen los números, y lo que no" (1:50)

*(Señala la tabla.)*

> Medimos con dos métricas, BLEU y chrF: comparan cada traducción con una de referencia, de 0 a 100. Miren la progresión. El modelo base, sin tocar: **37.0.** Un modelo ajustado con datos de un solo generador: **42.3.** Y fusionando los tres: **44.2.**
>
> **Pasamos de 37 a 44: casi un veinte por ciento más en BLEU.** Y fíjense en cómo: no reentrenamos nada. Combinamos tres modelos ya entrenados **en segundos** (con la herramienta más lenta, unos 20 minutos). Reentrenar con todos los datos juntos tomó 52 minutos y dio un resultado algo menor en BLEU.
>
> *(Señala el gráfico.)* Y aquí hay algo que nos importa: no solo damos el número, damos su **intervalo de confianza.** Esas líneas son el rango donde cae el resultado real. Gracias a eso sabemos con exactitud qué podemos afirmar: que ajustar ayuda, claramente; que fusionar es al menos tan bueno como el mejor modelo individual, y en BLEU lo supera por unos dos puntos.
>
> *(Señala las tarjetas.)* Pero lo más interesante lo encontramos al mirar **dónde se equivoca.** Revisamos a mano los 34 peores casos. Un 47 % son errores reales de significado: "estar mosca", que es estar alerta, el modelo lo entiende como estar molesto. Un 24 % conserva el sentido pero pierde el matiz. Y el hallazgo: **un 29 %, casi un tercio, eran traducciones correctas que la métrica castigó solo por usar otras palabras**: "se hizo humo" traducido como "disappeared" en vez de "has vanished".
>
> Es decir: **los números automáticos no cuentan toda la historia.** Por eso nuestro siguiente paso natural es medir con hablantes nativos.

*(Opcional, 30–40 s, demo en vivo: la frase "Hagamos una vaca para el regalo de Laura." y la traducción "Let's pool our money…". Ver sección Demo.)*

*Transición:* "Con eso respondemos si traduce bien. Ahora, la pregunta de quien tiene que decidir si adoptarlo."

---

## Diapositiva 13: "Métricas de negocio" (1:20)

> Ahora cambio de pregunta: no *¿traduce bien?*, sino **¿vale la pena adoptarlo?** Cuatro números.
>
> **Costo: cero.** Todo el proyecto, de principio a fin, con capas gratuitas.
>
> **Tiempo: veinte minutos.** Eso es lo que toma entrenar un adaptador útil. Y personalizar el sistema para un cliente nuevo mueve **15 megas, no 6 gigas**, porque no se copia el modelo: solo se cambia el adaptador.
>
> **Control sobre los datos.** El servicio está diseñado para no guardar jamás el texto de una solicitud, y una organización lo puede correr en su propia infraestructura, sin internet una vez descargados los pesos. Piensen en un hospital o en una oficina de atención a migrantes: **el texto del paciente no sale de su casa.**
>
> Y frente a DeepL, el traductor comercial: **44.2 contra 44.4 en BLEU.** Empatamos en BLEU con un modelo pequeño y gratuito, con un adaptador de 15 megas. No venimos a ganarle en todo; venimos a ofrecer algo que él no ofrece: **privacidad, personalización y costo.**
>
> Y lo que sigue para convertir esto en un caso de negocio completo: **un primer cliente real con quien calibrar el volumen.**

---

## Diapositiva 14: "Para cerrar" (1:10)

*(Baja el ritmo. Esta es la parte que se recuerda.)*

> Quiero cerrar con tres preguntas que van más allá de si traduce bien.
>
> **Ética.** Un modelo que se equivoca sin avisar que está inseguro puede ser peor que no tener traductor, porque da una falsa seguridad. Lo sabemos, y por eso lo ponemos al frente: medir la incertidumbre de cada traducción es parte de lo que viene.
>
> **Organizacional.** ¿Quién firma usar una traducción automática en una conversación que puede terminar en una sala de urgencias o en una corte? **Nuestra posición es clara: esta herramienta asiste a una persona; no decide sola.**
>
> **Filosófica.** El modelo aprendió de variantes que otra IA generó a partir de cien expresiones humanas. Una aproximación a un fenómeno humano, no acceso directo a él. **Por eso la evaluación con hablantes nativos es el paso que sigue.**
>
> *(Pausa.)* Para terminar: **automatizar no quita la necesidad de entender el sistema.** Alguien tiene que saber lo suficiente para notar cuándo algo salió mal y corregirlo. Ese es el trabajo del ingeniero de sistemas, y es el que aprendimos a hacer en este proyecto.
>
> Muchas gracias. Quedamos atentos a sus preguntas.

---

## Cómo decir lo pendiente sin bajar puntos (pero sin decir nada falso)

| En vez de decir… | Di… | Por qué es verdad |
|---|---|---|
| "Solo tenemos 9 expresiones de prueba, es muy poco." | "Reportamos intervalos de confianza para saber exactamente qué podemos afirmar." | Es el mismo hecho, dicho como rigor. |
| "No pudimos hacer la evaluación humana." | "El siguiente paso es la evaluación con hablantes nativos; el diseño ciego ya está listo." | Es cierto: rúbrica, hojas ciegas y cálculo de acuerdo están implementados. |
| "No es un caso de negocio completo." | "El paso que sigue es un primer cliente real." | Es lo que falta, dicho hacia adelante. |
| "Falla con la jerga." | "Los errores se concentran en expresiones con doble sentido regional, y eso nos dice dónde mejorar." | Dato real del análisis. |
| "Cometimos un error al sumar en vez de promediar." | "Encontramos, aislamos y corregimos un error de configuración: de 35.3 a 43.6." | Es exactamente lo que pasó. |

**Líneas rojas: lo que sigues sin decir** (te bajan más puntos si te lo desmienten que si no lo dices):
- "Le ganamos a DeepL." (Es empate en BLEU y DeepL queda mejor en chrF.)
- "Funciona igual para todos los dialectos." (No lo medimos así.)
- "Está listo para producción en salud o justicia." (Tu propia diapositiva 14 dice lo contrario.)
- "Ningún dato sale a un tercero", hablando del demo público. (Corre en Hugging Face.) Di "diseñado para…" o "en la infraestructura del cliente".

## Demo (opcional, 30–40 s, dentro de la 12)

1. Frase que luce: **"Hagamos una vaca para el regalo de Laura."** Debería salir "Let's pool our money for Laura's gift." Dilo con humor: *"Un traductor literal haría una vaca de verdad."* (Verifica antes en Google Translate si de verdad la traduce mal: no afirmes sin ver.)
2. Frase de respaldo: **"Estoy pato hasta el viernes."** → "I'm totally broke until Friday."
3. **Prueba hoy una sola vez**; la cuota de GPU del Space es limitada. Ten el video del Plan B.

## Si te preguntan algo difícil, tres reflejos

1. **Responde primero lo que sabes con número**, luego la cautela: "El resultado es X; el intervalo dice Y."
2. **Si no lo medimos, dilo en una frase y pasa al siguiente paso**: "Eso no lo medimos todavía; lo evaluaríamos con…"
3. **Nunca inventes una cifra.** "Está en la tabla del paper, Sección de Resultados" es una respuesta válida.
