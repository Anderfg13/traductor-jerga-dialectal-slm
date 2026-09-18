# Alcance declarado del banco de semillas

> Responde al punto de la retroalimentación del profesor: "definan
> desde el inicio qué dialectos y expresiones cubrirá el banco de
> semillas". Somos honestos sobre cómo llegamos aquí: la cobertura
> **creció de forma incremental** (Sesión 4: 4 dialectos → Sesión 9:
> se sumó un quinto) en vez de decidirse por completo desde el primer
> lote. Este documento declara el alcance ya fijado para el resto de
> las Fases 2 y 3, para que no siga creciendo de forma ad-hoc.

## Dialectos cubiertos (alcance cerrado)

El banco de semillas cubre **5 macro-variantes regionales del
español**, todas de América Latina:

| Dialecto | Región de referencia | Semillas (lote 1 + 2) |
|---|---|---|
| Caribeña | Colombia (costa Caribe), Venezuela | 21 |
| Andina | Colombia (interior/Bogotá), Perú, Ecuador | 21 |
| Rioplatense | Argentina, Uruguay | 22 |
| Mexicana | México (extensible a Centroamérica) | 21 |
| Chilena | Chile | 15 |

**Por qué estos 5**: cubren una franja amplia y reconocible de
variantes hispanoamericanas con rasgos léxicos bien diferenciados
entre sí (voseo y "che" rioplatense, "chimba"/parceo bogotano,
"cachai"/"al tiro" chileno, "no manches"/"chido" mexicano, "vaina"/
"dar papaya" caribeño), lo que facilita medir si el modelo realmente
distingue dialectos y no solo memoriza vocabulario. Son también los
dialectos sobre los que el equipo tiene acceso directo a hablantes
nativos o cuasi-nativos para la validación humana (Sesión 22).

**Qué se deja fuera, explícitamente, y por qué (limitación conocida,
no un descuido)**: español peninsular (España) y variantes
caribeñas insulares (Cuba, Puerto Rico, República Dominicana) no están
cubiertas. No es que se hayan olvidado — se excluyen a propósito
porque el equipo no tiene forma de reclutar evaluadores humanos nativos
de esas regiones para la Sesión 22, y meter dialectos que después no se
pueden validar con hablantes reales sería peor que no cubrirlos. Esto
se declara como limitación conocida del proyecto en la sección de
limitaciones del paper (Sesión 57, Fase 3), no se oculta.

**Balance**: ningún dialecto pasa de 22 semillas sobre un total de 100
(22%), y ninguno baja de 15 — criterio de balance ya verificado por
script en las Sesiones 4 y 9 (`seeds/lote_01.json`,
`seeds/lote_02.json`).

## Tipos de expresión cubiertos

El campo `registro` del esquema (`seeds/schema.md`, Sesión 3) separa
dos fenómenos que decidimos no mezclar:

- **`informal`**: habla regional cotidiana, propia de un dialecto pero
  no necesariamente jerga cerrada (ej. "ahorita", "al tiro", "hacer
  una vaca") — un hablante de otro dialecto la entendería con algo de
  contexto.
- **`jerga`**: argot más cerrado, específico de un grupo o generación
  dentro del dialecto (ej. "está a toda madre", "andar con la caña",
  "estar tragado") — más probable que un hablante de otro dialecto no
  la entienda sin explicación.

Dentro de esas dos categorías, el banco cubre, por diseño, estos tipos
funcionales de expresión (no es una taxonómía formal adicional en el
esquema, es cómo se distribuyó la curación en la práctica):

- Saludos e interjecciones cotidianas ("¿qué más, pues?", "¿qué onda?").
- Adjetivos/expresiones de aprobación o entusiasmo ("está brutal",
  "es la raja", "qué chimba").
- Estados de ánimo o de situación personal (económica, emocional,
  física: "estar salado", "estar pato", "andar con la caña").
- Advertencias e instrucciones informales ("dar papaya", "ponte
  trucha", "pilas con eso").
- Formas de referirse a personas o vínculos ("parcero", "ese gallo",
  "un pibe bárbaro").

No se cubren, por decisión de alcance, refranes/dichos completos ni
groserías fuertes explícitas — el foco es jerga y dialecto de uso
cotidiano no ofensivo, alineado con el caso de uso de producto
(traducción para negocios/atención al cliente, no moderación de
contenido).

## Qué significa "alcance cerrado" en la práctica

De aquí en adelante, ampliar el banco de semillas (ej. un sexto
dialecto, o cubrir refranes) requiere una decisión explícita del
equipo documentada en `BITACORA.md`, igual que se hizo para agregar
Chilena en la Sesión 9 — no debe volver a crecer de forma incidental
dentro de otra sesión que no sea específicamente sobre el banco de
semillas.
