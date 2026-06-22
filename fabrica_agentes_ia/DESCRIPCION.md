# Fábrica de Agentes de IA (`fabrica_agentes_ia`)

Este documento describe la arquitectura, principios operativos y diseño del núcleo de la **Fábrica de Agentes de IA** (`fabrica_agentes_ia`). Aunque actualmente está configurado para operar dentro del contexto del proyecto **Geojana**, su diseño ha sido desacoplado de forma modular para permitir su fácil reutilización y adaptación en cualquier otro proyecto de desarrollo de software multipropósito o multi-repositorio.

---

## 1. Núcleo Reutilizable y Desacoplado

La Fábrica de Agentes de IA está diseñada bajo el principio de **separación de datos y motor**. No contiene reglas de negocio de Geojana duras en el código de su motor base (`core/`). En su lugar, el comportamiento específico del proyecto se inyecta a través de dos fuentes externas:
1. **Configuración de repositorios e incumbencias:** Definida de forma declarativa en `config/repositories.json`.
2. **Base de conocimiento técnica portable:** Ingestada y serializada dinámicamente en `knowledge_base/evidence.jsonl` a partir de cualquier carpeta de documentación técnica.

Para migrar esta fábrica a otro proyecto, solo se requiere redefinir el archivo de repositorios y escanear la nueva documentación técnica del proyecto destino.

---

## 2. Descripción en Términos Operativos del Flujo de Trabajo

El ciclo de vida de una solicitud procesada por la fábrica se rige por diez etapas o pilares técnicos:

### A. Entrada Clara
La interacción comienza a través del comando `ask` del CLI (`cli.py`), el cual acepta solicitudes de lenguaje natural no estructuradas. 
- **Limpieza de Ruido:** El motor base utiliza funciones de normalización y expresiones regulares para limpiar la frase de invocaciones repetitivas (como `"usando los agentes de..."` o `"realiza..."`).
- **Extracción del Core de la Tarea:** Se aisla el mandato directo del usuario para que los agentes posteriores no se confundan con meta-instrucciones o ruido verbal.

### B. Refinamiento
Antes de involucrar a los agentes de código o planificación profunda, la entrada limpia pasa por un proceso de refinamiento estricto:
- **Detección de Repositorios:** Cruza términos clave contra los nombres y alias definidos en `repositories.json`. Si no detecta ninguno, intenta deducirlo a partir del directorio actual de ejecución (`current_dir`).
- **Detección de Modo de Intención:** Clasifica la tarea según diccionarios de verbos semánticos en 8 modos: `implement` (cambios de código), `review` (auditoría), `plan` (diseño), `test` (pruebas), `debug` (resolución de fallos), `docs` (documentación), `context` (contexto técnico) o `unknown` (desconocido).
- **Gestión de Bloqueos y Advertencias:** Si la solicitud menciona más de un repositorio (y no se ha usado un `--repo override`), el sistema genera un **bloqueo**. Si el modo o el repositorio objetivo quedan ambiguos, genera **advertencias**.
- **Cálculo de Confianza:** Se asigna un nivel de confianza (`blocked`, `high`, `medium`, `low`) que restringe los pasos posteriores.

### C. Planificación
A partir del modo y repositorio identificados, el refinador compila un conjunto de salidas orientadas a la acción:
- **`task.md`:** Define la tarea limpia, los criterios de aceptación esperados, advertencias y supuestos de partida.
- **`execution_plan.md`:** Secuencia una lista ordenada de pasos tácticos requeridos según el workflow del modo (por ejemplo, buscar dependencias, ubicar archivos, modificar por lotes pequeños, verificar).
- **`compiled_prompt.md`:** Un prompt listo para ser consumido por un agente ejecutor final (o el propio desarrollador), consolidando las políticas específicas del repositorio asignado y reglas de resguardo técnico.

### D. Especialización por Agentes
El trabajo complejo se subdivide en agentes especializados en `agents/`, cada uno con responsabilidades únicas y modelos de entrada/salida tipificados:
- **`DocumentIngestorAgent`:** Ingesta y formatea documentación técnica para construir la base de conocimiento portable.
- **`EvidenceCuratorAgent`:** Analiza la consulta del usuario y filtra la base de conocimiento para seleccionar únicamente las evidencias pertinentes sin saturar la ventana de contexto.
- **`PlannerAgent`:** Diseña el flujo lógico y los pasos secuenciales de implementación técnica.
- **`SoftwareArchitectAgent`:** Valida la adherencia a patrones de diseño y decisiones de arquitectura (como ADRs).
- **`ImplementerAgent`:** Ejecuta los cambios físicos en el código fuente.
- **`QAAgent`:** Identifica y diseña las pruebas necesarias para el cambio.
- **`ReviewerAgent`:** Realiza una auditoría final cruzada de las salidas de los agentes previos.

### E. Reglas y Workflows
La fábrica define flujos de ejecución específicos (`MODE_WORKFLOW`) según el modo de operación de la tarea.
- **Limitación Monolítica de Ejecución:** Una regla de diseño inquebrantable impide que una sola tarea modifique múltiples repositorios simultáneamente. Si una tarea es multirepositorio, la fábrica obliga a dividirla.
- **Políticas de Repositorio:** El comportamiento de los agentes se rige por políticas declaradas en la configuración del repositorio destino (ej. *"No cambiar contratos backend desde el frontend"*, *"Priorizar ergonomía móvil y estados offline"*).

### F. Arnés
El arnés de la fábrica (`harness.py`) actúa como el entorno de pruebas automatizado y verificador de calidad del pipeline del agente.
- No ejecuta el código del proyecto en sí, sino que **evalúa la validez de la ejecución del agente** y sus entregables.
- Revisa el cumplimiento de restricciones clave como el presupuesto de tokens consumido, la existencia de la traza de auditoría (`trace.jsonl`), y la validez formal de las afirmaciones hechas por el agente.

### G. Ejecución Reproducible
Toda ejecución de la fábrica es completamente autónoma e independiente de cambios externos futuros:
- **Directorio de Corrida (`runs/YYYYMMDD-HHMMSS/`):** Cada ejecución genera una carpeta fechada única y autocontenida.
- **Snapshot de Evidencia:** Copia la base de conocimiento (`evidence.jsonl`) utilizada en ese momento exacto dentro de la carpeta de la corrida. Esto asegura que la validación posterior sea idéntica incluso si los documentos originales cambian después.
- **Salidas Serializables:** Los agentes escriben archivos JSON estrictos con la estructura exacta de su procesamiento, decisiones y afirmaciones.

### H. Validación
La etapa de validación (`harness.py` / comando `validate`) corre de forma automatizada sobre la carpeta de la corrida:
- **Validación de Citas:** Cruza cada declaración/decisión técnica (`claims`) reportada por el agente y valida que su `evidence_id` exista y coincida de manera exacta con el snapshot de la base de conocimiento.
- **Control de Presupuesto:** Comprueba que los outputs de los agentes no excedan los límites establecidos de tokens salientes para evitar truncados y optimizar costos.
- **Detección de Anomalías:** Reporta fallos en la ingesta o ausencia del archivo de trazas.

### I. Evidencia
La regla central de la fábrica establece: **Si un hecho de dominio no está registrado en `evidence.jsonl`, no existe.**
- Se evitan las alucinaciones limitando el conocimiento del agente a las evidencias extraídas del inventario de documentos técnicos.
- Cualquier afirmación o decisión arquitectónica del agente debe ir acompañada de una cita formal (`[documento.md#evidence_id]`).
- Todo lo que no esté en la base de datos de evidencias debe ser clasificado explícitamente como `unknown` (desconocido) o supuesto, y el agente debe levantar una pregunta en lugar de asumir.

### J. Cierre Técnico
Al completar un ciclo de ejecución, la fábrica realiza el empaquetado y registro de continuidad:
- **Generación de Entregables de Contexto:** Crea `selected_context.md` (un extracto optimizado de evidencias de la base de conocimiento para la tarea) y `ambiguity_report.md` (si existen bloqueos que detengan el desarrollo).
- **Registro en Memoria:** Anota la consulta, el modo, la confianza y el resultado en `memory/natural_tasks.jsonl` para aprendizaje histórico.
- **Handoff:** Se consolida el estado final en documentos de continuidad (`HANDOFF.md` y `APRENDIZAJE.md`) permitiendo al desarrollador o a otro agente de software comprender los riesgos remanentes y los siguientes pasos lógicos sin reiniciar el análisis.

---

## 3. Estructura de Archivos del Núcleo Reutilizable

Para comprender la portabilidad de este diseño, he aquí cómo se organizan los componentes:

```text
fabrica_agentes_ia/
│
├── core/                       <-- Núcleo del Motor (100% Reutilizable)
│   ├── evidence.py             # Carga, selección de palabras clave y validación de citas
│   ├── natural_language.py     # Refinamiento, parseo de intenciones y generación de planes
│   ├── token_budget.py         # Control y estimación de costos en tokens
│   ├── trace.py                # Logger y trazabilidad de eventos del pipeline
│   └── llm.py                  # Adaptadores del LLM
│
├── agents/                     <-- Plantillas de Agentes Especializados (Reutilizables)
│   ├── base.py                 # Clase base y contratos de agentes
│   ├── document_ingestor.py    # Agente de Ingesta
│   ├── evidence_curator.py     # Agente de Curación de Contexto
│   ├── planner.py              # Agente Planificador
│   ├── software_architect.py   # Agente Arquitecto
│   ├── implementer.py          # Agente Implementador
│   ├── qa.py                   # Agente QA
│   └── reviewer.py             # Agente Revisor
│
├── config/                     <-- Configuración Específica del Proyecto destino
│   └── repositories.json       # Definición de repositorios, incumbencias y políticas
│
├── knowledge_base/             <-- Base de Evidencia del Proyecto destino
│   ├── documents_manifest.json # Manifiesto de hashes e inventario de archivos fuente
│   └── evidence.jsonl          # Base de datos portable de hechos citables
│
├── runs/                       <-- Paquetes de Corridas Temporales (Autocontenidos)
│   └── YYYYMMDD-HHMMSS/        # Salidas de agentes, trazabilidad y snapshots
│
├── cli.py                      # Interfaz de Línea de Comandos para automatizaciones
└── harness.py                  # Arnés de validación de calidad y presupuestos
```

---

## 4. Guía para Reutilizar la Fábrica en Otro Proyecto

Para portar este motor a un nuevo proyecto (por ejemplo, "Proyecto X"), siga estos pasos:

1. **Copiar la estructura:** Copie el directorio `fabrica_agentes_ia` a la raíz del nuevo espacio de trabajo.
2. **Definir los Repositorios:** Edite `fabrica_agentes_ia/config/repositories.json` con los módulos, subcarpetas o subproyectos del Proyecto X, estableciendo sus enfoques de contexto (`context_focus`) y sus políticas de calidad (`agent_policy`).
3. **Colocar Documentación:** Deposite todos los documentos técnicos de diseño, arquitectura, contratos o requerimientos del Proyecto X en una carpeta (ej. `documentos_proyecto_x/`).
4. **Construir la Nueva Base de Conocimiento:** Ejecute el comando de escaneo para procesar los documentos y generar el archivo de evidencia:
   ```powershell
   python -m fabrica_agentes_ia.cli scan-docs --docs documentos_proyecto_x
   ```
5. **Establecer la Base Portable:** Copie la evidencia generada en la corrida de refresco a la base estable de la fábrica:
   ```powershell
   Copy-Item fabrica_agentes_ia/runs/refresh/knowledge_base/* fabrica_agentes_ia/knowledge_base/ -Force
   ```
6. **¡Listo para Consultar!** La fábrica ahora responderá consultas sobre el "Proyecto X" respetando sus propias reglas, extrayendo evidencias del nuevo dominio técnico de forma segura y reproducible.
