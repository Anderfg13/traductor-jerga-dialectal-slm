# Guion de demo — sustentación de Fase 2 (Sesión 34)

Objetivo: 2-3 minutos, mostrar el prototipo funcionando de verdad, no
solo diapositivas.

## Restricción real que condiciona todo el guion

El servicio responde en **50-80 segundos por traducción sin GPU**
(medido en la Sesión 25/27, `api/README.md`). Eso es más de la mitad
del tiempo total del guion si se espera una respuesta en vivo sin
preparar nada antes. **El guion está diseñado alrededor de esta
restricción real, no ignorándola.**

Antes del día de la sustentación, confirmar cuál de estos dos
escenarios aplica y ajustar el Paso 3 según corresponda:

- **Si para esa fecha el despliegue en Hugging Face Spaces con ZeroGPU
  ya está activo** (posible desde el 2026-10-02, ver
  `docs/despliegue.md`): la latencia baja a segundos, no a minutos —
  usar la URL pública en vivo sin necesidad del Plan B.
- **Si todavía no está desplegado**: seguir el guion tal como está
  (con la solicitud lanzada ANTES de empezar a hablar).

## Guion (2:30 aprox.)

**[0:00-0:20] Gancho + contexto**
> "Google Translate y ChatGPT traducen bien el español estándar. Pero
> si les dices 'dar papaya' o 'qué chimba', o 'estoy remando' con el
> sueldo, la mayoría los traduce literal y pierde el sentido. Eso es
> justo lo que construimos: un modelo pequeño, ajustado con datos
> sintéticos, especializado en jerga y dialectos."

**[0:20-0:35] Lanzar la solicitud YA (antes de seguir hablando)**
Ejecutar en terminal, visible en pantalla, y seguir hablando mientras
corre en segundo plano:
```bash
curl -X POST http://localhost:8000/traducir \
  -H "Content-Type: application/json" \
  -d "{\"texto\": \"Che, estoy remando con el sueldo que me dan.\", \"dialecto\": \"Rioplatense\"}"
```

**[0:35-1:20] Mientras se espera la respuesta: arquitectura, en voz**
> "Mientras esa solicitud corre, así es como llega hasta ahí: una API
> en FastAPI, con un límite de solicitudes por minuto para evitar
> abuso, valida que el texto no esté vacío ni sea gigante, y el modelo
> —un Qwen de 3 mil millones de parámetros, ajustado con LoRA sobre
> datos sintéticos de jerga dialectal— genera la traducción. Todo esto
> corre sin depender de una API externa como OpenAI: el modelo vive
> acá, se puede desplegar sin internet constante, y nunca guardamos el
> texto de nadie — solo métricas agregadas, como latencia y cuántas
> traducciones salieron bien, por dialecto."

**[1:20-1:35] La respuesta llega**
> "Ahí está: 'estoy remando' se traduce como *'I'm barely scraping
> by'*, no como *'I'm rowing'* — que es lo que dice el modelo sin
> ajustar." (Mostrar en pantalla la comparación de
> `evaluation/comparacion_base_vs_ajustado.md` si la respuesta tardó
> más de lo esperado, para no dejar tiempo muerto.)

**[1:35-2:00] Métricas y honestidad sobre lo que falta**
> "El servicio también expone métricas por dialecto — latencia,
> retroalimentación — sin exponer nunca el contenido. Y somos
> transparentes con lo que aún nos falta: la latencia real sin GPU es
> de 50 a 80 segundos por solicitud, así que el despliegue con GPU
> real es el siguiente paso, no un detalle menor. Y todavía no tenemos
> evaluación con hablantes nativos reales — la infraestructura para
> reclutarlos ya existe, pero no inventamos resultados que no
> tenemos."

**[2:00-2:20] Cierre**
> "En resumen: un solo generador, un modelo, un servicio real que
> funciona de punta a punta. Lo que sigue es escalar a los otros dos
> generadores y probar si fusionar los tres modelos resultantes nos da
> lo mejor de los tres."

## Plan B si la demo en vivo falla

1. **Video corto pre-grabado** (30-40s) de una solicitud real
   respondiendo correctamente — grabarlo con antelación, la noche
   antes o el día de la sustentación antes de empezar, no
   improvisado en el momento.
2. Si ni el video está disponible: mostrar directamente
   `evaluation/comparacion_base_vs_ajustado.md` en pantalla (tabla
   real, ya generada) y narrar sobre eso en vez de un `curl` en vivo.
3. **Nunca** improvisar una cifra o una traducción que no esté en un
   archivo del repositorio — si algo falla, se dice explícitamente
   "esto falló, acá está la evidencia grabada de cuando sí funcionó"
   en vez de fingir que funcionó.

## Pendiente (acción del equipo, no simulable)

- Practicar este guion con cronómetro real y ajustar tiempos.
- Probar la demo en vivo al menos 2 veces antes de la sustentación,
  con el entorno real que se vaya a usar ese día (local, contenedor, o
  el despliegue si ya está listo).
- Grabar el video del Plan B con antelación.
