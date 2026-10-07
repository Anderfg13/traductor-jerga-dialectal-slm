# Pendientes de despliegue y pruebas (no dependen de código nuevo)

Cosas que quedaron abiertas en las Sesiones 26, 30 y 31 y que solo
faltan **ejecutar cuando se den las condiciones**. Cada una dice qué
condición espera, el comando exacto y **dónde anotar el resultado**.
Última actualización: 2026-10-07.

> Alcance: solo lo del despliegue/pruebas de la API. Los pendientes de
> otras etapas (entrenamiento completo en Colab, evaluadores humanos,
> generadores 2 y 3, etc.) siguen en `BITACORA.md` en sus sesiones.

## 1. Latencia del Space con 20 y 50 concurrentes (modelo real)

- **Espera**: que se reinicie la cuota diaria de ZeroGPU (~24 h después
  de la prueba del 2026-10-07 ~22:00 UTC, es decir, desde el 2026-10-08
  por la tarde), y/o un token de Hugging Face con más cuota.
- **Comando** (la cuota es por IP o por token; no correr otras
  pruebas contra el Space antes):
  ```bash
  export HF_TOKEN=...   # opcional, nunca escribirlo en archivos
  python api/prueba_carga_space.py --niveles 5 20 50
  ```
- **Anotar en**: `docs/pruebas_carga.md`, sección "Resultado 3"
  (reemplazar las filas de 20 y 50, que hoy dicen 100% fallos por
  cuota) y una línea en `BITACORA.md`.
- **Qué mirar**: si las solicitudes se serializan (latencia crece
  linealmente con N) o corren en paralelo, y cuántas solicitudes caben
  antes de agotar la cuota.

## 2. Probar si bajar `duration` estira la cuota de GPU

- **Hipótesis (sin verificar)**: `@spaces.GPU(duration=30)` en
  `api/space/app.py` reserva 30 s por llamada aunque una traducción
  tarda ~2 s; el error "45s requested" sugiere que se descuenta la
  reserva.
- **Pasos**: cambiar a `duration=10` en `api/space/app.py`, copiar al
  clon del Space, `git push` (el token lo pone quien hace el push), y
  repetir el punto 1 con la cuota ya reiniciada. Comparar cuántas
  solicitudes caben con 30 vs. 10.
- **Anotar en**: `docs/pruebas_carga.md` y `BITACORA.md`.

## 3. Arranque en frío del Space dormido

- **Espera**: que el Space lleve un rato sin uso (horas) y cuota
  disponible.
- **Comando**: una sola solicitud con cronómetro, la primera después
  de la inactividad:
  ```bash
  time curl -s https://andry891-traductor-jerga-dialectal.hf.space/gradio_api/call/salud -H "Content-Type: application/json" -d '{"data": []}'
  ```
  y luego una traducción (ver `docs/despliegue.md`, Paso 6).
- **Anotar en**: `docs/despliegue.md` (sección de resultado real) con
  los segundos medidos.

## 4. E2E de 6 etapas contra el servicio desplegado en HF

- **Bloqueo (decisión del equipo)**: el Space solo expone `traducir` y
  `salud`; `/metricas` y `/retroalimentacion` existen solo en la API
  FastAPI (`api/main.py`). Las etapas 4-6 de
  `tests/test_integracion_e2e.py` no se pueden verificar en el Space tal
  cual. Opciones: (a) portar métricas y retroalimentación al Space
  (endpoints Gradio con `api_name`), o (b) aceptar que el E2E completo
  se demuestra contra la API FastAPI/contenedor, que es lo hecho el
  2026-10-07 (`docs/evidencia_e2e.log`).
- **Si se elige (a)**: hay que adaptar el script para hablar el
  protocolo de dos pasos de Gradio, y correrlo con cuota disponible.
- **Anotar en**: `docs/evidencia_e2e.log` (nuevo log) y `BITACORA.md`.

## 5. Confirmar la numeración de sesiones en la bitácora

- Las entradas "Sesión 30 (2)" y "Sesión 31 (2)" se nombraron así
  porque continúan pendientes de esas sesiones; si el calendario del
  curso les asignó otro número, renombrarlas.
