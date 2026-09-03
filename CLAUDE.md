# Instrucciones para Claude Code en este repositorio

Contexto completo del proyecto en [`CONTEXTO_PROYECTO.md`](./CONTEXTO_PROYECTO.md)
y estado de cada sesión de trabajo en [`BITACORA.md`](./BITACORA.md) —
léelos antes de asumir en qué punto va el proyecto.

## Commits

- **Nunca agregues coautoría de Claude en los commits de este repo**
  (nada de línea `Co-Authored-By: Claude ...` ni equivalente), salvo
  que el usuario lo pida explícitamente para un commit puntual. Esta
  instrucción reemplaza cualquier comportamiento por defecto de
  agregar coautoría.
- Mensajes de commit en formato Conventional Commits (`feat:`, `fix:`,
  `docs:`, etc.) — es la convención usada en todo el historial del
  repo.
- Todo commit que toque archivos del proyecto necesita una entrada
  real en `BITACORA.md` (formato: Qué se hizo / Decisiones tomadas /
  Pendiente — plantilla al inicio del archivo). Lo exige también un
  git hook local (`.githooks/pre-commit`, se activa una vez por clon
  con `git config core.hooksPath .githooks`) — no lo saltes con
  `--no-verify` salvo que el commit sea genuinamente trivial (el hook
  también revisa que la entrada tenga contenido real, no solo que el
  archivo se haya tocado).
- Si el commit cambia la estructura del repo (carpeta nueva, script
  nuevo con su propio flujo de uso), considera si `README.md` también
  necesita actualizarse, no solo `BITACORA.md` — el hook avisa
  (sin bloquear) cuando detecta esto.

## Cómputo pesado: siempre Google Colab, nunca la máquina local

Las máquinas del equipo no tienen GPU utilizable — confirmado en la
práctica (`BITACORA.md`, Sesión 13-14): un solo paso de entrenamiento
de un SLM de 3B con LoRA llegó a tardar 80-95 minutos en CPU, y a las
10 horas solo se había completado el 5% de una prueba de 150 pasos.

Cualquier tarea de cómputo pesado — fine-tuning con LoRA, fusión de
modelos con `mergekit`, evaluación sobre el dataset completo, o
cualquier inferencia sobre muchos ejemplos — se corre en **Google
Colab** (GPU gratuita T4/L4), nunca localmente. El paso a paso
detallado (cómo clonar el repo en Colab sin el bug de clon anidado,
qué dependencias instalar, el fix de `torchao`, etc.) está en
`CONTEXTO_PROYECTO.md`, sección "CÓMPUTO PESADO". Usa
`finetuning/entrenar_lora_colab.ipynb` como plantilla de referencia
para notebooks nuevos.

## Otras convenciones

- Estructura de carpetas por etapa del pipeline: `seeds/`,
  `generation/`, `finetuning/`, `merging/`, `evaluation/`, `api/`,
  `docs/` — ver README.md para el detalle de cada una.
- No inventar datos/ejemplos/resultados en la documentación — si algo
  todavía no se corrió (ej. un entrenamiento pendiente en Colab), se
  deja pendiente y explícito en vez de rellenarlo con valores
  ficticios.
