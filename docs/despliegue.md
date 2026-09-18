# Despliegue del servicio de traducción

Servicio desplegado en **Hugging Face Spaces**, SDK **Gradio**,
hardware **ZeroGPU** (GPU real gratis, asignada solo durante cada
generación — ver `BITACORA.md` Sesión 26 para la comparación completa
contra Render/Railway/AWS Academy Lab y por qué se eligió esta
opción). Código fuente del Space en
[`api/space/`](../api/space/) (versión desplegable, adaptada de
`api/main.py`/FastAPI porque hospedar un Space Docker pasó a requerir
plan PRO de pago en 2026).

**URL pública**: _pendiente de completar una vez creado el Space —
ver "Pendiente" al final de este documento._

> **Bloqueo real encontrado (2026-09-18, ver BITACORA.md Sesión 26)**:
> en la pantalla de creación real (`huggingface.co/new-space`), Gradio
> y Docker aparecen con un badge **"Paid"** desde el primer paso — no
> hay forma de elegir ZeroGPU ahí para evitarlo. Confirmado que la
> causa es la antigüedad de la cuenta usada (creada 2026-09-02, menos
> de 30 días a la fecha), no el correo (ya estaba verificado). **No
> reintentar antes del 2026-10-02** con esa misma cuenta — o usar la
> cuenta de otro integrante del equipo que ya tenga +30 días.

## Prerrequisitos

- Cuenta de Hugging Face **verificada por correo** y **con más de 30
  días de antigüedad** — es requisito de Hugging Face para poder
  alojar Spaces con hardware ZeroGPU en una cuenta personal gratuita.
  Si la cuenta es más nueva, hay que esperar a que cumpla los 30 días
  o usar la cuenta de otro miembro del equipo que sí los tenga. **En
  la práctica, la pantalla de creación bloquea Gradio/Docker con un
  muro de pago sin más explicación si no se cumple esto** — no asumas
  que hay un botón o selector alternativo para evitarlo.
- Git instalado (para subir el código por `git push`) — alternativa:
  subir los archivos a mano desde la interfaz web, sin necesitar git.

## Paso 1 — Crear el Space

1. Ir a [huggingface.co/new-space](https://huggingface.co/new-space)
   (con sesión iniciada).
2. **Owner**: tu usuario (o una organización si el equipo tiene una).
3. **Space name**: ej. `traductor-jerga-dialectal`.
4. **License**: la que el equipo decida (el repo de GitHub del
   proyecto no tiene una definida todavía; se puede dejar sin
   especificar por ahora).
5. **Select the Space SDK**: **Gradio**.
6. **Space hardware**: en la creación inicial suele ofrecer "CPU
   Basic" (gratis) por default — está bien dejarlo así por ahora,
   ZeroGPU se activa en el paso 3 desde Settings (algunos flujos de
   creación sí lo ofrecen directo, en ese caso elegir **ZeroGPU** ahí
   mismo).
7. **Visibility**: **Public** (así cualquiera, incluyendo el equipo,
   puede probar la URL sin necesitar acceso especial).
8. Click **Create Space**.

## Paso 2 — Subir el código

Hugging Face crea un repositorio git vacío para el Space, en
`https://huggingface.co/spaces/<tu-usuario>/<nombre-del-space>`.

**Opción A — por la interfaz web** (más simple si no quieres usar
git): en la pestaña **Files** del Space, usar "Add file → Upload
files" y subir, respetando la misma estructura de carpetas:
- `app.py`
- `requirements.txt`
- `README.md`
- la carpeta `adapter/` completa (6 archivos: `adapter_config.json`,
  `adapter_model.safetensors`, `chat_template.jinja`, `README.md`,
  `tokenizer.json`, `tokenizer_config.json`)

Todos estos archivos ya están listos en
[`api/space/`](../api/space/) en este mismo repositorio — es subir
exactamente esa carpeta, sin modificar nada.

**Opción B — por git** (recomendado si el Space ya existe y se quiere
volver a desplegar más adelante, ver "Redesplegar" abajo):

```bash
git clone https://huggingface.co/spaces/<tu-usuario>/<nombre-del-space> espacio-hf
cp api/space/app.py api/space/requirements.txt api/space/README.md espacio-hf/
cp -r api/space/adapter espacio-hf/
cd espacio-hf
git add .
git commit -m "Desplegar servicio de traduccion"
git push
```

(La primera vez que hagas `git push` a Hugging Face te va a pedir
usuario/contraseña — usa tu usuario de HF y, como contraseña, un
**access token** generado en
[huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
con permiso de escritura, no tu contraseña real de la cuenta.)

## Paso 3 — Confirmar/activar hardware ZeroGPU

1. En el Space, ir a **Settings**.
2. En la sección **Hardware**, verificar que esté seleccionado
   **ZeroGPU**. Si no, cambiarlo ahí — es gratis, no pide tarjeta de
   crédito.

## Paso 4 — Variables de entorno / secretos (si hace falta)

**Este proyecto NO necesita ningún secreto para funcionar** — el
modelo base (`Qwen/Qwen2.5-3B-Instruct`) es público, así que no
requiere `HF_TOKEN`. Ningún archivo de `api/space/` tiene ninguna
clave ni credencial escrita — se puede confirmar buscando en el
código (`grep -r "hf_\|sk-\|token.*=.*['\"]" api/space/`, no debería
encontrar nada).

Si en el futuro hiciera falta alguna clave (por ejemplo, al cambiar al
candidato principal Llama 3.2, que sí necesita `HF_TOKEN` — ver
`BITACORA.md` Sesión 13), **nunca escribirla en el código**: en el
Space, ir a **Settings → Variables and secrets → New secret**, y
usarla desde el código como variable de entorno
(`os.environ["HF_TOKEN"]`), igual que se hace en el resto del
proyecto con `.env` local.

## Paso 5 — Esperar el build

El Space va a mostrar "Building" mientras instala las dependencias
(`requirements.txt`) y luego "Running" cuando termine — la primera vez
tarda varios minutos porque también descarga el modelo base (~6GB) la
primera vez que alguien llama a `/traducir` (o al arrancar, según la
configuración). Se puede seguir el progreso en la pestaña **Logs**.

## Paso 6 — Probar la URL pública

La interfaz web queda en
`https://<tu-usuario>-<nombre-del-space>.hf.space`. Para probar los
endpoints directamente (sin abrir la página), la API de Gradio usa un
patrón de dos pasos — se manda la solicitud, se recibe un `event_id`,
y se consulta el resultado con ese id (confirmado localmente antes de
desplegar, ver `BITACORA.md` Sesión 26):

```bash
# 1. Salud
curl -s https://<tu-usuario>-<nombre-del-space>.hf.space/gradio_api/call/salud \
  -H "Content-Type: application/json" -d '{"data": []}'
# devuelve {"event_id": "..."} -> con ese id:
curl -s https://<tu-usuario>-<nombre-del-space>.hf.space/gradio_api/call/salud/<event_id>
# devuelve: event: complete \n data: ["ok"]

# 2. Traducir
curl -s https://<tu-usuario>-<nombre-del-space>.hf.space/gradio_api/call/traducir \
  -H "Content-Type: application/json" \
  -d '{"data": ["Que chimba, parcero!", "Andina"]}'
# devuelve {"event_id": "..."} -> con ese id:
curl -s https://<tu-usuario>-<nombre-del-space>.hf.space/gradio_api/call/traducir/<event_id>
# devuelve: event: complete \n data: ["<traducción>"]
```

**La prueba de aceptación real es correr estos comandos desde una
máquina DISTINTA a la que hizo el despliegue** (para confirmar que de
verdad es un servicio público, no algo que solo funciona "en mi
máquina") — ver el resultado real en "Pendiente" abajo.

## Redesplegar si algo falla

- **El Space no arranca / error en el build**: revisar la pestaña
  **Logs** del Space — casi siempre es una dependencia faltante en
  `requirements.txt` o un error de sintaxis en `app.py`.
- **Volver a subir una versión corregida**: si se usó la Opción B
  (git), corregir el archivo en `api/space/` de este repositorio,
  copiarlo de nuevo a la carpeta clonada del Space
  (`espacio-hf/`), y repetir `git add . && git commit -m "..." && git
  push`. Cada push reconstruye el Space automáticamente.
- **El Space se "durmió" por inactividad**: en hardware gratuito
  (incluyendo ZeroGPU), un Space sin uso se pausa — la siguiente
  solicitud lo despierta sola, solo que esa primera respuesta tarda
  más (tiene que volver a cargar el modelo). No hace falta que nadie
  lo reinicie a mano.
- **Se agotó la cuota diaria de GPU** (5 min/día por cuenta
  autenticada, 2 min/día sin autenticar — ver `BITACORA.md` Sesión
  26): las solicitudes se ponen en cola hasta que se resetea 24h
  después del primer uso del día. No genera ningún cobro.

## Pendiente

- **Bloqueado hasta ~2026-10-02**: la cuenta de HF que se iba a usar
  (creada 2026-09-02) no cumple todavía el requisito de +30 días para
  la excepción gratuita de ZeroGPU — confirmado en la pantalla real de
  creación del Space (ver aviso arriba). Decisión del equipo: esperar
  con esa cuenta en vez de usar la de otro integrante (Sesión 26,
  2026-09-18) — el resto del proyecto sigue avanzando mientras tanto.
- Cuando se cumpla la fecha (o si se decide usar otra cuenta antes):
  crear el Space de verdad, subir `api/space/` (todo ya está listo, no
  necesita cambios), y completar la URL pública al inicio de este
  documento.
- Correr la prueba de aceptación real (`curl` desde una máquina
  distinta a la que despliega) y documentar aquí el resultado
  (traducción obtenida, tiempo de respuesta) una vez el Space esté
  arriba.
