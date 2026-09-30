# 9. Evidencia de prototipo (Fase 2) — borrador

> Nota para el equipo: continúa la numeración después de "8.
> Arquitectura" (`docs/fase2_arquitectura_borrador.md`). Cada cifra de
> este documento está sacada textualmente de `docs/pruebas_carga.md`
> o de `docs/despliegue.md` — no se estima ni se redondea nada de
> memoria, siguiendo el criterio de aceptación de la Sesión 33.

## 9.1. El servicio construido

El prototipo de esta fase es un servicio de traducción vía **API
REST** (`api/main.py`, FastAPI), no un script de entrenamiento local:
expone `POST /traducir`, `GET /salud`, `GET /metricas` y `POST
/retroalimentacion`, con el modelo cargado una sola vez al iniciar el
proceso, no por solicitud.

**Seguridad y privacidad** (Sesión 28): límite de tasa de 10
solicitudes/60 segundos por cliente, validación de entrada (texto
obligatorio, no vacío, máximo 500 caracteres), y ninguna llamada en
todo el código que escriba a disco o a un log externo el texto de una
solicitud o de una traducción — verificado explícitamente en
`api/test_main.py::test_metricas_solo_expone_contadores_agregados`.

**Observabilidad** (Sesión 29): `GET /metricas` reporta, por cada
dialecto solicitado, cuántas solicitudes tuvo, su latencia promedio, y
la tasa de retroalimentación positiva recibida vía `POST
/retroalimentacion` — sin guardar nunca el texto de ninguna solicitud
individual.

**Contenerización** (Sesión 27): `Dockerfile` y `docker-compose.yml`
en la raíz del repositorio, probados de punta a punta con Podman en
Windows (Docker Desktop no se pudo instalar en la máquina usada) —
`podman build` sin errores, contenedor levantado respondiendo `GET
/salud` en ~36ms y `POST /traducir` con una traducción real y
coherente en 33.8s.

## 9.2. Evidencia de que funciona de punta a punta, con el modelo real

No es un prototipo solo probado con mocks. Se levantó el servicio con
el modelo real (Qwen2.5-3B-Instruct + adaptador LoRA del Generador 1)
en la máquina local, sin GPU, y se confirmó con `curl`:

- `GET /salud` → `200 {"estado":"ok"}` en ~7ms.
- `POST /traducir` con `"Que chimba, parcero!"` → `200
  {"traduccion":"That's awesome, buddy!",...}` en **79.4s** (primera
  solicitud, con el costo de arranque en frío).
- Una segunda solicitud → **49.8s**.

**Las traducciones son correctas y coherentes — el problema medido es
latencia, no funcionalidad.** Esta cifra (50-80s por solicitud en CPU)
es la razón directa por la que el despliegue de esta fase busca
hardware con GPU real (ver 9.3), no una limitación oculta: se reporta
aquí explícitamente porque no cumple el objetivo de latencia del
proyecto tal cual, sin GPU.

## 9.3. Despliegue en la nube (Sesión 26) — en curso, bloqueado por un requisito externo, no técnico

Plataforma elegida: **Hugging Face Spaces**, SDK **Gradio**, hardware
**ZeroGPU** (GPU real asignada solo durante cada generación, gratis
para cuentas personales verificadas con más de 30 días de antigüedad).
Se descartaron **Render** (free tier de 512MB RAM, insuficiente para
un modelo de ~6.5GB) y **Railway** (ya no tiene free tier permanente
en 2026); también se evaluó **AWS Academy Learner Lab**, descartado
porque la sesión se apaga sola a los 40 minutos y los créditos
restantes se comparten con el resto del curso.

El código de despliegue (`api/space/app.py`, reescritura en Gradio del
mismo servicio, con el adaptador incluido) **ya está listo y
verificado localmente** — probado con `curl` real contra la app de
Gradio corriendo en la máquina de desarrollo, `salud` en ~1.6s y
`traducir` en 68s (consistente con la falta de GPU real fuera de un
Space verdadero). **Lo que falta no es código, es un requisito
externo**: la cuenta de Hugging Face usada para preparar esto tiene
menos de 30 días de antigüedad (creada 2026-09-02), y Hugging Face
exige esa antigüedad para la excepción gratuita de ZeroGPU en cuentas
personales — confirmado en la práctica el 2026-09-18, cuando la
pantalla de creación del Space mostró un muro de pago (`"Paid"`) para
Gradio/Docker sin ninguna opción visible de activar ZeroGPU antes de
esa fecha. El equipo decidió esperar con su propia cuenta (no usar la
de otro integrante para saltarse el requisito) y retomar el despliegue
real a partir del **2026-10-02**, sin bloquear el resto del proyecto
mientras tanto (`docs/despliegue.md`).

## 9.4. Pruebas de carga (Sesión 30)

Con el rate limiting por default (10 solicitudes/60s por IP,
`docs/pruebas_carga.md`), una ráfaga de solicitudes concurrentes
confirma el comportamiento diseñado: de 25 solicitudes mandadas en
niveles de 5 y luego 20 concurrentes, las primeras 10 en total pasan y
el resto recibe `429 Too Many Requests` — la protección contra abuso
funciona bajo carga real, no solo en pruebas unitarias.

Con el límite de tasa desactivado, para medir la capacidad de
concurrencia de la capa de API por separado: **0% de errores en 5, 20
y 50 solicitudes concurrentes**, con latencia promedio subiendo de
forma moderada (0.71s → 0.94s → 1.30s) — usando una traducción
simulada de 0.3s, no el modelo real (ver la limitación explícita
abajo).

**Limitación declarada, no oculta**: la prueba de carga mide la capa
de API (FastAPI, rate limiting, métricas), no el sistema completo con
el modelo real cargado. Con el modelo real, múltiples generaciones
concurrentes sobre el mismo objeto de modelo probablemente se
serializan (no hay paralelismo real dentro de un solo proceso/GPU) —
el número de "solicitudes concurrentes que el sistema completo
aguanta" con el modelo real no se pudo medir sin GPU, y no se reporta
un número inventado en su lugar.

## 9.5. Qué cubre este MVP y qué queda para Fase 3

Consistente con el alcance declarado desde la Fase 1 (Sección 4 del
paper) y reafirmado en la arquitectura (Sección 8): este prototipo
cubre **un solo generador sintético** (Groq/Generador 1) y **ninguna
técnica de fusión de modelos** todavía — es la fusión simple
(TIES/DARE vía `mergekit`) la que abre la Fase 3, junto con repetir
todo este mismo pipeline para los Generadores 2 y 3. La evaluación
humana formal (Sesión 22-24) también queda pendiente: existen los
artefactos para reclutarla y calificarla (`evaluation/reclutamiento_evaluadores.md`,
`evaluation/rubrica_humana.md`) pero no evaluadores reales confirmados
todavía — no se reporta ningún resultado de evaluación humana en el
paper que no venga de personas reales (ver Sección 10, resultados).
