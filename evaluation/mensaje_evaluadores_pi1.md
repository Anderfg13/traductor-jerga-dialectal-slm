# Mensaje y paquete para los evaluadores (ronda PI1)

Qué se le manda a **cada** evaluador (nada más):

1. La hoja de **su** dialecto: `evaluation/evaluacion_humana/hojas/<Dialecto>.csv`
   (se abre con Excel o Google Sheets; está en UTF-8).
2. `evaluation/evaluacion_humana/instrucciones_evaluador.md` (o pegar su texto en el correo).

**Nunca** se envía `clave_modelos.json`, `verificacion_ciego_PRIVADO.md` ni nada
de `evaluation/`: dentro hay cosas que revelan qué modelo hizo cada traducción.
No compartas el enlace del repositorio con los evaluadores por la misma razón.

## Texto del mensaje (reemplaza [DIALECTO] y [PLAZO])

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
> archivo como **CSV** con el nombre `[Dialecto]__[tu ID].csv` (por ejemplo
> `Andina__E1.csv`; usa solo el ID que te doy, no tu nombre) y mándamelo de
> vuelta antes del [PLAZO]. No uso tus datos para nada más que este proyecto, y
> solo guardo tu ID, no tu nombre, junto a tus calificaciones.

## Antes de enviar (checklist)

- [ ] Hay 3 o más evaluadores confirmados **por dialecto** (`evaluation/evaluadores.csv`); Chilena y Rioplatense suelen ser las difíciles.
- [ ] Cada evaluador tiene un ID (E1, E2...) y el equipo guarda en `evaluadores.csv` quién es quién (privado, sin subir nombres reales si prefieren).
- [ ] La calibración cruzada de la rúbrica entre dos del equipo está hecha (ver el final de `evaluation/rubrica_humana.md`).
- [ ] `python evaluation/verificar_ciego.py` termina sin problemas.
- [ ] Anotar fecha de envío en `evaluadores.csv` (`instrucciones_enviadas`).

## Al recibir las hojas

1. Guardarlas en `evaluation/evaluacion_humana/respuestas/` con el nombre `<Dialecto>__<ID>.csv`.
2. `python evaluation/consolidar_resultados_humanos.py` → crea `evaluation/resultados_humanos_pi1.csv` (se niega si falta algo).
3. `python evaluation/kappa.py --salida evaluation/resultados_evaluacion_humana.md` → acuerdo entre evaluadores y puntaje por modelo.
4. Solo ahora: publicar la clave (`clave_modelos.json`) y verificar su hash con `clave_sha256.txt`.
