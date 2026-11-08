# Reporte de métricas automáticas (BLEU / chrF)

Ejemplos evaluados: 174

## Global

- BLEU: 43.89
- chrF: 58.27

## Por dialecto

| Dialecto | n | BLEU | chrF |
|---|---|---|---|
| Andina | 38 | 37.28 | 54.96 |
| Caribeña | 39 | 42.77 | 57.48 |
| Chilena | 19 | 48.93 | 59.83 |
| Mexicana | 40 | 47.78 | 61.37 |
| Rioplatense | 38 | 44.13 | 59.65 |

## Por fuente de la referencia

`oro` = traducción escrita por el equipo (sin sesgo hacia ningún generador); `generadorN` = traducción del LLM generador N.

| Fuente | n | BLEU | chrF |
|---|---|---|---|
| generador1 | 54 | 45.32 | 62.44 |
| generador2 | 55 | 47.18 | 59.52 |
| generador3 | 56 | 38.67 | 55.17 |
| oro | 9 | 4.48 | 13.33 |
