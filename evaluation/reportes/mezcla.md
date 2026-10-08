# Reporte de métricas automáticas (BLEU / chrF)

Ejemplos evaluados: 174

## Global

- BLEU: 42.42
- chrF: 57.20

## Por dialecto

| Dialecto | n | BLEU | chrF |
|---|---|---|---|
| Andina | 38 | 38.34 | 55.35 |
| Caribeña | 39 | 40.42 | 55.26 |
| Chilena | 19 | 44.46 | 56.08 |
| Mexicana | 40 | 48.90 | 62.05 |
| Rioplatense | 38 | 40.77 | 57.70 |

## Por fuente de la referencia

`oro` = traducción escrita por el equipo (sin sesgo hacia ningún generador); `generadorN` = traducción del LLM generador N.

| Fuente | n | BLEU | chrF |
|---|---|---|---|
| generador1 | 54 | 42.32 | 61.04 |
| generador2 | 55 | 46.40 | 58.09 |
| generador3 | 56 | 37.86 | 54.78 |
| oro | 9 | 5.25 | 10.73 |
