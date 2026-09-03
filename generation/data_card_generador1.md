# Data card — dataset del Generador 1

## Qué es

Dataset de entrenamiento español-inglés para jerga/dialectos,
generado sintéticamente a partir del banco de semillas curado por
Paula (`seeds/lote_01.json`, 40 semillas) mediante el proceso de
"derivación" (`generation/prompt_derivacion.md`, Sesión 6), usando
**Generador 1 = Groq (`openai/gpt-oss-20b`)** como único LLM generador
(`generation/generar_sintetico.py` + `generation/consolidar.py`,
Sesiones 7-8, Anderson).

## Tamaño y cobertura

| Etapa | Variantes | Semillas cubiertas |
|---|---|---|
| Generadas en crudo (`dataset_generador1.json`) | 238 | 40 |
| Después del filtro automático (`dataset_generador1_limpio.json`) | 236 | 40 |

Cobertura por dialecto (semillas, todas con 10 cada una en el lote de
origen):

| Dialecto | Semillas | Variantes en el dataset limpio |
|---|---|---|
| Caribeña | 10 | 59 |
| Andina | 10 | 60 |
| Rioplatense | 10 | 58 |
| Mexicana | 10 | 59 |

(el pequeño desbalance de variantes entre dialectos, pese a tener las
mismas 10 semillas cada uno, viene de que el generador no siempre
produce exactamente el mismo número de variantes por semilla — puede
dar entre 5 y 8, según pide `prompt_derivacion.md`).

**Nota de alcance:** este dataset solo cubre `seeds/lote_01.json`. El
segundo lote de semillas de Paula (`seeds/lote_02.json`, 60 semillas
más, incluye el dialecto Chileno) se curó en la Sesión 9, **después**
de que Anderson corriera esta generación (Sesiones 7-8) — todavía no
tiene su propia pasada de generación sintética.

## Cómo se generó

1. Semilla real (`seeds/lote_01.json`, esquema en `seeds/schema.md`).
2. Plantilla de derivación (`generation/prompt_derivacion.md`, Sesión
   6): pide 5-8 variantes por semilla, variando contexto/registro/tono,
   conservando el significado y el dialecto original, en JSON.
3. Llamada a Groq (`generar_sintetico.py`, Sesión 7) con reintentos y
   guardado de la salida cruda por semilla en `generation/raw/generador1/`
   antes de cualquier procesamiento.
4. Consolidación (`consolidar.py`, Sesión 8): parsea cada salida cruda,
   descarta variantes vacías y duplicados exactos, y arma
   `dataset_generador1.json`.

## Filtros aplicados (Sesión 11, `generation/validar.py`)

4 reglas automáticas — ver el docstring de `validar.py` para el
razonamiento completo de cada una:

1. Longitud fuera de rango (< 3 o > 40 palabras) → descarta.
2. Casi idéntica a la semilla original, sin variación real (similitud
   >= 0.8) → descarta.
3. Idioma inesperado (heurística de palabras frecuentes es/en) →
   marca como sospechosa, no descarta.
4. Duplicada exacta dentro del dataset → descarta.

**Resultado:** 236/238 aprobadas (99.2%), 2 descartadas (0.8%, ambas
por la regla 2 — variantes que solo agregaban una palabra suelta tipo
"che"/"¿vale?" a la semilla), 0 marcadas como sospechosas. Muy por
debajo del límite de 20% definido como criterio de calidad — no hizo
falta ajustar la plantilla de derivación.

## Splits (Sesión 12, `generation/split_dataset.py`)

80/10/10 por **semilla** (no por variante, para evitar fuga de datos:
todas las variantes de una semilla quedan en el mismo split),
estratificado por dialecto para que los 4 dialectos queden
proporcionalmente representados en los tres splits.

| Split | Semillas | Variantes |
|---|---|---|
| train | 32 | 189 |
| val | 4 | 24 |
| test | 4 | 23 |
| **Total** | **40** | **236** |

Verificado automáticamente (dentro de `split_dataset.py`): ninguna
semilla aparece en más de un split, y la suma de variantes de los tres
splits coincide con el total del dataset limpio.

## Limitaciones conocidas

- **Solo un generador (Groq).** Este dataset no dice nada todavía
  sobre PI1 (efecto del generador en la calidad) — eso requiere los
  Generadores 2 y 3 (Semana 7) entrenados con la misma configuración
  para comparar.
- **Solo `seeds/lote_01.json` (40 de las 100 semillas que ya existen
  en el banco combinado).** El dialecto Chileno (agregado en
  `seeds/lote_02.json`, Sesión 9) no tiene ninguna representación en
  este dataset.
- **El filtro automático no detecta mezcla de dialectos dentro de una
  misma variante**, solo detecta longitud, casi-duplicados de la
  semilla, idioma inesperado y duplicados exactos. La evaluación
  humana piloto (Sesión 10, Paula) encontró un caso real que las 4
  reglas de `validar.py` no atrapan: la semilla `sem-016` (Andina)
  tiene una variante con "Che" —un marcador claramente Rioplatense—
  ("Che, ¡qué chimba tu nuevo look!"), y **sigue presente en
  `dataset_generador1_limpio.json`** porque ninguna de las 4 reglas
  actuales busca marcadores de otro dialecto. Es un hueco conocido del
  filtro automático, no un error de esta sesión — se deja anotado
  aquí para que quien entrene con este dataset lo sepa, y como
  candidato a una futura Regla 5 (detección de mezcla de dialectos)
  si el equipo decide que vale la pena antes del entrenamiento
  completo (Sesión 19).
- **La heurística de idioma (regla 3) es aproximada** (conteo de
  palabras frecuentes es/en, no un detector de idioma real) y se
  calibró contra este dataset específico para evitar falsos positivos
  en frases cortas — podría comportarse distinto con los datasets de
  los Generadores 2 y 3.
- **Splits pequeños** (4 semillas en val, 4 en test): suficientes para
  un MVP de Fase 2, pero las métricas automáticas (BLEU/chrF, Sesión
  21) sobre un test de solo 23 variantes van a tener bastante
  varianza — no sobre-interpretar diferencias pequeñas.
