PROYECTO: Traductor especializado en jerga y dialectos del español-inglés
mediante ajuste fino de un modelo de lenguaje pequeño (SLM) sobre datos
sintéticos generados por múltiples LLMs, con fusión de modelos.

EQUIPO: Anderson García, Paula Lozano, Mariana Malagón.
CURSO: TDSE — Transformación Digital y Sistemas Empresariales.

PREGUNTAS DE INVESTIGACIÓN:
- PI1: ¿Cómo afecta el LLM usado para generar datos sintéticos a la
  calidad de la traducción de un SLM ajustado?
- PI2: ¿Puede la fusión de pesos (simple o guiada por destilación
  multi-maestro) consolidar el conocimiento de varios SLMs entrenados
  con datos sintéticos de distintas fuentes, igualando o superando al
  mejor modelo individual?
- PI3: ¿Es posible obtener un modelo pequeño y eficiente, competitivo
  frente a sistemas de propósito general, y portable (corre sin
  internet constante)?

PIPELINE (4 etapas):
1. Banco de semillas: expresiones dialectales/jerga + traducción correcta.
2. Generación sintética: 3 LLMs generadores distintos expanden las
   semillas de forma independiente ("derivación": variantes de
   contexto, registro y tono).
3. Fine-tuning: un SLM candidato (Llama 3.2 3B / Qwen2.5 3B / Gemma 2
   2B) ajustado con LoRA, uno por cada fuente sintética.
4. Fusión: TIES/DARE simple vía `mergekit`, y fusión guiada por
   destilación multi-maestro, comparadas entre sí y contra el mejor
   modelo individual y un modelo entrenado sobre la mezcla completa.

ALCANCE POR FASE:
- Fase 2 (semanas 1-6 de este calendario): arquitectura completa +
  prototipo MVP con UN SOLO generador sintético y UNA sola técnica de
  fusión (simple), desplegado como servicio en la nube vía API.
- Fase 3 (semanas 7-10): comparación completa de los 3 generadores,
  las 2 técnicas de fusión, resultados cuantitativos y cualitativos.

ARQUITECTURA OBJETIVO: servicio desplegable en la nube, expuesto por
API REST, NO un script local. Con observabilidad (métricas de calidad
por dialecto, latencia), pensado para poder correr en hardware modesto
y sin conexión constante a internet (portabilidad).

ATRIBUTOS DE CALIDAD A EVALUAR: (i) calidad de traducción (BLEU, chrF,
evaluación humana de retención de matices con mínimo 3 hablantes
nativos por dialecto, acuerdo entre evaluadores con kappa de Cohen/
Fleiss); (ii) eficiencia (tamaño, latencia); (iii) efecto del generador
sintético (PI1); (iv) efectividad de la fusión (PI2); (v) portabilidad
(PI3).

DIFERENCIACIÓN DE PRODUCTO (frente a Google Translate/DeepL/ChatGPT):
no requiere internet constante, los datos sensibles no salen a una
nube de terceros, es personalizable por cliente, es auditable, y es
barato de correr a escala por ser un modelo pequeño.

ALTERNATIVA NO-IA CONSIDERADA: glosario/diccionario curado por
dialecto — descartada como solución única porque no generaliza a
construcciones nuevas.

ESTADO DEL ARTE (vacío identificado): existe traducción dialectal vía
fine-tuning para otros idiomas (libanés, aromanian, šariš) y jerga
en-zh, pero no para español (solo hay reconocimiento/clasificación).
Existe comparación de generadores sintéticos en clasificación y
diálogo médico, pero no aplicada a traducción. Existe fusión de
modelos entrenados con datos de distintas fuentes en clasificación,
pero no en traducción; la fusión multilingüe estándar es frágil.

CONVENCIONES DE CÓDIGO: Python, entorno gestionado con
requirements.txt (o poetry si el equipo lo prefiere), un notebook o
script por etapa del pipeline dentro de carpetas separadas
(seeds/, generation/, finetuning/, merging/, evaluation/, api/).
Todo commit relevante va acompañado de una entrada en BITACORA.md —
regla exigida técnicamente por un git hook local
(`.githooks/pre-commit`, ver README.md "Instalación del entorno"),
no solo por convención escrita.
