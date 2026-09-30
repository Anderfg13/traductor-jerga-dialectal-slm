# Presupuesto de tiempo y cómputo

> Responde directamente al punto de la retroalimentación del profesor
> sobre la Fase 1: "completen la información pendiente sobre el tiempo
> y los recursos de cómputo disponibles". Este placeholder venía
> pendiente desde la Sesión 1 del calendario interno (nunca se llenó
> en el `.tex` original). Este documento se integra a la sección
> correspondiente del paper (Overleaf).

## Tiempo del equipo

3 integrantes (Anderson García, Paula Lozano, Mariana Malagón), cada
uno dedica aproximadamente **5-8 horas semanales** al proyecto, además
de la carga del resto de materias del curso — entre 15 y 24 horas
semanales combinadas del equipo completo.

Esto se traduce en el ritmo que ya veníamos siguiendo desde el inicio:
2 sesiones de trabajo por persona por semana (6 sesiones/semana en
total), cada sesión pensada para completarse dentro de ese presupuesto
de horas sin necesitar jornadas maratónicas. El calendario de 60
sesiones a 10 semanas fue diseñado explícitamente sobre este supuesto.

No hay dedicación exclusiva al proyecto por parte de ningún
integrante — es trabajo compaginado con el resto de la carga
académica, lo cual es relevante para entender por qué ciertas tareas
(ej. reclutar evaluadores humanos nativos, Sesión 22) tardan más en
completarse que las puramente técnicas.

## Recursos de cómputo disponibles

**Ninguna máquina del equipo tiene GPU utilizable para entrenar un SLM
de 3B**, ni siquiera con LoRA — esto no es una suposición, se confirmó
en la práctica (`BITACORA.md`, Sesión 13-14): un solo paso de
entrenamiento tardó 80-95 minutos en CPU, y a las 10 horas de correr
solo se había completado el 5% de una prueba de 150 pasos. Las
máquinas disponibles son de gama media/portátiles de uso personal, sin
GPU dedicada o con VRAM insuficiente (una GPU integrada sin CUDA real,
otra con solo 2GB de VRAM).

Por eso, **todo el cómputo pesado del proyecto corre en Google Colab,
en su capa gratuita** (GPU T4/L4, según disponibilidad del momento):

- Generación sintética: llamadas a APIs externas (Groq, Cohere, Google
  Gemini), todas en capas gratuitas — **$0 de costo** (ver
  `CONTEXTO_PROYECTO.md`, decisión documentada en Sesión 2 de
  descartar generadores de pago).
- Fine-tuning con LoRA: Google Colab gratuito — **$0 de costo**.
- Fusión de modelos (`mergekit`, Fase 3) y evaluación masiva: mismo
  esquema, Colab gratuito.

**Costo total de cómputo del proyecto a la fecha: $0.** No se ha
necesitado ni se planea contratar Colab Pro ni ningún servicio de pago
para el cómputo de entrenamiento/evaluación.

### Limitaciones que esto impone (y cómo se manejan)

- Colab gratuito desconecta el entorno por inactividad y tiene un
  límite (variable, no garantizado) de horas de GPU por día/semana por
  cuenta. El equipo lo maneja así: cada corrida pesada guarda sus
  resultados a disco tan pronto termina (adaptador, curva de pérdida,
  salidas de prueba) y se descarga de inmediato al repositorio, en vez
  de dejar resultados solo en el entorno de Colab entre sesiones — ya
  aplicado así desde la Sesión 14.
- Con 3 cuentas de Colab distintas (una por integrante) el equipo
  efectivamente triplica la cuota gratuita disponible si hace falta
  paralelizar cómputo (ej. entrenar los 3 generadores en paralelo en
  la Fase 3, cada quien en su cuenta).
- Si en algún punto el límite gratuito de Colab bloquea un
  entrenamiento crítico cerca de una entrega, la opción de respaldo
  discutida por el equipo es Kaggle Notebooks (también gratuito, GPU
  T4, cuota semanal separada de la de Colab) — no se ha necesitado
  usar todavía.
