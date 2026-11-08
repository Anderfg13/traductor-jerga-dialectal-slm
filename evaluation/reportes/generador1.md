# Reporte de métricas automáticas (BLEU / chrF)

Ejemplos evaluados: 174

## Global

- BLEU: 42.22
- chrF: 57.53

## Por dialecto

| Dialecto | n | BLEU | chrF |
|---|---|---|---|
| Andina | 38 | 36.02 | 55.16 |
| Caribeña | 39 | 41.52 | 57.07 |
| Chilena | 19 | 39.00 | 51.91 |
| Mexicana | 40 | 48.70 | 61.18 |
| Rioplatense | 38 | 44.69 | 59.23 |

## Por fuente de la referencia

`oro` = traducción escrita por el equipo (sin sesgo hacia ningún generador); `generadorN` = traducción del LLM generador N.

| Fuente | n | BLEU | chrF |
|---|---|---|---|
| generador1 | 54 | 44.78 | 62.75 |
| generador2 | 55 | 45.90 | 58.24 |
| generador3 | 56 | 36.30 | 54.00 |
| oro | 9 | 4.04 | 10.54 |
