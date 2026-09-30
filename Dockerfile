# Dockerfile (raíz del repo)
#
# Vive en la raíz (no dentro de api/) a propósito: build context =
# raíz del repositorio (necesita archivos de fuera de api/ —
# finetuning/probar_baseline.py y el adaptador entrenado — así que el
# contexto no puede ser solo api/), y ponerlo aquí evita depender de
# `-f`/`dockerfile:` en la config de compose — con "podman-compose"
# (no el nativo "podman compose") ese campo no se respeta de forma
# confiable en Windows (ver BITACORA.md Sesión 27 para el detalle
# completo del bug encontrado). Correr desde la raíz del repo:
#
#     docker build -t traductor-api .
#
# Ver api/README.md para el paso a paso completo (build, run,
# docker-compose, y por qué el modelo se descarga en el primer
# arranque en vez de venir dentro de la imagen).

FROM python:3.11-slim

WORKDIR /app

# Ninguna dependencia del sistema operativo hace falta: todos los
# paquetes de requirements.txt instalan desde wheels precompilados
# (no se necesita gcc/build-essential para compilar nada).

COPY api/requirements.txt api/requirements.txt
# --extra-index-url para instalar la build de torch SOLO-CPU (más
# liviana que la build con CUDA, y aquí no hay GPU disponible dentro
# del contenedor de todos modos) -- mismo criterio que la máquina
# local y Colab (ver CONTEXTO_PROYECTO.md, "CÓMPUTO PESADO": aquí no
# es cómputo pesado de entrenamiento, es solo instalar el paquete
# correcto para no traer ~2GB de más en binarios CUDA que nunca se
# usarían).
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu \
    -r api/requirements.txt

# Copiado explícito y puntual (no "COPY . .") de solo lo que el
# servicio necesita para correr -- ni datos crudos, ni otros
# checkpoints, ni el resto del pipeline. Ver .dockerignore para lo que
# además queda fuera del build context desde el vamos.
COPY api/main.py api/__init__.py api/
COPY finetuning/probar_baseline.py finetuning/probar_baseline.py
COPY finetuning/checkpoints/generador1/adapter finetuning/checkpoints/generador1/adapter

EXPOSE 8000

# El modelo base (~6GB) se descarga de Hugging Face en el PRIMER
# arranque del contenedor (no viene horneado en la imagen, para no
# tener una imagen de +6GB) -- por eso start-period es generoso: en
# el primer arranque, la descarga + carga del modelo puede tardar
# varios minutos según el ancho de banda.
HEALTHCHECK --interval=30s --timeout=10s --start-period=300s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/salud', timeout=5)" || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
