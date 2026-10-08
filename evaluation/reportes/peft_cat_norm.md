# Reporte de métricas automáticas (BLEU / chrF)

Ejemplos evaluados: 174

## Global

- BLEU: 43.52
- chrF: 58.11

## Por dialecto

| Dialecto | n | BLEU | chrF |
|---|---|---|---|
| Andina | 38 | 38.79 | 55.60 |
| Caribeña | 39 | 43.01 | 57.51 |
| Chilena | 19 | 42.18 | 54.19 |
| Mexicana | 40 | 50.62 | 62.96 |
| Rioplatense | 38 | 42.70 | 58.53 |

## Por fuente de la referencia

`oro` = traducción escrita por el equipo (sin sesgo hacia ningún generador); `generadorN` = traducción del LLM generador N.

| Fuente | n | BLEU | chrF |
|---|---|---|---|
| generador1 | 54 | 45.70 | 62.52 |
| generador2 | 55 | 47.17 | 59.93 |
| generador3 | 56 | 37.57 | 54.31 |
| oro | 9 | 4.89 | 14.08 |
