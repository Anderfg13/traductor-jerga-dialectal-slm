# Modelo de gobernanza

> El syllabus pide explícitamente un "governance model" para el
> Project Advance 2. Esta pieza no tenía ninguna sesión asignada en el
> calendario interno de 60 sesiones — es trabajo nuevo, no una tarea
> que ya estuviera en curso. Documenta cómo se gobiernan las
> decisiones, los datos, los modelos y el proceso del proyecto,
> basado en lo que el equipo ya viene haciendo en la práctica (no son
> reglas nuevas inventadas para esta entrega, son las que ya rigen el
> repositorio desde hace varias semanas).

## 1. Gobernanza de decisiones (roles)

El equipo no tiene una jerarquía formal, pero en la práctica cada
persona es dueña de una porción del pipeline y toma las decisiones de
esa porción sin necesitar aprobación previa del resto — sí las deja
documentadas en `BITACORA.md` para que el equipo pueda objetar después
si hace falta (gobernanza "async", no por comité):

| Área | Dueño principal | Ejemplo de decisión tomada así |
|---|---|---|
| Infraestructura, generación sintética, entrenamiento | Anderson | Cambiar de generador cuando un modelo queda obsoleto (Sesión 2), escribir el script de LoRA para no bloquear al equipo (Sesión 14) |
| Datos (semillas, muestreo, validación humana), configuración de LoRA | Paula | Alcance dialectal final (Sesión 9), criterios de calificación del muestreo piloto (Sesión 10) |
| Estructura del repo, documentación, filtros y splits, observabilidad | Mariana | Formato de `BITACORA.md` (Sesión 5), reglas de filtrado automático (Sesión 11) |

Decisiones que sí requieren acuerdo explícito de los 3 (no solo del
dueño del área): cambios de alcance de fase (qué entra en Fase 2 vs
Fase 3), cambio de modelo base o de técnica de fusión, y cualquier
cosa que afecte la entrega ante el profesor. Estas quedan marcadas en
`BITACORA.md` como "decisión tomada con el equipo" quando aplica (ej.
Sesión 14: escribir el script de LoRA antes de que Paula lo hiciera).

## 2. Gobernanza de datos

- **Qué se versiona en el repositorio**: semillas, datasets sintéticos
  crudos y limpios, splits, data cards — todo en JSON/Markdown,
  versionado en git, con procedencia rastreable (`seed_id`, generador,
  modelo) hasta la semilla original.
- **Qué NO se persiste nunca, ni siquiera en el repo**: contenido real
  de traducciones que pase por el servicio en producción una vez esté
  desplegado (Sesión 28-29) — solo metadata agregada (dialecto,
  latencia, si el usuario marcó la traducción como correcta o no). Es
  una decisión de producto declarada desde `CONTEXTO_PROYECTO.md`
  ("los datos sensibles no salen a una nube de terceros"), no algo que
  se improvise en el momento de construir la API.
- **Datos de evaluadores humanos**: los resultados de evaluación
  (Sesión 24) se guardan con el dialecto y el evaluador identificado
  de forma anonimizada (no con nombre real ni dato de contacto en el
  archivo consolidado), suficiente para calcular kappa por dialecto
  sin exponer la identidad de quien evaluó.
- **Reproducibilidad**: todo muestreo aleatorio (splits, muestreo de
  validación) usa una semilla aleatoria fija y documentada en el
  propio script — cualquiera puede reproducir exactamente la misma
  muestra corriendo el mismo script.

## 3. Gobernanza de modelos

- **Versionado de artefactos**: cada adaptador LoRA entrenado vive en
  su propia carpeta con el nombre del generador que lo produjo
  (`finetuning/checkpoints/generadorN/`), nunca se sobrescribe un
  adaptador anterior con uno nuevo del mismo generador sin cambiar de
  carpeta o dejarlo explícito en `BITACORA.md`.
- **Criterio para promover un checkpoint a "final"**: el de mejor
  pérdida de validación, no el de la última época — ya implementado
  con `load_best_model_at_end` + `EarlyStoppingCallback` (Sesión 19),
  precisamente para no promover un checkpoint sobreajustado solo
  porque fue el último en entrenarse.
- **Cuándo re-entrenar**: si se amplía el banco de semillas (nuevo
  lote) o si la evaluación humana (Sesión 24 en adelante) muestra
  degradación de calidad en algún dialecto, no antes — no se
  re-entrena de forma reactiva sin una señal concreta que lo
  justifique, para no gastar cómputo gratuito de Colab sin necesidad.
- **Transparencia de limitaciones conocidas del modelo**: cualquier
  hallazgo negativo real (sobreajuste detectado en la Sesión 19, mezcla
  de dialecto encontrada en la Sesión 10, caso de "tinto" no corregido
  en la Sesión 20) se documenta explícitamente en vez de omitirse —
  política de honestidad que el equipo ha seguido desde la Fase 1 y
  que se mantiene aquí como parte de la gobernanza, no solo como buena
  fe puntual.

## 4. Gobernanza de proceso y código

- **Trazabilidad obligatoria**: todo commit que toca archivos del
  proyecto requiere una entrada real en `BITACORA.md`
  (Qué se hizo / Decisiones tomadas / Pendiente), exigido técnicamente
  por un git hook local (`.githooks/pre-commit`), no solo por
  convención escrita — el hook bloquea el commit si la entrada no
  tiene contenido real.
- **Convenciones de commit**: Conventional Commits (`feat:`, `fix:`,
  `docs:`) en todo el historial, para que el registro de cambios sea
  legible sin tener que releer cada diff.
- **Cómputo pesado siempre en Colab, nunca en máquina local** —
  política fija desde la Sesión 14, con el paso a paso documentado en
  `CONTEXTO_PROYECTO.md`, para que cualquier persona nueva en el
  equipo (o el profesor revisando el repo) entienda por qué no hay
  cómputo pesado corriendo localmente.
- **Instrucciones persistentes para asistentes de IA** (`CLAUDE.md`):
  el equipo usa Claude Code para varias sesiones de trabajo y dejó por
  escrito las reglas que debe seguir (sin coautoría automática en
  commits, seguir estas mismas convenciones) — la gobernanza del
  proyecto incluye explícitamente cómo se gobierna el uso de
  asistentes de IA dentro de él, no solo el trabajo humano.

## 5. Riesgos éticos y cómo se manejan

- **Contenido sensible en jerga/dialecto**: por decisión de alcance
  (ver `docs/alcance_banco_semillas.md`), el banco de semillas excluye
  groserías fuertes explícitas — el foco es jerga cotidiana no
  ofensiva, coherente con el caso de uso de producto (traducción para
  negocios/atención al cliente).
- **Representación dialectal**: se declaran explícitamente los
  dialectos NO cubiertos (español peninsular, Caribe insular) como
  limitación conocida, en vez de dar a entender que el modelo cubre
  "español" en general — evita una promesa de producto más amplia de
  lo que el modelo realmente puede hacer.
- **Privacidad del usuario final**: el servicio (una vez desplegado)
  no guarda el contenido de lo que el usuario traduce — ver gobernanza
  de datos arriba.
