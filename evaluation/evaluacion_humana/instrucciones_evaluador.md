# Instrucciones para el evaluador

Gracias por ayudarnos. Eres hablante nativo del dialecto indicado en tu
hoja (`<dialecto>.csv`). Cada fila tiene una expresión en español y UNA
posible traducción al inglés. Para cada fila:

1. Lee `texto_dialectal` (lo que dice el hablante).
2. Lee `traduccion` (la traducción propuesta).
3. Pon en `calificacion` un número de 1 a 5 según qué tanto la
   traducción conserva el **significado y el tono** (no solo si está bien
   escrita en inglés):

| Punto | Significa |
|---|---|
| 5 | Significado y tono/registro se conservan por completo. |
| 4 | Significado intacto, pero el tono queda un poco más neutro/formal. |
| 3 | Se entiende, pero se pierde un matiz importante. |
| 2 | Significado parcialmente distorsionado o ambiguo. |
| 1 | Significado perdido o invertido. |

Si dudas entre dos números, elige el **más bajo**. Si calificas 3 o
menos, escribe en `comentario` una frase de por qué.

Notas:
- Varias filas comparten el mismo `id_item` (la misma frase) con
  traducciones distintas (`opcion` A, B, C...). Califícalas por separado.
- No sabes ni necesitas saber qué sistema produjo cada traducción.
- No consultes a otros evaluadores mientras calificas.
- Guarda el archivo como CSV (UTF-8) con el nombre `<Dialecto>__<tu ID>.csv` (por ejemplo `Andina__E1.csv`; usa el ID que te dieron, no tu nombre) y devuélvelo.
