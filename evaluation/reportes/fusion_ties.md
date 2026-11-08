# Reporte de métricas automáticas (BLEU / chrF)

Ejemplos evaluados: 174

## Global

- BLEU: 43.75
- chrF: 58.16

## Por dialecto

| Dialecto | n | BLEU | chrF |
|---|---|---|---|
| Andina | 38 | 39.04 | 55.64 |
| Caribeña | 39 | 42.88 | 57.47 |
| Chilena | 19 | 49.03 | 59.67 |
| Mexicana | 40 | 49.26 | 61.23 |
| Rioplatense | 38 | 41.86 | 58.57 |

## Por fuente de la referencia

`oro` = traducción escrita por el equipo (sin sesgo hacia ningún generador); `generadorN` = traducción del LLM generador N.

| Fuente | n | BLEU | chrF |
|---|---|---|---|
| generador1 | 54 | 44.59 | 62.05 |
| generador2 | 55 | 46.82 | 58.98 |
| generador3 | 56 | 39.33 | 55.83 |
| oro | 9 | 4.35 | 10.51 |
