# Limitaciones, riesgos y gobernanza (borrador para el paper)

Borrador para la sesión de limitaciones. Cada limitación remite a la fuente donde
está documentada. Está redactado para que el equipo lo revise; no suaviza ni
exagera lo que el repositorio muestra.

## 1. Limitaciones de los datos

- **Referencias sintéticas.** 165 de las 174 entradas del conjunto de prueba tienen como referencia la
  salida de otro LLM, no de hablantes nativos. Solo las **9 "oro"** (una por semilla
  de prueba) son referencias humanas. Todo BLEU/chrF
  mide cercanía a lo que escribió otro modelo, no corrección ante un hablante nativo.
  (`evaluation/test_comun.json`; `docs/resultados_fase3.md`.)
- **Banco pequeño.** 100 semillas en 5 dialectos, con 1-2 expresiones por dialecto
  en el conjunto de prueba. No se puede separar "dialecto" de "expresión".
  (`docs/alcance_banco_semillas.md`; `evaluation/analisis_cualitativo.md`.)
- **Generador 3 es un modelo "lite"** (Google, versión ligera) elegido por cuota
  gratuita, no por calidad. Los tres generadores son tres LLM distintos, pero ninguno
  es un hablante nativo.
- **Filtrado automático casi no filtra.** Descartó 2 de 589 (G1), 0 de 632 (G2) y 0
  de 625 (G3): sirve para detectar defectos de formato, no de naturalidad dialectal
  (`generation/reporte_filtrado*.md`).

## 2. Limitaciones del diseño experimental

- **Conjunto de prueba común de 9 semillas / 174 entradas.** Los intervalos de
  confianza (bootstrap por semilla) son amplios; se hicieron decenas de
  comparaciones sin corrección por comparaciones múltiples. Casi todas las
  diferencias entre modelos fusionados (43.7-44.2 BLEU) **no son distinguibles**.
- **Una corrida por modelo, una semilla de entrenamiento.** No se midió la
  variabilidad entre corridas del propio entrenamiento.
- **Sobreajuste rápido.** En todos los entrenamientos la mejor época fue la 1
  (`finetuning/curva_final_*.md`): con pocos datos el modelo se ajusta enseguida.
- **Sesgo de circularidad.** Parte de las comparaciones con LLM generales
  (`docs/resultados_pi3.md`) usa referencias producidas por LLM; los modelos del
  mismo tipo pueden verse favorecidos.
- **Sin evaluación humana.** A la fecha **no hay evaluadores ni resultados
  humanos** (`evaluation/evaluadores.csv` vacío; `evaluation/resultados_humanos_pi1.csv`
  no existe). PI1 queda con respuesta parcial (solo métricas automáticas) y el
  kappa no pudo calcularse. Es la limitación más importante.

## 3. Errores propios que se corrigieron durante el proyecto

Se dejan escritos porque afectan cómo leer los resultados (`BITACORA.md`):

- Las primeras corridas de Colab (G1) reutilizaron un adaptador antiguo: se
  descartaron y el cuaderno ahora fuerza el reentrenamiento y verifica el número de
  ejemplos.
- Se atribuyó el fallo del promedio con PEFT (35.3 BLEU) a "términos cruzados";
  el aislamiento (`merging/analisis_lineal_peft.md`) mostró que era sumar con pesos
  1.0 en vez de promediar: normalizado da 43.6 BLEU.
- Se afirmó que la destilación superaba a la mezcla; el análisis con intervalos
  mostró que no se distinguen.
- Se dijo que los adaptadores "memorizaban"; con pérdida de entrenamiento de
  0.54-0.84 y mejor época 1 eso no se sostiene.

## 4. Limitaciones técnicas y de despliegue

- **Cuota de GPU del Space** (ZeroGPU): hay límite de uso diario; la carga de 20 y 50
  concurrentes y el arranque en frío no se midieron (`docs/pendientes_despliegue.md`).
- **Uso en CPU sin cuantizar es impracticable**: 46-65 s por traducción
  (`evaluation/pi3_portabilidad.md`). Ver ese documento para la cuantización.
- **Métricas y retroalimentación** solo existen en la API local, no en el Space.
- Sin pruebas de seguridad más allá de las de la Fase 2 (`docs/despliegue.md`).

## 5. Riesgos

| Riesgo | Descripción | Mitigación actual |
|---|---|---|
| Malinterpretar la jerga | El modelo confunde sentidos regionales (p. ej. "mosca", "pedo", "mala leche") y puede producir una traducción con otro significado. | Documentado con ejemplos reales (`evaluation/analisis_cualitativo.md`). No usar para contextos críticos (legales, médicos). |
| Contenido ofensivo | Parte de la jerga es vulgar o insultante; el modelo puede traducirla sin advertir. | Sin filtro de contenido propio; pendiente decidir una política. |
| Estereotipos regionales | Datos sintéticos de LLM pueden reproducir estereotipos sobre dialectos. | Revisión humana solo de las 9 "oro"; faltan evaluadores nativos. |
| Sesgo de cobertura | Solo 5 dialectos; ausencia de otros (p. ej. centroamericano, español peninsular). | Declarado como alcance (`docs/alcance_banco_semillas.md`). |
| Privacidad | Las traducciones se envían a la API/Space. | No verificado en esta fase qué se registra de las solicitudes; confirmar y publicar una política antes de promocionar el servicio. |
| Licencia y términos de uso | Datos generados con APIs gratuitas de terceros (Groq, Cohere, Google) bajo sus términos. | Sin verificación legal formal de la redistribución del dataset: **pendiente de revisar con el equipo**. |
| Dependencia de servicios gratuitos | Cuotas y condiciones pueden cambiar. | Los artefactos (adaptadores, modelo destilado) están versionados en el repositorio. |

## 6. Gobernanza

El modelo de gobernanza (roles, datos, modelos, proceso) está en
`docs/modelo_gobernanza.md`. En esta fase se aplicó así: decisiones registradas en
`BITACORA.md` por commit; hook local que exige entrada de bitácora; evaluación
humana a ciegas con clave guardada fuera de git y su hash (SHA-256) publicado; y
declaración explícita de qué resultados son preliminares.

**Qué falta confirmar como equipo:** política de contenido ofensivo, verificación
de licencias de los datos sintéticos y si el modelo/adaptador se publica con tarjeta
de modelo y advertencias de uso.
