# Reporte de métricas automáticas (BLEU / chrF)

Ejemplos evaluados: 174

## Global

- BLEU: 35.31
- chrF: 51.47

## Por dialecto

| Dialecto | n | BLEU | chrF |
|---|---|---|---|
| Andina | 38 | 32.88 | 49.83 |
| Caribeña | 39 | 36.30 | 51.85 |
| Chilena | 19 | 28.77 | 47.69 |
| Mexicana | 40 | 37.83 | 52.81 |
| Rioplatense | 38 | 33.83 | 52.88 |

## Por fuente de la referencia

`oro` = traducción escrita por el equipo (sin sesgo hacia ningún generador); `generadorN` = traducción del LLM generador N.

| Fuente | n | BLEU | chrF |
|---|---|---|---|
| generador1 | 54 | 36.08 | 54.74 |
| generador2 | 55 | 38.86 | 52.37 |
| generador3 | 56 | 32.47 | 49.94 |
| oro | 9 | 0.93 | 8.81 |
