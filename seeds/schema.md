# Esquema del banco de semillas

Una **semilla** es una expresión dialectal o de jerga en español, con su
traducción correcta al inglés, que alimenta el proceso de generación
sintética (Sesión 6: la plantilla de "derivación" toma una semilla y la
expande en varias variantes de contexto/registro/tono).

## Campos

| Campo | Tipo | Obligatorio |
|---|---|---|
| `id` | string | sí |
| `texto_original` | string | sí |
| `dialecto_region` | string | sí |
| `registro` | string (`formal` \| `informal` \| `jerga`) | sí |
| `traduccion_referencia` | string | sí |
| `nota_contexto_cultural` | string | sí |

### `id`

Identificador único de la semilla (ej. `sem-001`). Permite trazar una
expresión a lo largo de todo el pipeline — semilla → variantes generadas
por cada uno de los 3 LLMs (Semana 2 y Semana 7) → muestreo de validación
(Sesión 10) → evaluación humana (Sesión 24) — algo indispensable para
poder comparar generadores y auditar errores más adelante.

### `texto_original`

La expresión tal como se usa realmente en el habla cotidiana, sin
normalizar ortografía ni gramática. El modelo debe aprender el habla
real, no una versión "corregida"; normalizarla perdería justo la señal
dialectal que el proyecto busca capturar.

### `dialecto_region`

Región o macro-variante donde se usa la expresión (ej. `Caribeña`,
`Andina`, `Rioplatense`, `Mexicana`). Es la unidad de análisis para medir
cobertura dialectal, evitar que el dataset quede sesgado hacia un solo
dialecto, y desglosar métricas (BLEU/chrF, evaluación humana) por
dialecto, tal como exige `CONTEXTO_PROYECTO.md`.

### `registro`

Uno de `formal`, `informal` o `jerga`. **Dialecto y jerga son dos
dimensiones distintas y no deben mezclarse en el mismo campo**: una
expresión puede ser dialectal (propia de una región) sin ser jerga
(ej. "ahorita" es dialectal pero no marcadamente jerga), y jerga pura
puede aparecer en cualquier dialecto. Separarlas evita tratar ambos
fenómenos como si fueran lo mismo.

### `traduccion_referencia`

Traducción correcta al inglés, en el mismo registro y con el mismo
matiz de significado (no una traducción literal palabra por palabra).
Es el ground truth que alimenta BLEU/chrF (Sesión 21), la evaluación
humana (Sesiones 22-24), y el ejemplo de referencia dentro del prompt
de derivación (Sesión 6).

### `nota_contexto_cultural`

Nota breve (1-2 frases) de en qué situación se usa la expresión: quién
la dice, a quién, en qué tono. Una traducción literal no comunica cuándo
es apropiado usar la expresión ni qué matiz cultural conlleva — dato
necesario para que los evaluadores humanos puedan calificar "retención
de matices dialectales" (atributo de calidad definido en
`CONTEXTO_PROYECTO.md`).

## Ejemplo de una semilla completa

```json
{
  "id": "sem-001",
  "texto_original": "¡Qué nota!",
  "dialecto_region": "Caribeña",
  "registro": "jerga",
  "traduccion_referencia": "That's awesome!",
  "nota_contexto_cultural": "Exclamación de aprobación entusiasta, muy usada entre jóvenes de la costa caribe colombiana ante algo que les gustó mucho."
}
```

Ver `seeds/ejemplos.json` para 5 ejemplos completos que validan el
esquema en la práctica, cubriendo más de un dialecto.
