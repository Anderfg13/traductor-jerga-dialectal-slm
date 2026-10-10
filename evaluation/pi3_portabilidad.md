# PI3: portabilidad (tamaño, memoria, latencia y funcionamiento sin internet)

Generado por `evaluation/pi3_portabilidad.py`. Máquina: CPU, sin GPU (la de desarrollo del equipo).

## Tamaño

| Pieza | Tamaño |
|---|---|
| Modelo base Qwen2.5-3B-Instruct (bfloat16, pesos) | 6.17 GB |
| Adaptador LoRA de un generador (r=8) | 14.8 MB (0.24 % del base) |
| Adaptador de la mezcla | 14.8 MB |
| Parámetros entrenables del adaptador | 3.69 M (0.12 % de ~3.1 B) |
| Un modelo completo ya fusionado con `mergekit` (float16) | ~6.2 GB |

Cambiar de "especialización" cuesta 14.8 MB (un adaptador) y no otros 6 GB, porque el modelo base se comparte.

## Funciona sin internet

- Proceso con `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1` y **toda conexión de red bloqueada** a nivel de sockets (se cuenta cualquier `connect`/`getaddrinfo`).
- **Intentos de conexión durante la carga y la generación: 0**.
- Carga el modelo base y el adaptador desde la caché local y traduce:

| Entrada | Traducción | Latencia |
|---|---|---|
| Che, estoy remando con el sueldo que me dan. | Look, I'm struggling to make ends meet with the salary they give me. | 64.8 s |
| No hay bronca, ahorita te marco. | Don't worry, I'll call you right now. | 51.1 s |
| Estar hecho percha después de tanto laburar. | To be completely exhausted after working so hard. | 46.0 s |

- Carga "del modelo": 1.5 s y 0.51 GB de RAM, **pero es engañoso**: los pesos se mapean de forma perezosa desde disco y recién se leen a RAM durante la primera traducción, que por eso es la más lenta. La cifra que importa es la RAM tras generar: **6.69 GB** (el modelo de ~6.2 GB en bfloat16 más activaciones). Hace falta una máquina con al menos ~8 GB de RAM libre.

**Limitaciones de esta prueba**: bloquear los sockets dentro del proceso demuestra que el código de carga y generación no necesita red; no es lo mismo que desconectar físicamente la máquina. Los pesos se descargaron antes (el primer arranque sí necesita internet, una sola vez). Solo se probó el adaptador del Generador 3 en CPU, no el servicio completo ni la imagen Docker.

## Latencia (una solicitud, un texto corto)

| Entorno | Latencia | Fuente |
|---|---|---|
| CPU local, sin GPU | 46.0-64.8 s (esta prueba); 50-80 s en pruebas anteriores | esta prueba; BITACORA Sesión 25 |
| GPU T4 (Colab), modelo ajustado, una a una sobre 174 entradas | ~1.9 s por entrada (5.6 min / 174) | `finetuning/tiempos_fase3_corrida2.json` |
| GPU compartida (ZeroGPU, Space público), una solicitud | 2.5 s | `docs/despliegue.md` |

Sin GPU el modelo de 3B no es interactivo; con una GPU modesta sí.

## Cuantización int8 en CPU (prueba preliminar, 3 frases)

Generado por `evaluation/pi3_cuantizacion.py --variante int8 --n 3 --bloquear-red --medir-tam`
(cuantización dinámica de PyTorch sobre las capas lineales; se parte del modelo fusionado `peft_cat_norm`).

| Medida | bfloat16 (tabla anterior) | int8 dinámico |
|---|---|---|
| Tamaño del modelo | 6.17 GB | **4.33 GB** (−30 %, medido en disco) |
| Latencia por traducción (mediana) | 46.0-64.8 s | **28.0 s** (13.3-31.0 s) |
| Intentos de conexión con sockets bloqueados | 0 | 0 |
| RAM pico | 6.69 GB | **12.48 GB** (durante la carga y la cuantización) |
| Carga + cuantización | 1.5 s | 363.7 s (una sola vez) |

Lo que sí muestra: la latencia en CPU baja a ~la mitad, aunque sigue sin ser interactiva (13-31 s), y el modelo ocupa menos en disco.
Lo que **no** se puede concluir:

- **Calidad.** Solo se tradujeron 3 frases, y ninguno de los tres resultados acierta el sentido de la referencia
  ("Estar salado" → "I'm broke"; "Estar mosca" → "I'm stuck"; "Neta" → una respuesta con prefacio, "Sure, here's the translation..."),
  pero esa comparación **no es limpia** (el modelo de referencia de esas frases en `predicciones/` es otro, `mergekit_linear`) y 3 frases no
  son una medición. La calidad sobre las 174 entradas no se midió: según `CLAUDE.md` una evaluación completa va a Colab, y 174 × 28 s ≈ 81 min en esta máquina.
- **RAM.** La cuantización dinámica exige cargar primero el modelo completo: el pico fue casi el doble. Quien solo ejecute la versión cuantizada
  necesitaría guardarla ya cuantizada (no se hizo).
- **4 bits** (bitsandbytes/GGUF) no se probó: requiere GPU o herramientas que no están en esta máquina. Queda como trabajo futuro, no como resultado.
