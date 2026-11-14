# Traductor de jerga y dialectos del español → inglés

**Resumen ejecutivo — una página, sin tecnicismos.**

## El problema

Los traductores automáticos de uso general (Google Translate, DeepL, ChatGPT)
funcionan bien con el español "de libro", pero fallan con jerga y dialectos
regionales: traducen literal y a veces invierten el significado. No es un
problema menor — en 1980, a un paciente en Florida le tradujeron mal una sola
palabra ("intoxicado") y quedó cuadripléjico; el hospital pagó 71 millones de
dólares de indemnización. Hoy, en 2026, este tipo de error sigue sin
resolverse: ningún traductor comercial está diseñado específicamente para
jerga regional del español.

## Lo que construimos

Un servicio de traducción especializado en jerga y dialectos del español
(caribeño, andino, rioplatense, mexicano, chileno), ajustado a partir de un
modelo de lenguaje pequeño y barato de operar, entrenado con datos generados
por tres proveedores de IA distintos y luego combinado en un solo modelo.

## Por qué es distinto de lo que ya existe

| | Google Translate / DeepL / ChatGPT | Nuestro traductor |
|---|---|---|
| Internet | Obligatorio | No obligatorio, corre localmente |
| Datos sensibles | Salen a la nube de un tercero | Nunca salen, nunca se guardan |
| Personalización | Caja negra | Se puede reentrenar por cliente |
| Auditabilidad | No se sabe con qué se entrenó | Origen de cada dato documentado |
| Costo a gran escala | Pago por llamada a un modelo grande | Modelo pequeño, barato de operar |

## Evidencia de que funciona (no promesas, medido)

- **Servicio público real**, desplegado y probado en vivo: traduce una frase
  en ~2-3 segundos con GPU, o localmente sin ninguna conexión a internet.
- Ajustar el modelo mejora la calidad de traducción de forma medible
  (de 37 a 44 puntos en una escala estándar de calidad de traducción), un
  salto comparable al que separa a un modelo gratuito de uno comercial.
- Al nivel de calidad de un traductor comercial pago (DeepL) en una de las
  dos métricas que usamos, y un poco por debajo en la otra — competitivo,
  no superior, a una fracción del costo.
- Soporta hasta 50 solicitudes al mismo tiempo sin caerse ni degradarse
  (verificado con pruebas de carga reales contra el servicio desplegado).
- **Costo total del proyecto hasta hoy: \$0** — todo construido con niveles
  gratuitos de cómputo e IA.

## Lo que todavía falta antes de un piloto real

1. **Evaluación con hablantes nativos reales** (en curso) — las métricas
   automáticas no capturan si se conserva el tono y la intención, solo si
   las palabras coinciden con una referencia.
2. Ampliar el conjunto de prueba (hoy cubre 9 expresiones representativas).
3. Definir, junto con un cliente real, un modelo de responsabilidad para
   casos de alto riesgo (salud, justicia): recomendamos que el sistema
   asista a una persona, no que decida solo.

## En una frase

Un traductor de jerga regional del español, gratis de construir, que
corre sin depender de internet ni exponer datos sensibles, con calidad ya
medida y comparable a una alternativa comercial — listo para un piloto
supervisado, no todavía para una decisión automática sin revisión humana.
