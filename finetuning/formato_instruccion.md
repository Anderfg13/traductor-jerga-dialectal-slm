# Formato de instrucción

## Contexto

Este formato **ya estaba implementado en el código** desde la Sesión
14 (Anderson, `entrenar_lora.py`) y la Sesión 13
(`probar_baseline.py`) — esta sesión no lo diseña desde cero, lo deja
documentado formalmente y verifica con una prueba real de round-trip,
que es lo que pedía el prompt original de la Sesión 17 y que todavía
no existía como documento independiente.

## El formato

Cada ejemplo se arma como una conversación de 2 o 3 turnos, usando la
plantilla de chat nativa del tokenizador (`apply_chat_template`, no una
plantilla hecha a mano) — así el formato queda automáticamente
consistente con lo que espera el modelo base, sin tener que reproducir
a mano los tokens especiales de control (`<|im_start|>`, `<|im_end|>`,
etc.) que cambian de un modelo a otro.

1. **`system`**: `SYSTEM_PROMPT` (definido una sola vez en
   `probar_baseline.py`, importado tanto por `probar_baseline.py` como
   por `entrenar_lora.py`) — instruye traducir español→inglés y
   responder ÚNICAMENTE con la traducción, sin explicaciones.
2. **`user`**: el campo `texto_dialectal` del ejemplo (la frase en
   dialecto/jerga a traducir).
3. **`assistant`** (solo en entrenamiento, no en inferencia): el campo
   `traduccion` del ejemplo (la traducción de referencia).

**Por qué es el mismo formato en entrenamiento y en inferencia**: los
dos scripts importan el mismo `SYSTEM_PROMPT` de un solo lugar
(`probar_baseline.py`) y arman los mensajes con la misma estructura de
turnos — si estuvieran definidos por separado en cada script, sería
fácil que se desincronizaran con el tiempo (alguien cambia el prompt
en un archivo y se le olvida el otro) y el LoRA aprendería una tarea
ligeramente distinta a la que se mide después.

**Enmascarado de la pérdida**: al entrenar, los tokens del prompt
(`system` + `user`) se marcan con la etiqueta `-100` (valor que
`CrossEntropyLoss` de PyTorch ignora por convención), y solo los
tokens de la respuesta del `assistant` cuentan para la pérdida — el
modelo no es premiado por "aprender a copiar" el prompt, que es fijo y
no aporta señal de traducción.

## Ejemplo real: antes y después de tokenizar

Ejemplo `sem-013` de `generation/splits/dataset_generador1/train.json`:

```json
{
  "texto_dialectal": "¿Mamar gallo, hermano? No me digas que tu nuevo auto es tan caro.",
  "traduccion": "You kidding, bro? Tell me your new car isn't that expensive."
}
```

**Antes de tokenizar** (texto plano que arma
`tokenizer.apply_chat_template(mensajes, tokenize=False)`, tokenizador
de `Qwen/Qwen2.5-3B-Instruct`):

```
<|im_start|>system
Traduce del español al inglés la frase que te dé el usuario. Responde ÚNICAMENTE con la traducción al inglés, sin explicaciones ni texto adicional.<|im_end|>
<|im_start|>user
¿Mamar gallo, hermano? No me digas que tu nuevo auto es tan caro.<|im_end|>
<|im_start|>assistant
You kidding, bro? Tell me your new car isn't that expensive.<|im_end|>
```

**Después de tokenizar** (`apply_chat_template(..., tokenize=True)`,
que es lo que usa `entrenar_lora.py` de verdad):

- Prompt (`system`+`user`, con `add_generation_prompt=True`): **72
  tokens**.
- Secuencia completa (`system`+`user`+`assistant`): **89 tokens**.
- Primeros 15 ids: `[151644, 8948, 198, 42834, 10521, 1594, 69888, 452, 143184, 1187, 90329, 1709, 1013, 7439, 655]`
  (`151644` es el id de `<|im_start|>`).
- Etiquetas (`labels`) para la pérdida: los primeros 72 ids (todo el
  prompt) quedan en `-100`; los 17 ids restantes (la respuesta del
  `assistant`) se dejan tal cual — son los únicos que cuentan para la
  pérdida de este ejemplo.

## Verificación de round-trip (prueba de aceptación de la Sesión 17)

Con el mismo ejemplo, cargando solo el tokenizador de
`Qwen/Qwen2.5-3B-Instruct` (sin pesos del modelo — no hace falta GPU
para esto, es una operación de tokenización pura, no cómputo pesado
según `CONTEXTO_PROYECTO.md`):

1. `tok.decode(ids_completos)` (los 89 ids tokenizados arriba) **==**
   el texto plano de la plantilla mostrado arriba, carácter por
   carácter. ✅
2. Decodificando SOLO los ids cuya etiqueta no es `-100` (o sea, solo
   la parte que el modelo aprende a predecir), el texto reconstruido
   es exactamente `"You kidding, bro? Tell me your new car isn't that
   expensive.\n"`, que coincide con `traduccion` del ejemplo original
   (salvo el salto de línea final del token `<|im_end|>`, que se quita
   con `.strip()` — mismo `.strip()` que ya usa `traducir()` en
   `probar_baseline.py` sobre la salida generada). ✅

Ambas verificaciones confirman que el formato de tokenización no
corrompe ni trunca el texto en ningún punto, y que el enmascarado de
`-100` aísla exactamente la parte de la secuencia que se quiere que el
modelo aprenda a generar.
