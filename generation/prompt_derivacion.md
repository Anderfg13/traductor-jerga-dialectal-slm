# Plantilla de prompt de "derivación"

La **derivación** es el paso de generación sintética (Semana 2 y Semana
7 del calendario): cada uno de los 3 LLMs generadores recibe UNA
semilla (`seeds/schema.md`) y la expande en varias variantes de uso
real — no la repite ni genera solo sinónimos. Esta plantilla es la que
se le manda a cada generador para hacer esa expansión, y debe producir
el mismo formato de salida sin importar cuál de los 3 LLMs la reciba
(Groq, Cohere o Google Gemini), para poder comparar entre generadores
más adelante (PI1).

## Requisitos que la plantilla exige explícitamente

1. **Conservar el significado real** de la expresión — la variante
   puede cambiar la situación de uso, no el significado.
2. **Entre 5 y 8 variantes por semilla**, cada una un contexto de uso
   distinto (quién habla, a quién, en qué situación/tono) — no solo
   parafraseos o sinónimos de la traducción.
3. **Salida en JSON estructurado**, parseable directamente sin
   posprocesamiento manual.
4. **No inventar dialectos ni mezclar el dialecto original con otro**
   — todas las variantes deben quedarse en el mismo
   `dialecto_region` de la semilla.

## Plantilla

El texto exacto (implementado como función en
`generation/probar_prompt_derivacion.py::construir_prompt`) es:

```text
Eres un lingüista que ayuda a construir un dataset de traducción
español-inglés para jerga y dialectos regionales del español.

Se te da UNA semilla: una expresión real de un dialecto del español,
su traducción de referencia al inglés, y una nota de contexto cultural.

SEMILLA:
- id: {id}
- Expresión original: "{texto_original}"
- Dialecto/región: {dialecto_region}
- Registro original: {registro}
- Traducción de referencia: "{traduccion_referencia}"
- Contexto cultural: {nota_contexto_cultural}

TAREA: genera entre 5 y 8 variantes de esta semilla. Cada variante debe:

1. Conservar el significado real de la expresión. No cambies lo que
   quiere decir, solo cómo y en qué situación se dice.
2. Usar la expresión (o una forma natural muy cercana) dentro de una
   oración de uso real distinta cada vez: varía el CONTEXTO (quién
   habla, a quién, en qué situación), el REGISTRO (formal/informal/
   jerga) y el TONO (serio, en broma, molesto, etc.). No generes solo
   sinónimos de la traducción: cada variante es una oración distinta.
3. Mantener el MISMO dialecto/región que la semilla: {dialecto_region}.
   No inventes un dialecto nuevo ni mezcles esta expresión con
   expresiones de otra región.
4. Incluir su propia traducción correcta al inglés, en el mismo
   registro y tono que la variante en español (no traducción literal
   palabra por palabra).

FORMATO DE SALIDA: responde ÚNICAMENTE con JSON válido, sin texto antes
ni después, sin bloques de código (```), exactamente con esta forma:

{{
  "seed_id": "{id}",
  "variantes": [
    {{
      "texto_dialectal": "...",
      "traduccion": "...",
      "registro": "formal | informal | jerga",
      "contexto_uso": "quién lo dice, a quién, y en qué situación/tono"
    }}
  ]
}}

El arreglo "variantes" debe tener entre 5 y 8 elementos. No agregues
campos ni comentarios fuera del JSON.
```

Los `{...}` se reemplazan con los campos de la semilla (mismos nombres
que `seeds/schema.md`) antes de mandar el prompt a cada generador.

## Ejemplo de entrada

Semilla `sem-007` del lote de Paula (`seeds/lote_01.json`):

```json
{
  "id": "sem-007",
  "texto_original": "Está brutal",
  "dialecto_region": "Caribeña",
  "registro": "jerga",
  "traduccion_referencia": "It's amazing",
  "nota_contexto_cultural": "Elogio entusiasta hacia algo que impresionó mucho a quien habla, usado entre jóvenes en tono muy informal."
}
```

## Ejemplo de salida

Salida real de Cohere (`command-r-08-2024`) para la semilla `sem-007`,
obtenida corriendo:

```bash
python generation/probar_prompt_derivacion.py --generador cohere --ids sem-007
```

```json
{
  "seed_id": "sem-007",
  "variantes": [
    {
      "texto_dialectal": "El concierto de anoche estuvo brutal.",
      "traduccion": "Last night's concert was incredible.",
      "registro": "informal",
      "contexto_uso": "Un joven hablando con un amigo sobre un concierto al que asistieron."
    },
    {
      "texto_dialectal": "La comida que preparó tu madre está brutal, ¡felicítala de mi parte!",
      "traduccion": "Your mom's cooking is amazing; please give her my compliments!",
      "registro": "informal",
      "contexto_uso": "Un amigo elogiando la comida de la madre de otro amigo."
    },
    {
      "texto_dialectal": "El nuevo restaurante en el centro está brutal, tienes que probarlo.",
      "traduccion": "The new restaurant in town is amazing; you should definitely check it out.",
      "registro": "informal",
      "contexto_uso": "Una persona recomendando un restaurante a un amigo."
    },
    {
      "texto_dialectal": "La vista desde la cima de la montaña es brutal, ¡qué experiencia!",
      "traduccion": "The view from the top of the mountain is breathtaking; what an experience!",
      "registro": "informal",
      "contexto_uso": "Alguien compartiendo su emoción tras una caminata en la montaña."
    },
    {
      "texto_dialectal": "El partido de hoy estuvo brutal, ¡qué emoción!",
      "traduccion": "Today's game was amazing; what a thrill!",
      "registro": "informal",
      "contexto_uso": "Un fanático deportivo hablando con otro sobre un partido emocionante."
    },
    {
      "texto_dialectal": "La presentación de la banda local estuvo brutal, me encantó su energía.",
      "traduccion": "The local band's performance was incredible; I loved their energy.",
      "registro": "informal",
      "contexto_uso": "Un asistente a un concierto compartiendo su opinión con un amigo."
    },
    {
      "texto_dialectal": "El proyecto que presentaste está brutal, felicidades.",
      "traduccion": "The project you presented is amazing; congratulations.",
      "registro": "formal",
      "contexto_uso": "Un profesor elogiando el trabajo de un estudiante."
    }
  ]
}
```

7 variantes, JSON válido, todas conservan el dialecto Caribeña de la
semilla original (ninguna inventa ni mezcla otro dialecto) y varían
contexto/tono sin ser simples sinónimos. La semilla `sem-018` ("Hacer
una vaca", Andina) se probó con el mismo comando y también dio 7
variantes válidas.
