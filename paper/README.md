# paper/

`main.tex` es el paper del proyecto (Fase 1 entregada, en actualización
para Fase 2). Antes de esta sesión, este documento solo vivía en
Overleaf y no estaba versionado en el repositorio — se trajo aquí para
que quede trazable como todo lo demás (`BITACORA.md`, revisión de
código, historial de cambios), en vez de ser el único artefacto del
proyecto sin control de versiones.

## Cómo se sincroniza con Overleaf

Por ahora, la sincronización es manual: los cambios que se hagan aquí
se copian y pegan de vuelta al proyecto de Overleaf (y viceversa, si
alguien edita directamente en Overleaf, hay que traer esos cambios acá
antes de seguir editando en el repo, para no perderlos). Si el equipo
tiene una cuenta de Overleaf con plan que soporte integración con Git,
vale la pena configurarla para no depender de copiar y pegar — no se
ha hecho todavía.

## Cómo compilar localmente

Requiere una distribución de LaTeX (MiKTeX en Windows, TeX Live en
Linux/Mac) con soporte para `babel` en español.

```
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex   # segunda pasada, para referencias cruzadas y bibliografía
```

`main.pdf` se versiona en el repo como evidencia de que el documento
compila limpio en el momento del commit — no se versionan los
artefactos intermedios de compilación (`.aux`, `.log`, `.out`, ver
`.gitignore`).
