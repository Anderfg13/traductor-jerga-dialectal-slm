# Reporte de métricas automáticas (BLEU / chrF)

Ejemplos evaluados: 174

## Global

- BLEU: 37.01
- chrF: 53.90

## Por dialecto

| Dialecto | n | BLEU | chrF |
|---|---|---|---|
| Andina | 38 | 35.72 | 54.23 |
| Caribeña | 39 | 36.91 | 54.25 |
| Chilena | 19 | 29.71 | 44.27 |
| Mexicana | 40 | 44.86 | 58.11 |
| Rioplatense | 38 | 33.58 | 52.27 |

## Por fuente de la referencia

`oro` = traducción escrita por el equipo (sin sesgo hacia ningún generador); `generadorN` = traducción del LLM generador N.

| Fuente | n | BLEU | chrF |
|---|---|---|---|
| generador1 | 54 | 38.24 | 58.01 |
| generador2 | 55 | 40.66 | 54.65 |
| generador3 | 56 | 31.83 | 51.26 |
| oro | 9 | 1.40 | 8.59 |
