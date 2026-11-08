# Reporte de métricas automáticas (BLEU / chrF)

Ejemplos evaluados: 174

## Global

- BLEU: 44.22
- chrF: 58.36

## Por dialecto

| Dialecto | n | BLEU | chrF |
|---|---|---|---|
| Andina | 38 | 39.64 | 55.62 |
| Caribeña | 39 | 42.94 | 57.44 |
| Chilena | 19 | 44.77 | 55.73 |
| Mexicana | 40 | 52.44 | 64.10 |
| Rioplatense | 38 | 42.56 | 58.17 |

## Por fuente de la referencia

`oro` = traducción escrita por el equipo (sin sesgo hacia ningún generador); `generadorN` = traducción del LLM generador N.

| Fuente | n | BLEU | chrF |
|---|---|---|---|
| generador1 | 54 | 46.84 | 62.95 |
| generador2 | 55 | 48.40 | 60.36 |
| generador3 | 56 | 37.27 | 54.25 |
| oro | 9 | 4.89 | 14.08 |
