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
no solo por convención escrita. El hook también revisa que la entrada
sea real (que siga el formato mínimo "Qué se hizo: ..."), no solo que
el archivo se haya tocado — la idea es que, cerca de la entrega, se
pueda reconstruir qué pasó en cada commit sin releer el diff completo.

CÓMPUTO PESADO (FINE-TUNING, FUSIÓN, EVALUACIÓN MASIVA): SIEMPRE EN
GOOGLE COLAB, NUNCA EN LA MÁQUINA LOCAL

Confirmado en la práctica (BITACORA.md, Sesión 13-14): las máquinas
del equipo no tienen GPU utilizable para esto (una tiene GPU integrada
sin CUDA real, otra tiene solo 2GB de VRAM) — entrenar un SLM de 3B ni
siquiera con LoRA es viable en CPU (un solo paso de entrenamiento
llegó a tardar 80-95 minutos; a las 10 horas solo se había completado
el 5% de una prueba de 150 pasos). Por eso, cualquier tarea de cómputo
pesado — fine-tuning con LoRA, fusión de modelos con `mergekit`,
evaluación sobre el dataset completo, o cualquier inferencia sobre
muchos ejemplos — se corre en **Google Colab** (GPU gratuita T4/L4),
nunca en la máquina local de quien esté trabajando.

Paso a paso genérico, repetible para cualquier script pesado nuevo (no
solo el de fine-tuning):

1. Escribir el script como un `.py` normal dentro de la carpeta que
   corresponda (`finetuning/`, `merging/`, `evaluation/`), que se
   pueda correr con `python <ruta>/<script>.py` desde la raíz del
   repo — nada de lógica que dependa de estar dentro de un notebook.
2. Crear (o adaptar) un notebook de Colab en la misma carpeta, sufijo
   `_colab.ipynb` (usar `finetuning/entrenar_lora_colab.ipynb` como
   plantilla de referencia), con estas celdas en orden:
   a. `!nvidia-smi` — confirmar que hay GPU asignada (si no, primero
      hay que activarla: "Entorno de ejecución" → "Cambiar tipo de
      entorno de ejecución" → GPU).
   b. Clonar el repo con RUTAS ABSOLUTAS y solo si no existe ya
      (`%cd /content`, chequear `os.path.isdir(...)` antes de hacer
      `git clone`, `%cd` final con ruta absoluta) — evita el bug de
      clon anidado si la celda se corre más de una vez sin reiniciar
      el entorno.
   c. Instalar SOLO las dependencias puntuales que hace falta para ese
      script (`pip install -q <paquetes>`), NUNCA
      `requirements.txt` completo — Colab ya trae `torch` con CUDA
      preinstalado, y reinstalarlo desde requirements.txt puede
      romper esa integración. Si el script usa `peft`, desinstalar de
      una vez `torchao` (`pip uninstall -y -q torchao`): Colab lo trae
      preinstalado en una versión vieja que rompe `get_peft_model()`
      aunque el script no use cuantización con `torchao` para nada.
   d. Correr el script (`!python <ruta>/<script>.py`).
   e. Empaquetar y descargar los resultados
      (`!zip -rq resultados.zip <carpeta_de_salida>` seguido de
      `google.colab.files.download(...)`).
3. Dentro del script, detectar el dispositivo automáticamente
   (`device_map="auto" if torch.cuda.is_available() else "cpu"`) y NO
   cuantizar salvo que el modelo de verdad no quepa en la VRAM/RAM
   disponible — así el mismo script sirve tanto para Colab (GPU) como,
   en el peor caso, para una prueba muy pequeña en local (nunca para
   el entrenamiento/evaluación real).
4. Traer los resultados descargados de vuelta al repo local, a la ruta
   que use el script (ej. `finetuning/lora_prueba/`), revisarlos,
   documentarlos (BITACORA.md, y el `.md` de resultados que
   corresponda) y hacer commit. El `.zip` en sí NO se commitea, solo
   su contenido ya organizado en la carpeta correspondiente.

Esto aplica a lo que viene: entrenamiento completo de LoRA de los 3
generadores (Fase 2-3), fusión con `mergekit` (Sesión 44), y cualquier
evaluación que corra el modelo sobre el dataset completo.
