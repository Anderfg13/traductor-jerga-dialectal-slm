---
title: Traductor Jerga Dialectal
emoji: 🗣️
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
---

# Traductor de jerga y dialectos del español → inglés

Traduce expresiones dialectales/de jerga del español al inglés,
conservando el significado real (no traducción literal). Modelo base
Qwen2.5-3B-Instruct + adaptador LoRA entrenado sobre datos sintéticos
del Generador 1 (proyecto TDSE — ver
[repositorio en GitHub](https://github.com/Anderfg13/traductor-jerga-dialectal-slm)
para el pipeline completo: generación sintética, fine-tuning,
evaluación).

Corre en hardware **ZeroGPU** (GPU real asignada solo durante cada
generación, gratis para cuentas personales de Hugging Face).

## Endpoints de la API

Además de la interfaz web, Gradio expone estas funciones como API:

- `traducir(texto, dialecto)` → traducción (dialecto es opcional e
  informativo).
- `salud()` → `"ok"`, para confirmar que el servicio está vivo.

Ver `docs/despliegue.md` en el repositorio del proyecto para ejemplos
de cómo llamarlas con `curl`/Python desde fuera de la interfaz web.
