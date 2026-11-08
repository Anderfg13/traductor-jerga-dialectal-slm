# Reporte de métricas automáticas (BLEU / chrF)

Ejemplos evaluados: 174

## Global

- BLEU: 44.03
- chrF: 57.99

## Por dialecto

| Dialecto | n | BLEU | chrF |
|---|---|---|---|
| Andina | 38 | 38.03 | 54.75 |
| Caribeña | 39 | 42.94 | 57.10 |
| Chilena | 19 | 47.57 | 57.85 |
| Mexicana | 40 | 50.73 | 61.64 |
| Rioplatense | 38 | 43.48 | 59.51 |

## Por fuente de la referencia

`oro` = traducción escrita por el equipo (sin sesgo hacia ningún generador); `generadorN` = traducción del LLM generador N.

| Fuente | n | BLEU | chrF |
|---|---|---|---|
| generador1 | 54 | 45.60 | 62.04 |
| generador2 | 55 | 46.24 | 58.88 |
| generador3 | 56 | 39.32 | 55.36 |
| oro | 9 | 4.33 | 11.75 |
