# Reporte de métricas automáticas (BLEU / chrF)

Ejemplos evaluados: 174

## Global

- BLEU: 43.78
- chrF: 57.66

## Por dialecto

| Dialecto | n | BLEU | chrF |
|---|---|---|---|
| Andina | 38 | 37.44 | 54.37 |
| Caribeña | 39 | 42.74 | 56.73 |
| Chilena | 19 | 45.39 | 57.76 |
| Mexicana | 40 | 50.96 | 61.73 |
| Rioplatense | 38 | 42.91 | 58.81 |

## Por fuente de la referencia

`oro` = traducción escrita por el equipo (sin sesgo hacia ningún generador); `generadorN` = traducción del LLM generador N.

| Fuente | n | BLEU | chrF |
|---|---|---|---|
| generador1 | 54 | 45.34 | 62.35 |
| generador2 | 55 | 45.59 | 57.65 |
| generador3 | 56 | 39.10 | 55.07 |
| oro | 9 | 10.48 | 13.93 |
