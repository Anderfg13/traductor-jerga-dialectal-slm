# Checklist de reclutamiento y evaluación humana (PI1)

Documento único para seguir paso a paso, desde que se contacta a alguien
hasta que su hoja queda lista para el análisis. Junta en un solo lugar lo
que ya existía repartido en `reclutamiento_evaluadores.md`,
`rubrica_humana.md` y `mensaje_evaluadores_pi1.md` (esos archivos siguen
siendo la fuente de detalle; este es el flujo operativo).

Objetivo: **15 evaluadores, 3 nativos por cada uno de 5 dialectos**
(Caribeña, Andina, Rioplatense, Mexicana, Chilena).

**IDs**: se asignan de forma global y secuencial a medida que se confirma
gente, sin importar el dialecto: `E1`, `E2`, `E3`... hasta `E15`. Nunca el
nombre real de la persona en ningún archivo del repositorio.

---

## Paso 0 — Antes de contactar a nadie (una sola vez, hacerlo ya)

- [ ] **Calibración cruzada de la rúbrica** entre dos personas del equipo:
  cada una califica por separado los 5 ejemplos de
  `evaluation/rubrica_humana.md` (sin consultarse) y comparan. Si alguna
  calificación difiere en más de 1 punto, hay que afinar la rúbrica antes
  de seguir. **Todavía no se ha hecho** — es lo único que bloquea el resto
  de este checklist, así que conviene hacerlo primero.
- [ ] **Decidir en equipo** si se agrega el modelo base como control en la
  ronda (agrega ~1/3 más de filas por hoja a cada evaluador). Anotar la
  decisión aquí: ______

## Paso 1 — Contactar personas

Para cada persona candidata, mandar este mensaje (reemplaza `[DIALECTO]`):

> Hola! Estamos armando un traductor de jerga/dialectos del español
> (proyecto universitario) y necesitamos tu ayuda como hablante nativo
> de [DIALECTO]. La tarea: calificar ~15-20 traducciones cortas al
> inglés en una escala de 1-5 según qué tanto conservan el sentido
> real de la expresión — toma unos 15-20 minutos. No necesitas saber
> de tecnología, solo tu criterio como hablante de la región. ¿Te
> animas?

Si dice que sí, pasa el filtro con estas tres preguntas (evita el
"¿de dónde eres?" ambiguo):

1. ¿En qué ciudad/región creciste y viviste la mayor parte de tu vida?
2. ¿Qué variante del español hablas en tu día a día (la que usas con
   familia/amigos, no la que usarías en un examen)?
3. ¿Cuánto tiempo llevas fuera de esa región, si aplica?

Mensajes ya personalizados por dialecto, listos para copiar y pegar:

<details>
<summary><b>Caribeña</b></summary>

> Hola! Estamos armando un traductor de jerga/dialectos del español
> (proyecto universitario) y necesitamos tu ayuda como hablante nativo
> de **Caribeña**. La tarea: calificar ~15-20 traducciones cortas al
> inglés en una escala de 1-5 según qué tanto conservan el sentido
> real de la expresión — toma unos 15-20 minutos. No necesitas saber
> de tecnología, solo tu criterio como hablante de la región. ¿Te
> animas?
</details>

<details>
<summary><b>Andina</b></summary>

> Hola! Estamos armando un traductor de jerga/dialectos del español
> (proyecto universitario) y necesitamos tu ayuda como hablante nativo
> de **Andina**. La tarea: calificar ~15-20 traducciones cortas al
> inglés en una escala de 1-5 según qué tanto conservan el sentido
> real de la expresión — toma unos 15-20 minutos. No necesitas saber
> de tecnología, solo tu criterio como hablante de la región. ¿Te
> animas?
</details>

<details>
<summary><b>Rioplatense</b></summary>

> Hola! Estamos armando un traductor de jerga/dialectos del español
> (proyecto universitario) y necesitamos tu ayuda como hablante nativo
> de **Rioplatense**. La tarea: calificar ~15-20 traducciones cortas al
> inglés en una escala de 1-5 según qué tanto conservan el sentido
> real de la expresión — toma unos 15-20 minutos. No necesitas saber
> de tecnología, solo tu criterio como hablante de la región. ¿Te
> animas?
</details>

<details>
<summary><b>Mexicana</b></summary>

> Hola! Estamos armando un traductor de jerga/dialectos del español
> (proyecto universitario) y necesitamos tu ayuda como hablante nativo
> de **Mexicana**. La tarea: calificar ~15-20 traducciones cortas al
> inglés en una escala de 1-5 según qué tanto conservan el sentido
> real de la expresión — toma unos 15-20 minutos. No necesitas saber
> de tecnología, solo tu criterio como hablante de la región. ¿Te
> animas?
</details>

<details>
<summary><b>Chilena</b></summary>

> Hola! Estamos armando un traductor de jerga/dialectos del español
> (proyecto universitario) y necesitamos tu ayuda como hablante nativo
> de **Chilena**. La tarea: calificar ~15-20 traducciones cortas al
> inglés en una escala de 1-5 según qué tanto conservan el sentido
> real de la expresión — toma unos 15-20 minutos. No necesitas saber
> de tecnología, solo tu criterio como hablante de la región. ¿Te
> animas?
</details>

**Dónde buscar gente**: contactos directos del equipo primero (familia,
amigos, compañeros de otras materias). Si no alcanza el mínimo por
dialecto, sobre todo en Chilena y Rioplatense (donde el equipo tiene
menos contactos directos), usar Prolific u otra plataforma de anotación
remunerada.

## Paso 2 — Registrar a cada persona confirmada

En cuanto alguien pasa el filtro y acepta, anótala en
`evaluation/evaluadores.csv` (ya tiene 15 filas vacías, 3 por dialecto,
listas para llenar):

1. Asígnale el siguiente ID disponible (`E1`, `E2`...).
2. Llena `contacto_id` (el ID, no el nombre), `fecha_contacto` y marca
   `confirmado` = sí.
3. **Nunca** pongas el nombre real en `evaluadores.csv` ni en ningún otro
   archivo del repositorio — es público. Si el equipo necesita recordar
   quién es quién, eso se guarda aparte, fuera del repo (por ejemplo, un
   mensaje privado entre ustedes).

## Paso 3 — Cuando un dialecto llega a 3 confirmados

Recién ahí se le envía la tarea real a esas personas (no antes, y no a
alguien de un dialecto que todavía no tiene el mínimo, para no generar
hojas que después no se puedan analizar en conjunto).

Qué enviar a **cada** evaluador, nada más:

1. Su hoja: `evaluation/evaluacion_humana/hojas/<Dialecto>.csv`
2. `evaluation/evaluacion_humana/instrucciones_evaluador.md`

**Nunca** envíes `clave_modelos.json`, nada más de `evaluation/`, ni el
enlace del repositorio — revelan qué modelo hizo cada traducción.

Mensaje a personalizar por persona (`[nombre]`, `[tu nombre]`, `[PLAZO]`,
y su `[ID]` ya asignado en el Paso 2):

> Hola [nombre]. Soy [tu nombre]. En un proyecto de la universidad estamos
> probando un traductor de jerga y dialectos del español al inglés, y necesito
> tu ayuda como hablante nativo de **[DIALECTO]**.
>
> Te mando una hoja con unas 30 filas: cada una tiene una expresión en español
> y UNA traducción al inglés. Para cada fila pon, en la columna `calificacion`,
> un número del 1 al 5 según qué tanto la traducción conserva el **significado
> y el tono** de lo que dice el hablante (no importa si el inglés está bien
> escrito, importa si dice lo mismo que dice la expresión):
>
> 5 = significado y tono idénticos · 4 = significado intacto pero el tono queda
> más neutro · 3 = se entiende, pero se pierde un matiz importante · 2 = queda
> distorsionado o ambiguo · 1 = el significado se pierde o se invierte.
>
> Si dudas entre dos números, elige el más bajo. Si calificas 3 o menos, escribe
> en `comentario` una frase del porqué. Algunas filas repiten la misma expresión
> con traducciones distintas: califícalas por separado, sin compararlas. No sabes
> (ni necesitas saber) cómo se hicieron las traducciones.
>
> Toma unos 15-20 minutos. Hazlo por tu cuenta, sin consultar a nadie. Guarda el
> archivo como **CSV** con el nombre **`[Dialecto]__[ID]`.csv** (por ejemplo
> `Andina__E1.csv`; usa solo el ID que te doy, no tu nombre) y mándamelo de
> vuelta antes del [PLAZO]. No uso tus datos para nada más que este proyecto, y
> solo guardo tu ID, no tu nombre, junto a tus calificaciones.

Checklist antes de dar clic a enviar, por persona:

- [ ] Ya está hecha la calibración cruzada (Paso 0).
- [ ] La persona tiene su ID asignado y está en `evaluadores.csv`.
- [ ] Marca `instrucciones_enviadas` = fecha en `evaluadores.csv` al enviar.

## Paso 4 — Al recibir cada hoja de vuelta

1. Verifica que el nombre del archivo sea exactamente
   `<Dialecto>__<ID>.csv` (por ejemplo `Andina__E1.csv`).
2. Guárdala en `evaluation/evaluacion_humana/respuestas/`.
3. Marca en `evaluadores.csv` que esa persona ya devolvió su hoja (usa la
   columna `notas`).

## Paso 5 — Cuando TODAS las hojas de un dialecto estén de vuelta (idealmente las 15)

Avisar a quien vaya a correr el análisis (hoy, eso lo hace quien tenga
sesión con Claude en el repo — ver la tabla "Cuando me pases X, yo hago Y"
en `docs/hoja_de_ruta_fin_proyecto.md`). Esa persona corre, en orden:

1. `python evaluation/verificar_ciego.py`
2. `python evaluation/consolidar_resultados_humanos.py` → crea
   `evaluation/resultados_humanos_pi1.csv`
3. `python evaluation/analisis_pi1.py` → kappa de Fleiss/Cohen y puntaje
   humano por modelo
4. Solo ahora: publicar `clave_modelos.json` (guardado aparte, fuera de
   git) y verificar su hash contra `clave_sha256.txt`
5. Actualizar `paper/main.tex` (PI1 y conclusiones), recompilar y anotar
   la bitácora

## Resumen de archivos que ya existen y no hay que recrear

| Qué | Dónde |
|---|---|
| Rúbrica (escala 1-5) y ejemplos de calibración | `evaluation/rubrica_humana.md` |
| Registro de evaluadores (15 filas listas para llenar) | `evaluation/evaluadores.csv` |
| Hojas ciegas por dialecto | `evaluation/evaluacion_humana/hojas/<Dialecto>.csv` |
| Instrucciones para el evaluador | `evaluation/evaluacion_humana/instrucciones_evaluador.md` |
| Detalle completo del diseño del experimento | `docs/evaluacion_humana_pi1.md` |
