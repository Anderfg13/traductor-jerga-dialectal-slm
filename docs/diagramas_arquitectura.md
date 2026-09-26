# Diagramas de arquitectura (Project Advance 2)

Diagramas para los entregables del syllabus de la semana 10:
arquitectura empresarial, de datos, de aplicación y de tecnología,
diseño del componente inteligente, diseño de la API, plan de
despliegue en la nube, diseño de seguridad, hoja de ruta y modelo de
gobernanza.

Cómo leerlos:

- Cada elemento sale del código o de la documentación real del repo
  (se indica el archivo cuando ayuda). No hay componentes inventados.
- **Línea punteada y fondo amarillo = pendiente o no implementado.**
- Notación libre (no C4 ni UML formal), porque el syllabus no dice
  cuál se espera. Si el profesor pide una notación específica, hay
  que redibujarlos.
- Se ven renderizados en GitHub y en la vista previa de VS Code
  (con la extensión Markdown Preview Mermaid Support). El código
  fuente de cada diagrama queda dentro de su bloque `mermaid`.
- Los escenarios de atributos de calidad no llevan diagrama: ya son
  una tabla formal en `paper/main.tex` (estímulo, entorno, respuesta,
  medida).

---

## 1. Arquitectura empresarial

Interesados, capacidad de negocio y diferenciadores. Contenido de la
Sección de Caracterización del problema y de la Tabla de diferencias
de producto del paper.

```mermaid
flowchart LR
  subgraph INT["Interesados"]
    H["Hablantes de español con dominio<br/>limitado del inglés (o viceversa)"]
    P["Profesionales que actúan a partir<br/>de la traducción (salud, justicia, servicios)"]
    I["Intérpretes informales<br/>(familiares, a veces menores)"]
    C["Organización cliente<br/>opera la API y su gobernanza de datos"]
  end
  S["Servicio de traducción de jerga y dialecto<br/>SLM ajustado con LoRA"]
  CAP["Capacidad de negocio habilitada:<br/>traducción dialectal auditable, sin exponer<br/>datos sensibles a un tercero"]
  DIF["Diferenciadores frente a Google Translate, DeepL y ChatGPT:<br/>no exige internet constante, datos no salen a la nube de un tercero,<br/>personalizable por cliente, auditable, barato a escala"]

  H -->|usa| S
  P -->|usa| S
  I -->|usa| S
  C -->|adopta y opera| S
  S --> CAP
  DIF -.->|explica| CAP
```

---

## 2. Arquitectura de datos

Pipeline de datos con los scripts y archivos reales de `seeds/`,
`generation/` y `evaluation/`. Solo el Generador 1 (Groq) está
implementado; los Generadores 2 y 3 son fase final.

```mermaid
flowchart TD
  subgraph SEM["1. Banco de semillas (seeds/)"]
    L1["lote_01.json<br/>40 semillas, 4 dialectos"]
    L2["lote_02.json<br/>60 semillas, suma el dialecto chileno"]
    SCH["schema.md<br/>id, texto_original, dialecto_region, registro,<br/>traduccion_referencia, nota_contexto_cultural"]
  end

  PD["2. Derivación<br/>generation/prompt_derivacion.md<br/>5-8 variantes por semilla, JSON, sin mezclar dialectos"]

  subgraph GEN["3. Generación sintética (generation/)"]
    G1["generar_sintetico.py<br/>Generador 1: Groq openai/gpt-oss-20b<br/>reintentos con backoff, reanudable"]
    RAW["raw/generador1/{seed_id}.json<br/>salida cruda por semilla"]
    CON["consolidar.py<br/>quita variantes vacías y duplicadas exactas"]
    DS["dataset_generador1.json<br/>238 variantes"]
  end

  subgraph VAL["4. Validación"]
    V["validar.py<br/>longitud, casi-copia de la semilla,<br/>idioma inesperado, duplicados"]
    LIM["dataset_generador1_limpio.json<br/>236 variantes (99.2%)"]
    REP["reporte_filtrado.md"]
    MUE["evaluation/muestreo.py<br/>muestra proporcional por dialecto"]
    CSV["muestreo_manual.csv<br/>para validación humana"]
  end

  subgraph SPL["5. Splits y documentación"]
    SP["split_dataset.py<br/>80/10/10 por semilla, estratificado por dialecto"]
    TR["train.json<br/>189 variantes, 32 semillas"]
    VA["val.json<br/>24 variantes, 4 semillas"]
    TE["test.json<br/>23 variantes, 4 semillas"]
    DC["data_card_generador1.md"]
  end

  G23["Generadores 2 y 3<br/>Fase final, sin implementar"]

  L1 --> G1
  L2 -.->|aún no procesado| G1
  SCH -.->|define el formato| L1
  PD --> G1
  G1 --> RAW --> CON --> DS --> V
  V --> LIM
  V --> REP
  DS --> MUE --> CSV
  LIM --> SP
  SP --> TR
  SP --> VA
  SP --> TE
  SP --> DC
  G23 -.-> PD

  classDef pend fill:#fff8e1,stroke:#b58900,color:#1a1a1a,stroke-dasharray: 5 5;
  class G23 pend;
```

---

## 3. Arquitectura de aplicación

Componentes internos del servicio `api/main.py` (FastAPI) y el orden
en que una solicitud los atraviesa. Todo el estado vive en memoria del
proceso: no hay base de datos ni escritura a disco.

```mermaid
flowchart LR
  CL["Cliente<br/>(curl, app del cliente)"]

  subgraph API["Servicio FastAPI (api/main.py, uvicorn :8000)"]
    direction TB
    EP1["POST /traducir"]
    EP2["POST /retroalimentacion"]
    EP3["GET /metricas"]
    EP4["GET /salud"]
    VAL["Validación de entrada<br/>Pydantic: texto obligatorio, máx. 500 caracteres"]
    RL["Límite de tasa por IP<br/>ventana deslizante, 10 solicitudes / 60 s"]
    GEN["Generación<br/>modelo y tokenizador cargados una sola vez al iniciar"]
    MET["Métricas en memoria<br/>contadores globales y por dialecto,<br/>latencia promedio, tasa de retroalimentación positiva"]
    FB["Mapa solicitud_id a dialecto<br/>en memoria, sin texto, se borra al usarse"]
    ERR["Manejo de errores<br/>500 genérico, nunca el traceback"]
  end

  subgraph MOD["Modelo (en memoria)"]
    BASE["Qwen2.5-3B-Instruct<br/>bfloat16"]
    AD["Adaptador LoRA del Generador 1<br/>finetuning/checkpoints/generador1/adapter"]
  end

  CL --> EP1
  CL --> EP2
  CL --> EP3
  CL --> EP4
  EP1 --> VAL --> RL --> GEN
  GEN --> BASE
  AD -.->|se suma al modelo base| BASE
  GEN --> MET
  GEN --> FB
  EP2 --> FB
  FB --> MET
  EP3 --> MET
  ERR -.->|captura excepciones de| GEN
```

---

## 4. Diseño de la API

Contrato de los cuatro endpoints y secuencia de una traducción con su
retroalimentación. Detalle completo en `api/README.md`.

| Endpoint | Entrada | Salida correcta | Errores posibles | Límite de tasa |
|---|---|---|---|---|
| `GET /salud` | ninguna | `{"estado": "ok"}` | ninguno | No |
| `GET /metricas` | ninguna | contadores globales y `por_dialecto` (latencia promedio, tasa de retroalimentación positiva) | ninguno | No |
| `POST /traducir` | `{"texto": "...", "dialecto": "opcional"}` | `{"traduccion", "dialecto", "solicitud_id"}` | `422` entrada inválida, `429` límite de tasa (con `Retry-After`), `400` solo espacios, `503` modelo no cargado, `500` error interno genérico | Sí, 10 por 60 s por IP |
| `POST /retroalimentacion` | `{"solicitud_id": "...", "es_correcta": true/false}` | `{"registrada": true}` | `404` id inexistente o ya usado | No |

```mermaid
sequenceDiagram
  autonumber
  participant C as Cliente
  participant A as API FastAPI
  participant M as Modelo Qwen2.5-3B + LoRA

  C->>A: POST /traducir {texto, dialecto}
  alt Entrada inválida (vacía, sin campo, más de 500 caracteres)
    A-->>C: 422 con detail claro
  else Más de 10 solicitudes en 60 s desde la misma IP
    A-->>C: 429 con Retry-After
  else Texto solo espacios
    A-->>C: 400 con detail claro
  else Modelo todavía no cargado
    A-->>C: 503 intentar de nuevo
  else Solicitud válida
    A->>M: generar traducción
    M-->>A: traducción
    A->>A: registra latencia por dialecto<br/>y solicitud_id a dialecto (sin texto)
    A-->>C: 200 {traduccion, dialecto, solicitud_id}
  end

  C->>A: POST /retroalimentacion {solicitud_id, es_correcta}
  alt solicitud_id válido y sin usar
    A->>A: suma a la tasa positiva del dialecto<br/>y borra el solicitud_id
    A-->>C: 200 {registrada: true}
  else id inexistente o ya usado
    A-->>C: 404
  end

  C->>A: GET /metricas
  A-->>C: solo contadores agregados, nunca texto
```

---

## 5. Arquitectura de tecnología y diseño del componente inteligente

Ciclo de vida del modelo: de los splits al adaptador que sirve la API.
El entrenamiento corre en Google Colab (política del repo: cómputo
pesado nunca en máquina local).

```mermaid
flowchart TD
  TRJ["train.json y val.json<br/>Generador 1"]

  subgraph FMT["Formato de instrucción (finetuning/formato_instruccion.md)"]
    F1["Chat: system + user + assistant<br/>vía apply_chat_template<br/>mismo SYSTEM_PROMPT en entrenamiento e inferencia"]
    F2["Pérdida enmascarada con -100 sobre el prompt<br/>solo se aprende la traducción<br/>truncamiento MAX_LENGTH = 512, recorta por la izquierda"]
  end

  subgraph TRN["Entrenamiento LoRA en Google Colab (GPU T4/L4)"]
    BASE["Modelo base Qwen2.5-3B-Instruct<br/>bfloat16, sin cuantizar<br/>(Llama 3.2 3B bloqueado por acceso gated de Meta)"]
    LORA["LoRA: r=8, alpha=16, dropout=0.05,<br/>bias=none, módulos q_proj k_proj v_proj o_proj"]
    ES["Selección por mejor pérdida de validación<br/>load_best_model_at_end + EarlyStopping<br/>(se detectó sobreajuste)"]
  end

  AD["Adaptador LoRA final<br/>finetuning/checkpoints/generador1/adapter"]

  subgraph EVA["Evaluación"]
    AUT["metricas_automaticas.py<br/>BLEU y chrF, global y por dialecto<br/>(8 de 23 ejemplos de test, resto requiere GPU)"]
    HUM["Evaluación humana con rúbrica 1-5<br/>mínimo 3 hablantes nativos por dialecto<br/>kappa de Fleiss"]
  end

  SRV["Servicio de traducción<br/>api/main.py"]

  FUS["Fusión de modelos<br/>TIES/DARE vía mergekit y destilación multi-maestro<br/>merging/ vacío, fase final"]

  TRJ --> F1 --> F2 --> LORA
  BASE --> LORA --> ES --> AD
  AD --> AUT
  AD -.-> HUM
  AD --> SRV
  AD -.->|Generadores 2 y 3| FUS

  classDef pend fill:#fff8e1,stroke:#b58900,color:#1a1a1a,stroke-dasharray: 5 5;
  class HUM,FUS pend;
```

---

## 6. Plan de despliegue en la nube

Tres entornos. El contenedor local ya funciona; el despliegue público
en Hugging Face Spaces tiene el código listo pero está bloqueado por
un requisito externo (antigüedad de 30 días de la cuenta para la
excepción gratuita de ZeroGPU, esperada alrededor del 2026-10-02).
Pasos de despliegue en `docs/despliegue.md`.

```mermaid
flowchart LR
  GH["Repositorio GitHub<br/>fuente única del código"]

  subgraph COL["Google Colab (GPU T4/L4)"]
    TR["Entrenamiento LoRA,<br/>evaluación masiva,<br/>fusión futura"]
  end

  subgraph LOC["Contenedor local (Docker o Podman)"]
    direction TB
    IMG["Imagen python:3.11-slim<br/>torch solo CPU, uvicorn :8000<br/>incluye el adaptador LoRA"]
    VOL["Volumen hf-cache<br/>guarda el modelo base entre reinicios"]
    HC["HEALTHCHECK a /salud"]
  end

  subgraph HFS["Hugging Face Spaces (api/space)"]
    direction TB
    SP["Gradio + ZeroGPU<br/>GPU real solo durante cada generación<br/>expone traducir y salud"]
  end

  HUB["Hugging Face Hub<br/>modelo base Qwen2.5-3B-Instruct, ~6 GB"]
  CLI["Clientes"]

  GH -->|clonar y correr script| TR
  TR -->|adaptador entrenado| GH
  GH -->|docker compose up| IMG
  HUB -->|descarga en el primer arranque| IMG
  IMG --- VOL
  IMG --- HC
  CLI -->|probado en local| IMG
  GH -.->|subir código| SP
  HUB -.-> SP
  CLI -.->|pendiente: URL pública| SP

  NOTA["Bloqueo: cuenta con menos de 30 días<br/>(esperado ~2026-10-02).<br/>Alternativas descartadas: Render (poca memoria),<br/>Railway (sin free tier), AWS Academy (sesión de 40 min)"]
  SP -.- NOTA

  classDef pend fill:#fff8e1,stroke:#b58900,color:#1a1a1a,stroke-dasharray: 5 5;
  class SP,NOTA pend;
```

---

## 7. Diseño de seguridad

Controles sobre el recorrido de una solicitud, y lo que el servicio no
hace. Las cifras salen de `api/README.md` y de las pruebas de la
Sesión 28.

```mermaid
flowchart TD
  REQ["Solicitud POST /traducir"]

  subgraph CTRL["Controles implementados"]
    C1["1. Validación de entrada<br/>texto obligatorio, máx. 500 caracteres,<br/>solo espacios rechazado<br/>respuesta 422 o 400 con mensaje claro"]
    C2["2. Límite de tasa por IP<br/>10 por 60 s, respuesta 429 con Retry-After<br/>en memoria, pensado para una sola instancia"]
    C3["3. Errores controlados<br/>excepción no prevista: 500 genérico<br/>el traceback queda solo en logs del servidor"]
  end

  PRIV["Privacidad por diseño<br/>nunca se escribe a disco ni a un log el texto de la solicitud,<br/>de la traducción ni el dialecto<br/>/metricas expone solo contadores agregados<br/>sin persistencia: todo se reinicia en cero"]

  GAP["No implementado (límites declarados)<br/>autenticación de clientes<br/>escala a varias instancias: el límite de tasa<br/>necesitaría un almacén compartido, ej. Redis<br/>TLS y exposición pública dependen de la plataforma de despliegue"]

  REQ --> C1 --> C2 --> C3
  C3 --> PRIV
  CTRL -.-> GAP

  classDef pend fill:#fff8e1,stroke:#b58900,color:#1a1a1a,stroke-dasharray: 5 5;
  class GAP pend;
```

---

## 8. Hoja de ruta

Estado a la fecha, según la Tabla de hoja de ruta del paper.

```mermaid
flowchart TD
  subgraph DONE["Ya cerrado"]
    direction LR
    D1["Banco de semillas, generación sintética,<br/>validación y splits"]
    D2["Ajuste fino completo del Generador 1<br/>con detección de sobreajuste"]
    D3["Comparación cuantitativa contra la línea base"]
    D4["API con seguridad, observabilidad,<br/>pruebas de carga y prueba e2e"]
  end

  subgraph CLOSING["Cerrando esta fase"]
    direction LR
    C1["Evaluación humana con hablantes nativos reales<br/>infraestructura lista, falta reclutar<br/>y calibrar la rúbrica entre dos personas"]
    C2["Despliegue público en la nube<br/>código listo, bloqueado por antigüedad de cuenta"]
    C3["BLEU y chrF sobre los 23 ejemplos de test<br/>hoy solo 8, requiere GPU (Colab)"]
  end

  subgraph FINAL["Fase final"]
    direction LR
    F1["Generadores 2 y 3:<br/>generación sintética y ajuste fino"]
    F2["Fusión de modelos:<br/>simple (TIES/DARE) y por destilación multi-maestro"]
    F3["Comparación completa PI1, PI2, PI3<br/>incluye sistemas de propósito general"]
  end

  DONE --> CLOSING --> FINAL

  classDef cerrado fill:#e8f5e9,stroke:#2e7d32,color:#1a1a1a;
  classDef cerrando fill:#fff8e1,stroke:#b58900,color:#1a1a1a;
  classDef final fill:#eceff1,stroke:#607d8b,color:#1a1a1a,stroke-dasharray: 5 5;
  class D1,D2,D3,D4 cerrado;
  class C1,C2,C3 cerrando;
  class F1,F2,F3 final;
```

---

## 9. Modelo de gobernanza

Roles, decisiones y trazabilidad. Detalle en
`docs/modelo_gobernanza.md`.

```mermaid
flowchart TD
  subgraph ROL["Dueños por área (gobernanza asíncrona, sin comité)"]
    A["Anderson<br/>infraestructura, generación sintética, entrenamiento"]
    P["Paula<br/>datos (semillas, muestreo, validación humana),<br/>configuración de LoRA"]
    M["Mariana<br/>estructura del repo, documentación,<br/>filtros y splits, observabilidad"]
  end

  DEC["Decisión dentro del área"]
  ACU["Decisión que exige acuerdo de los 3<br/>alcance de fase, modelo base,<br/>técnica de fusión, entrega al profesor"]

  subgraph TRZ["Trazabilidad de cada cambio"]
    CM["Commit en formato Conventional Commits"]
    HK["git hook pre-commit<br/>exige entrada real en BITACORA.md<br/>(Qué se hizo, Decisiones, Pendiente)"]
    BIT["BITACORA.md<br/>registro cronológico compartido"]
  end

  subgraph POL["Políticas fijas"]
    DAT["Datos: versionados con procedencia hasta la semilla,<br/>el servicio nunca persiste el texto traducido"]
    MOD["Modelos: un adaptador por generador,<br/>se promueve el de mejor pérdida de validación"]
    CMP["Cómputo pesado siempre en Colab"]
    ETI["Riesgos éticos: sin groserías fuertes,<br/>dialectos no cubiertos declarados"]
  end

  A --> DEC
  P --> DEC
  M --> DEC
  ROL --> ACU
  DEC --> CM
  ACU --> CM
  CM --> HK
  HK -->|bloquea si falta| BIT
  BIT -.-> POL
```
