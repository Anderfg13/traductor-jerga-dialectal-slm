# Reporte de métricas automáticas (BLEU / chrF)

Ejemplos evaluados: 174

## Global

- BLEU: 43.63
- chrF: 58.12

## Por dialecto

| Dialecto | n | BLEU | chrF |
|---|---|---|---|
| Andina | 38 | 38.87 | 55.57 |
| Caribeña | 39 | 43.16 | 57.83 |
| Chilena | 19 | 42.44 | 54.13 |
| Mexicana | 40 | 51.02 | 62.99 |
| Rioplatense | 38 | 41.95 | 58.19 |

## Por fuente de la referencia

`oro` = traducción escrita por el equipo (sin sesgo hacia ningún generador); `generadorN` = traducción del LLM generador N.

| Fuente | n | BLEU | chrF |
|---|---|---|---|
| generador1 | 54 | 44.82 | 62.27 |
| generador2 | 55 | 47.48 | 59.66 |
| generador3 | 56 | 38.09 | 54.94 |
| oro | 9 | 4.38 | 9.39 |
