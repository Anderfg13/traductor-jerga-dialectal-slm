# 8. Arquitectura (Fase 2) — borrador

> Nota para el equipo: este borrador está pensado para integrarse al
> `.tex` en la Sesión 32, continuando la numeración del documento de
> Fase 1 (que cerró en la Sección 7, Conclusiones). Cada afirmación
> técnica de abajo señala entre paréntesis la sesión de `BITACORA.md`
> de la que sale — revísenlo contra la bitácora antes de dar por
> cerrado el borrador, tal como pide el criterio de aceptación de la
> Sesión 18.

En la Fase 1 dejamos la arquitectura como una visión de cuatro etapas
sin desarrollar (Figura 1 de ese documento: banco de semillas →
generación sintética → fine-tuning por fuente → fusión de modelos), a
propósito, porque esa fase se quedaba en la propuesta general. Esta
sección describe qué tanto de esa visión ya es real a la fecha de
cierre de esta entrega, y qué falta.

Como en la Fase 1, separamos la arquitectura en tres frentes: de
datos, de aplicación y de tecnología. Adelantamos algo que se repite
en las tres: **la Fase 2, según el alcance que definimos nosotros
mismos, cubre un solo generador sintético (de los tres considerados) y
deja la fusión de modelos para la fase siguiente** — no es que nos
haya faltado tiempo para los otros dos generadores, es una decisión de
alcance tomada desde el principio para poder construir y probar el
pipeline completo de punta a punta con una sola fuente de datos antes
de triplicar el trabajo.

## 8.1. Arquitectura de datos

El pipeline de datos, tal como existe hoy, tiene cinco pasos
concretos, cada uno con su propio script y su propia salida
versionada en el repositorio:

1. **Banco de semillas** (`seeds/`). Cada semilla sigue un esquema de
   6 campos — `id`, `texto_original`, `dialecto_region`, `registro`
   (formal/informal/jerga), `traduccion_referencia` y
   `nota_contexto_cultural` — con `dialecto_region` y `registro` como
   campos separados a propósito, porque dialecto (geografía) y jerga
   (formalidad) son dos dimensiones distintas que no queríamos mezclar
   en un solo dato (Sesión 3). El banco tiene hoy 105 semillas
   curadas a mano, cubriendo 5 macro-variantes del español (Caribeña,
   Andina, Rioplatense, Mexicana, Chilena — Sesiones 4 y 9), aunque
   solo las 40 semillas del primer lote (4 dialectos) han pasado por
   el resto del pipeline hasta ahora (ver más abajo).

2. **Derivación** (`generation/prompt_derivacion.md`). Es la plantilla
   de *prompt* que le pedimos a cada LLM generador para expandir una
   semilla en variantes de uso real, no en sinónimos: exige conservar
   el significado, generar entre 5 y 8 variantes por semilla variando
   contexto/registro/tono, devolver JSON estructurado, y —esto
   importa particularmente— no inventar ni mezclar el dialecto
   original con otro (Sesión 6). Diseñamos esta plantilla para que
   produzca el mismo formato de salida sin importar cuál LLM la
   reciba, precisamente para poder comparar generadores más adelante
   sin que el formato mismo sea una variable de confusión.

3. **Generación sintética** (`generation/generar_sintetico.py` +
   `consolidar.py`). Automatiza el envío de la plantilla de derivación
   a la API del generador elegido, con reintentos ante límites de
   tasa y guardado de la salida cruda por semilla antes de cualquier
   procesamiento (para no perder nada si algo falla a mitad de
   camino), y luego consolida esas salidas en un solo dataset,
   descartando variantes vacías o duplicadas exactas (Sesiones 7-8).
   Para esta fase corrimos este proceso solo con el primer generador
   (Groq, modelo `openai/gpt-oss-20b`) sobre las 40 semillas del
   primer lote, produciendo 238 variantes crudas.

4. **Validación automática** (`generation/validar.py`). Aplica 4
   reglas de filtrado sobre el dataset consolidado: longitud fuera de
   rango, variantes casi idénticas a la semilla original sin variación
   real, idioma inesperado (esta última solo marca como sospechosa,
   no descarta, porque es una heurística aproximada) y duplicados
   exactos (Sesión 11). Sobre las 238 variantes generadas, 236 (99.2
   %) pasaron el filtro, muy por debajo del límite de 20% de descarte
   que nos habíamos puesto como criterio de calidad. Vale la pena ser
   honestos sobre un hueco que encontramos: estas 4 reglas no detectan
   mezcla de dialectos dentro de una misma variante, y de hecho la
   evaluación humana piloto (Sesión 10) encontró un caso real —un
   marcador rioplatense ("che") colado en una variante etiquetada como
   andina— que sigue presente en el dataset "limpio" porque ninguna
   regla actual lo busca. Lo dejamos documentado como limitación
   conocida en `generation/data_card_generador1.md`, no lo ocultamos.

5. **Splits y data card** (`generation/split_dataset.py` +
   `data_card_generador1.md`). Dividimos el dataset limpio 80/10/10
   por semilla (no por variante, para que ninguna semilla se filtre de
   entrenamiento a evaluación) y estratificado por dialecto, con
   verificación automática de que ningún dialecto ni ninguna semilla
   queda repartida entre splits (Sesión 12): 32 semillas/189 variantes
   en entrenamiento, 4/24 en validación, 4/23 en prueba.

**Lo que todavía no existe en esta parte de la arquitectura**: el
mismo proceso para los otros dos generadores sintéticos que
consideramos, y para las 65 semillas adicionales del banco que aún no
se han generado. Ambas cosas quedan fuera del alcance de esta fase por
decisión explícita (ver más arriba). Conviene ser precisos sobre qué
tan reutilizable es el código tal como está hoy: `validar.py` y
`split_dataset.py` ya reciben la ruta del dataset como parámetro, así
que funcionan sin cambios sobre el dataset de cualquier generador.
`generar_sintetico.py`, en cambio, **todavía está escrito
específicamente para Groq** (cliente, carpeta de salida y el campo
`"generador": "groq"` quedaron fijos en el código, no parametrizados)
— adaptarlo para aceptar otro generador es trabajo explícitamente
planeado para cuando se aborden los Generadores 2 y 3, no algo que ya
esté resuelto.

## 8.2. Arquitectura de aplicación

Aquí es donde más se nota la diferencia entre lo que ya existe y lo
que la Fase 2 todavía debe entregar antes de cerrar.

**Lo que ya existe**: un conjunto de scripts de línea de comandos que
cubren de punta a punta la preparación de datos y el ajuste fino de un
SLM (`finetuning/entrenar_lora.py`), cada uno ejecutable de forma
independiente y documentado con su propio *docstring*. No hay,
todavía, ningún componente que exponga esto como un servicio: es
cómputo por lotes, pensado para correrse una vez y producir un
artefacto (un dataset, un adaptador entrenado), no para atender
solicitudes en vivo.

**Lo que la Fase 2 todavía debe entregar** (Semanas 5-6, sin empezar a
la fecha de este borrador):

- Un servicio de API REST (FastAPI) que envuelva el modelo ajustado
  con un endpoint de traducción y uno de salud.
- Despliegue de ese servicio en una plataforma en la nube accesible
  para un equipo de estudiantes, containerizado con Docker.
- Seguridad básica (límite de tasa de solicitudes, validación de
  entrada) y la garantía explícita de que el servicio no persiste ni
  registra el contenido de las traducciones, solo metadata agregada
  — coherente con el atributo de auditabilidad y no exposición de
  datos sensibles que planteamos como diferenciador de producto en la
  Fase 1.
- Observabilidad desde el diseño: métricas de calidad por dialecto,
  latencia, y un mecanismo de retroalimentación del usuario.
- Pruebas de carga que documenten cuántas solicitudes concurrentes
  soporta el servicio con cifras reales, no estimadas.

Ninguna de estas piezas existe todavía en el repositorio a la fecha de
este borrador (10 de septiembre de 2026) — las marcamos aquí
explícitamente como pendientes, no las damos por hechas, siguiendo el
mismo criterio de honestidad que nos propusimos en la Fase 1.

## 8.3. Arquitectura de tecnología

**Modelo de lenguaje pequeño**. La Fase 1 dejó tres candidatos sobre
la mesa: Llama 3.2 3B, Qwen2.5 3B y Gemma 2 2B. En la práctica,
elegimos **Qwen2.5-3B-Instruct** en vez de Llama 3.2 3B, nuestro
candidato principal original, porque el repositorio de Llama en
HuggingFace requiere aprobación manual de Meta (`gated="manual"`) y la
solicitud de acceso no se había resuelto al momento de necesitar el
modelo (Sesión 13). No es un cambio de rumbo respecto a lo que
planteamos en la Fase 1 —Qwen2.5 3B ya estaba entre los candidatos
declarados—, es simplemente que el orden de preferencia original
resultó bloqueado por un trámite externo, no por un criterio técnico
nuestro. Si el acceso a Llama se aprueba más adelante, el mismo script
de entrenamiento reproduce la prueba cambiando solo el identificador
del modelo.

**Precisión y cómputo**. Cargamos el modelo en `bfloat16` sin
cuantizar (no en 4-bit u 8-bit): confirmamos que un modelo de 3B en
esa precisión pesa entre 6 y 6.5GB, que cabe cómodo tanto en la VRAM
de una GPU gratuita de Google Colab como en la RAM de las máquinas del
equipo — el cuello de botella real nunca fue la memoria disponible,
sino la ausencia de una GPU utilizable en las máquinas locales del
equipo (un solo paso de entrenamiento LoRA llegó a tardar 80-95
minutos en CPU; a las 10 horas solo se había completado el 5% de una
prueba de 150 pasos). Por eso todo el cómputo de ajuste fino se corre
en Google Colab (GPU T4/L4 gratuita), nunca en máquina local — una
política que dejamos por escrito para el resto del proyecto, no solo
para esta prueba puntual (Sesión 14, `CONTEXTO_PROYECTO.md`).

**Técnica de ajuste fino: LoRA**. Elegimos LoRA sobre ajuste fino
completo por la misma razón de fondo que motivó elegir un SLM en
primer lugar: mantener el costo de entrenamiento y el tamaño del
artefacto resultante bajos, alineado con el objetivo de portabilidad
del proyecto. La configuración usada en la prueba de humo (Sesión
14-15) fue:

| Hiperparámetro | Valor | Por qué |
|---|---|---|
| `r` (rango) | 8 | Capacidad modesta, apropiada para un modelo ~3B con un dataset chico; mantiene el adaptador liviano. |
| `lora_alpha` | 16 | Heurística estándar `alpha = 2r`, para que siga siendo válida si `r` cambia al escalar el entrenamiento. |
| `lora_dropout` | 0.05 | Regularización barata contra sobreajuste — relevante porque ya observamos un indicio de sobreajuste con este mismo valor (ver abajo). |
| `bias` | `"none"` | Default estándar de LoRA para modelos de lenguaje causales. |
| `target_modules` | proyecciones de atención Q/K/V/O | Es donde más impacto tiene adaptar el modelo a una tarea nueva, sin tocar las capas MLP, para un adaptador más chico y un entrenamiento más rápido. |

**Formato de instrucción**. Cada ejemplo se arma como una conversación
de sistema/usuario/asistente usando la plantilla de chat nativa del
tokenizador (`apply_chat_template`), con el mismo *prompt* de sistema
en entrenamiento y en inferencia —importan del mismo módulo, así que
no se pueden desincronizar sin que alguien lo note— y con la pérdida
enmascarada (`-100`) sobre los tokens del *prompt*, de forma que solo
se entrena sobre los tokens de la respuesta esperada (Sesión 17).
Verificamos esto con un ejemplo real del dataset: el texto decodificado
de los tokens coincide, carácter por carácter, con el texto antes de
tokenizar, y decodificar solo los tokens no enmascarados reconstruye
exactamente la traducción de referencia. También agregamos un límite
de longitud (512 tokens) que trunca desde el inicio del *prompt*, no
desde el final, si algún ejemplo resultara excepcionalmente largo —hoy
no se activa con nuestros datos (la secuencia más larga mide 125
tokens), pero preferimos dejarlo manejado explícitamente a que el
entrenamiento fallara sin control el día que un dataset futuro traiga
un ejemplo largo.

**Resultado de la prueba de humo end-to-end**. Con esta configuración,
entrenamos sobre un subconjunto de 50 ejemplos durante 3 épocas en
Colab: la pérdida bajó de forma consistente (1.011 → 0.458 → 0.263
entre la primera y la última época), el adaptador se guardó y se
recargó desde disco correctamente, y sobre los mismos 8 ejemplos de
prueba usados para la línea base sin ajustar, las 8 traducciones
cambiaron respecto al modelo sin ajustar, con mejoras claras en 2-3 de
los 8 casos (Sesión 14). No maquillamos el resultado: el error más
sistemático de la línea base ("tinto" traducido como vino en vez de
café) no se corrigió, porque la semilla correspondiente cayó en el
split de prueba y no en los 50 ejemplos de entrenamiento — comportamiento
esperado de una prueba de humo con tan pocos datos, no un defecto del
pipeline. Tampoco ocultamos un hallazgo a vigilar: dos ejemplos
distintos de prueba produjeron exactamente la misma salida, posible
indicio de sobreajuste con tan pocos ejemplos y épocas, que dejamos
como algo a monitorear cuando entrenemos con el dataset completo.

## 8.4. Resumen de lo pendiente en esta fase

Para que quede en un solo lugar, sin repetir lo ya dicho arriba: a la
fecha de este borrador faltan, dentro del alcance ya comprometido para
la Fase 2, el servicio de API, su despliegue en la nube, la
containerización, la seguridad básica y la observabilidad (Semanas
5-6). El entrenamiento completo sobre el dataset entero (no solo el
subconjunto de la prueba de humo), la comparación contra la línea base
sin ajustar, y la evaluación automática y humana a escala completa
también quedan para las próximas sesiones dentro de esta misma fase
(Semana 4). La comparación entre los tres generadores sintéticos y la
fusión de modelos quedan fuera del alcance de esta fase por decisión
explícita, no por limitación técnica, y se retoman más adelante en el
proyecto.
