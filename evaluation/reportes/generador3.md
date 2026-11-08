# Reporte de métricas automáticas (BLEU / chrF)

Ejemplos evaluados: 174

## Global

- BLEU: 42.26
- chrF: 57.93

## Por dialecto

| Dialecto | n | BLEU | chrF |
|---|---|---|---|
| Andina | 38 | 38.73 | 56.47 |
| Caribeña | 39 | 42.00 | 56.78 |
| Chilena | 19 | 39.48 | 53.40 |
| Mexicana | 40 | 49.82 | 63.46 |
| Rioplatense | 38 | 37.46 | 57.38 |

## Por fuente de la referencia

`oro` = traducción escrita por el equipo (sin sesgo hacia ningún generador); `generadorN` = traducción del LLM generador N.

| Fuente | n | BLEU | chrF |
|---|---|---|---|
| generador1 | 54 | 42.43 | 61.36 |
| generador2 | 55 | 45.69 | 59.53 |
| generador3 | 56 | 38.32 | 55.17 |
| oro | 9 | 3.85 | 13.92 |
