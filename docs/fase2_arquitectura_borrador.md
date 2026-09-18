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

**Entrenamiento completo (Sesión 19-20), ya corrido — actualiza lo de
arriba**. Con el mismo script (`entrenar_lora.py --todos`) y la misma
configuración de LoRA, entrenamos sobre las 189 variantes completas de
`train.json`, con validación sobre `val.json` en cada época y
selección automática del mejor checkpoint
(`load_best_model_at_end` + `EarlyStoppingCallback`), no del último —
precisamente para no repetir a ciegas el indicio de sobreajuste que ya
habíamos visto en la prueba de humo. **Y en efecto se detectó
sobreajuste real**: la pérdida de validación subió a partir de la
época 2 mientras la de entrenamiento seguía bajando, así que el
entrenamiento se detuvo ahí y se quedó con el adaptador de la época 1
(la de mejor validación) como checkpoint final — el mecanismo funcionó
exactamente para lo que se diseñó.

Comparamos ese checkpoint final contra la línea base sin ajustar sobre
los mismos 8 ejemplos de prueba de siempre
(`evaluation/comparacion_base_vs_ajustado.md`): mejoras reales y
consistentes en el registro dialectal ("está brutal" → "brutal"
literal en la base, "awesome"/"insane" en el ajustado; "estoy remando"
→ "rowing" literal en la base, "barely getting by"/"struggling" en el
ajustado), pero **el caso de "tinto" (café) traducido como "vino"
sigue sin corregirse** incluso con el dataset completo, porque esa
semilla específica cayó en el split de prueba y nunca estuvo en
entrenamiento — no es un defecto del pipeline, es la consecuencia
esperada y correcta de mantener un conjunto de prueba genuinamente
independiente (ver más abajo). Seguimos sin maquillar resultados: un
adaptador con solo una época efectiva de entrenamiento útil es un
punto de partida razonable, no un modelo terminado, y así lo dejamos
dicho en la propia comparación.

**Sobre el conjunto de prueba independiente** (respuesta directa a un
punto que el profesor pidió reforzar): el split de la Sesión 12 separa
por **semilla completa**, no por variante individual — todas las
variantes generadas a partir de una misma semilla quedan en el mismo
split, verificado automáticamente. Esto significa que ninguna
expresión del conjunto de prueba, ni ninguna de sus paráfrasis
sintéticas, fue vista de ninguna forma durante el entrenamiento; el
modelo tiene que generalizar el patrón de traducción dialectal a
semillas genuinamente nuevas, no solo reconocer una variante de algo
ya memorizado. El caso de "tinto" de arriba es evidencia empírica de
que esta independencia es real: si hubiera fuga de datos entre splits,
ese error probablemente ya se habría corregido.

## 8.4. Resumen de lo pendiente en esta fase

Para que quede en un solo lugar, sin repetir lo ya dicho arriba: a la
fecha de esta actualización (17 de septiembre de 2026) el entrenamiento
completo, su comparación honesta contra la línea base, y el formato de
instrucción ya están cerrados (Sesiones 17, 19, 20). Falta, dentro del
alcance ya comprometido para la Fase 2: la evaluación automática
(BLEU/chrF) y humana a escala completa (Sesiones 21-24), y el servicio
de API, su despliegue en la nube, la containerización, la seguridad
básica y la observabilidad (Sesiones 25-30) — nada de esto existe
todavía en el repositorio. La comparación entre los tres generadores
sintéticos y la fusión de modelos quedan fuera del alcance de esta
fase por decisión explícita, no por limitación técnica, y se retoman
en la Fase 3.

## 8.5. Hoja de ruta (roadmap)

| Cuándo | Qué | Sesiones |
|---|---|---|
| Ya cerrado | Banco de semillas, generación sintética, validación, splits, fine-tuning completo del Generador 1, comparación honesta vs. línea base | 3-20 |
| Próximos ~7 días | Evaluación automática (BLEU/chrF) y humana a escala completa; servicio de API (FastAPI) | 21-26 |
| Próximos ~15 días (cierre de Fase 2) | Containerización, seguridad básica, observabilidad, pruebas de carga, pruebas de integración e2e, compilación final del paper de Fase 2 y sustentación | 27-36 |
| Fase 3 (semanas 7-10) | Generadores 2 y 3, fusión simple (TIES/DARE) y por destilación multi-maestro, comparación completa PI1/PI2/PI3 | 37-60 |

Esta hoja de ruta asume el presupuesto de tiempo declarado en
`docs/presupuesto_tiempo_computo.md` (5-8h/semana por integrante) y
que el cómputo pesado sigue corriendo sobre Colab gratuito sin
bloqueos de cuota.

## 8.6. Alcance de datos y gobernanza

Dos piezas que la Fase 1 dejó abiertas y que se cierran formalmente en
esta entrega, con su propio documento porque son transversales a las
tres arquitecturas de arriba, no solo a la de datos:

- **Alcance declarado del banco de semillas** — qué dialectos y qué
  tipos de expresión cubre el proyecto, y cuáles se excluyen a
  propósito y por qué: `docs/alcance_banco_semillas.md`.
- **Modelo de gobernanza** — roles y decisiones del equipo, gobernanza
  de datos, de modelos, y de proceso/código, y riesgos éticos
  identificados: `docs/modelo_gobernanza.md`.
