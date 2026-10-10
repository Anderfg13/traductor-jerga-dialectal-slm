# Extra (después de cerrar la hoja de ruta): seguir afinando el modelo fusionado

**Orden acordado con el equipo:** primero se cierra `docs/hoja_de_ruta_fin_proyecto.md` (evaluación humana, revisión del paper, sustentación, entrega). Esto va después, **como extra**: se presentan los resultados de la investigación y se dice que, con base en ellos, se decidió seguir afinando el modelo fusionado; se mide y se compara. Estado: **no iniciado**.

## Idea

Partir del modelo fusionado (fusión simple con mergekit, 44.2 BLEU / 58.4 chrF en el test común) y entrenar un LoRA nuevo encima, en Colab (regla de cómputo pesado), para mejorar la precisión. Después medir contra el punto de partida con el mismo test común y los mismos intervalos (bootstrap por semilla).

## Cautelas que ya conocemos

- Todos los entrenamientos anteriores dieron la mejor época en la 1 y sobreajustan después: **más pasos con los mismos datos probablemente no mejoran**. Hace falta información nueva.
- Las 9 semillas del test se mantienen apartadas; si se entrenaran, ya no se podría medir la mejora.
- Con 9 semillas de prueba solo se detectan mejoras grandes; una mejora pequeña no se distinguirá del ruido.
- El servicio desplegado usa hoy el adaptador del Generador 1 (`api/main.py`), no el fusionado: desplegar lo mejor requiere un cambio aparte (y el token de Hugging Face).

## Fuentes de datos nuevos (de menor a mayor dependencia de personas)

1. **Datos dirigidos** a los errores observados (`evaluation/analisis_cualitativo.md`): expresiones polisémicas ("mosca", "pedo", "mala leche", "coger la caña", "hacer el bulto", "hacerse humo"), generados con el sentido regional en el prompt. Solo con las semillas de entrenamiento (nunca las de test). La puedo preparar sin ayuda.
2. **Semillas nuevas** escritas o revisadas por el equipo (cobertura de más expresiones).
3. **Correcciones humanas** de los evaluadores (ejemplos corregidos por nativos).

## Protocolo de medición

Mismo test común (174 entradas), mismas métricas y el mismo bootstrap; comparar: fusión simple (punto de partida) vs. fusión + fine-tuning adicional. Reportar también si no hay mejora distinguible. Registrar tiempos de T4.

## Qué necesito de ti para empezar

- Confirmar la fuente de datos (1 por defecto, solo con las 100 semillas actuales).
- Que corras en Colab los cuadernos que yo prepare y me pases el zip de resultados.
