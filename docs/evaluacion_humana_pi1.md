# Evaluación humana ciega de los tres modelos individuales (PI1)

**Estado (2026-10-08): preparada, NO ejecutada.** `evaluation/evaluadores.csv`
está vacío: no hay ningún evaluador confirmado, así que no se envió nada y no
existen resultados humanos. `evaluation/resultados_humanos_pi1.csv` **no
existe a propósito**: lo crea `evaluation/consolidar_resultados_humanos.py`
solo a partir de hojas realmente devueltas, y se niega a escribir si falta
alguna. No se simuló ni se rellenó nada.

## Diseño

- **Qué se compara**: las traducciones de los adaptadores de los generadores 1,
  2 y 3 sobre **las mismas 60 expresiones** (12 por dialecto: primero las de
  referencia humana del banco de semillas y luego variantes del test común
  elegidas al azar; ninguna estuvo en entrenamiento de ningún modelo).
- **Ciego**: cada ítem muestra una fila por traducción distinta, con etiquetas
  A/B/C en orden aleatorio por ítem; si dos modelos dan exactamente la misma
  traducción se muestra una sola fila (por eso hay entre 28 y 36 filas por
  hoja, no 36 fijas). Las hojas no contienen nombres de modelos.
- **Clave privada**: `evaluation/evaluacion_humana/clave_modelos.json` **no
  se versiona** (el repositorio es público). Se generó con una semilla secreta
  que no está en el código, y su hash SHA-256 está en `clave_sha256.txt`, de
  modo que al cerrar la ronda se puede demostrar que no se alteró.
- **Escala**: 1-5 de retención de matices (`evaluation/rubrica_humana.md`).
- **Acuerdo entre evaluadores**: kappa de Fleiss (3 o más) y de Cohen ponderado
  (`evaluation/kappa.py`, verificado contra valores publicados).

## Verificación del ciego (`evaluation/verificar_ciego.py`)

Sobre las hojas generadas: sin nombres de modelos en ninguna celda ni
identificador; columnas esperadas; los tres modelos presentes en cada ítem; la
posición no delata al modelo (reparto de 23 % a 42 % por posición, sin ninguno
por encima del 50 %); y las longitudes medias difieren menos de 7 %
(13.3, 13.5 y 14.2 palabras), por debajo del umbral de aviso de 20 %. Limitación:
esto descarta pistas simples; no puede descartar que un evaluador reconozca el
estilo de un modelo al leer muchos ejemplos.

## Procedimiento (cuando haya evaluadores)

Ver `evaluation/mensaje_evaluadores_pi1.md`: qué enviar (solo la hoja de su
dialecto y las instrucciones), el texto del mensaje, el checklist previo y los
pasos al recibir las hojas.

## Qué falta

- Conseguir y confirmar **mínimo 3 evaluadores nativos por dialecto** (15 en
  total) y registrarlos en `evaluadores.csv` (con ID, no nombre real).
- Hacer la calibración cruzada de la rúbrica entre dos del equipo
  (pendiente desde la Sesión 23).
- Enviar, recoger, consolidar y calcular kappa.
- No se incluyó el modelo base como control. Añadirlo permitiría ver si los
  evaluadores distinguen entre "ajustado" y "sin ajustar"; es una decisión del
  equipo (agrega ~1/3 más de filas por hoja).
