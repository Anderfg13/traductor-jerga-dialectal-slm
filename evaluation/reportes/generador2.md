# Reporte de métricas automáticas (BLEU / chrF)

Ejemplos evaluados: 174

## Global

- BLEU: 40.74
- chrF: 55.28

## Por dialecto

| Dialecto | n | BLEU | chrF |
|---|---|---|---|
| Andina | 38 | 37.24 | 54.93 |
| Caribeña | 39 | 40.33 | 54.49 |
| Chilena | 19 | 44.56 | 56.36 |
| Mexicana | 40 | 42.24 | 54.58 |
| Rioplatense | 38 | 41.52 | 57.02 |

## Por fuente de la referencia

`oro` = traducción escrita por el equipo (sin sesgo hacia ningún generador); `generadorN` = traducción del LLM generador N.

| Fuente | n | BLEU | chrF |
|---|---|---|---|
| generador1 | 54 | 41.91 | 59.39 |
| generador2 | 55 | 47.38 | 58.57 |
| generador3 | 56 | 33.36 | 50.59 |
| oro | 9 | 3.18 | 10.46 |
