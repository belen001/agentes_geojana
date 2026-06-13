# Fabrica de software de agentes de IA para Geojana

Este directorio permite usar agentes de IA sobre Geojana con trazabilidad, contexto tecnico verificable, control de alucinaciones y ahorro de tokens.

La fabrica esta pensada para copiarse o referenciarse desde tres repositorios:

- `frontend_desktop`
- `frontend_mobile`
- `backend`

## Como funciona

La fabrica separa el trabajo en cinco capas:

1. `knowledge_base/`: base tecnica portable extraida desde `documentos/`.
2. `core/`: lectura de documentos, evidencias, seleccion de contexto, trazas, presupuesto y lenguaje natural.
3. `agents/`: agentes especializados para ingesta, curacion de evidencia, planificacion, arquitectura, implementacion, QA y revision.
4. `jobs/`: entradas importables para automatizaciones.
5. `runs/`: paquetes temporales generados por cada ejecucion.

Regla central: si no existe en `evidence.jsonl`, no es un hecho del proyecto. Es un supuesto, una pregunta o `unknown`.

## Base tecnica actual

La base portable esta en:

```text
fabrica_agentes_ia/knowledge_base/evidence.jsonl
```

Estado verificado:

- 20 documentos procesados.
- 110 evidencias generadas.
- Todos los documentos con `extraction_status: ok`.

Archivos relevantes:

- `knowledge_base/documents_manifest.json`: inventario con hash, tipo y estado.
- `knowledge_base/evidence.jsonl`: chunks citables con `evidence_id`.

## Uso principal con lenguaje natural

Ejecuta:

```powershell
python -m fabrica_agentes_ia.cli ask "Usando los agentes de fabrica_agentes_ia realiza crear login respetando Identity Access en frontend_mobile"
```

La fabrica detecta:

- modo: `implement`, `review`, `plan`, `test`, `debug`, `docs`, `context` o `unknown`;
- repositorio objetivo;
- advertencias y bloqueos;
- evidencias relevantes;
- plan de ejecucion;
- prompt compilado para otro agente.

Salida generada:

```text
runs/YYYYMMDD-HHMMSS/natural_task/
  task.md
  selected_context.md
  execution_plan.md
  ambiguity_report.md
  compiled_prompt.md
  execution_prompt.md
  manifest.json
```

Si `ambiguity_report.md` contiene bloqueos, no implementes codigo: divide la tarea o aclara el repo.

## Forzar repo o modo

```powershell
python -m fabrica_agentes_ia.cli ask "revisa autenticacion" --repo backend --mode review
```

Modos disponibles:

- `implement`: crear o modificar funcionalidad.
- `review`: auditar sin modificar archivos.
- `plan`: producir plan tecnico.
- `test`: crear o ajustar pruebas.
- `debug`: investigar y corregir fallos.
- `docs`: actualizar documentacion.
- `context`: solo generar contexto.

## Uso desde Antigravity

Prompt recomendado:

```text
Usando los agentes de C:\Users\belen\Desktop\fabrica\fabrica_agentes_ia realiza:
"DESCRIBE_LA_TAREA"

Repositorio objetivo: frontend_desktop | frontend_mobile | backend

Primero ejecuta:
python -m fabrica_agentes_ia.cli ask "DESCRIBE_LA_TAREA en REPOSITORIO"

Luego lee task.md, selected_context.md, execution_plan.md, ambiguity_report.md y compiled_prompt.md.
No afirmes hechos de dominio sin evidence_id.
Si falta evidencia, marca unknown.
Implementa solo lo necesario y prueba lo tocado.
```

## Uso en los tres repositorios

Opcion A: copiar `fabrica_agentes_ia/` dentro de cada repo.

```text
frontend_desktop/
  fabrica_agentes_ia/
frontend_mobile/
  fabrica_agentes_ia/
backend/
  fabrica_agentes_ia/
```

Dentro del repo:

```powershell
python -m fabrica_agentes_ia.cli ask "crear pantalla de login en frontend_mobile"
```

Opcion B: una sola fabrica compartida.

```text
workspace/
  fabrica_agentes_ia/
  frontend_desktop/
  frontend_mobile/
  backend/
```

Desde un repo objetivo, usa ruta absoluta:

```powershell
python C:\ruta\workspace\fabrica_agentes_ia\cli.py ask "revisar contrato de endpoints en backend" --evidence C:\ruta\workspace\fabrica_agentes_ia\knowledge_base\evidence.jsonl
```

## Prompts listos

Backend:

```text
Usando los agentes de C:\Users\belen\Desktop\fabrica\fabrica_agentes_ia realiza:
"Implementar endpoint o caso de uso backend: DESCRIBE_AQUI"

Repositorio objetivo: backend.
Respeta ADRs, contrato de endpoints, servicios, modelo de datos y autorizacion.
No rompas contratos consumidos por frontend_mobile o frontend_desktop.
Cita evidence_id en decisiones tecnicas y de dominio.
```

Frontend mobile:

```text
Usando los agentes de C:\Users\belen\Desktop\fabrica\fabrica_agentes_ia realiza:
"Implementar pantalla o flujo movil: DESCRIBE_AQUI"

Repositorio objetivo: frontend_mobile.
Respeta Design System, autenticacion, mapas, sighting service y comportamiento offline cuando aplique.
No inventes endpoints ni permisos.
Cita evidence_id en decisiones de UI, API y estados.
```

Frontend desktop:

```text
Usando los agentes de C:\Users\belen\Desktop\fabrica\fabrica_agentes_ia realiza:
"Implementar vista o flujo desktop: DESCRIBE_AQUI"

Repositorio objetivo: frontend_desktop.
Respeta Design System, contrato de endpoints, autenticacion y mapas.
No cambies contratos backend desde frontend.
Cita evidence_id en decisiones de UI y API.
```

Solo contexto:

```text
Usa la fabrica solo para preparar contexto.
Tarea: "DESCRIBE_AQUI".
Repositorio objetivo: REPO.
Entrega selected_context.md y evidence_id relevantes.
No edites codigo todavia.
```

Revision sin cambios:

```text
Usando la fabrica revisa el repo REPO para:
"DESCRIBE_RIESGO_O_CAMBIO"

No modifiques archivos.
Compara codigo real contra selected_context.md.
Lista hallazgos con severidad y evidence_id.
Marca unknown cuando falte evidencia.
```

## Comandos adicionales

Generar solo contexto:

```powershell
python -m fabrica_agentes_ia.cli context --task "task xxx" --evidence fabrica_agentes_ia/knowledge_base/evidence.jsonl --out selected_context.md
```

Ejecutar pipeline completo usando la base portable:

```powershell
python -m fabrica_agentes_ia.cli run --task "task xxx" --use-packaged-context
```

Procesar documentos desde cero:

```powershell
python -m fabrica_agentes_ia.cli scan-docs --docs documentos --run-dir fabrica_agentes_ia/runs/refresh
```

Validar una corrida:

```powershell
python -m fabrica_agentes_ia.cli validate --run-dir fabrica_agentes_ia/runs/NOMBRE_DE_CORRIDA
```

## Actualizar knowledge_base

Cuando cambie `documentos/`:

```powershell
python -m fabrica_agentes_ia.cli scan-docs --docs documentos --run-dir fabrica_agentes_ia/runs/refresh
Copy-Item fabrica_agentes_ia/runs/refresh/knowledge_base/evidence.jsonl fabrica_agentes_ia/knowledge_base/evidence.jsonl -Force
Copy-Item fabrica_agentes_ia/runs/refresh/knowledge_base/documents_manifest.json fabrica_agentes_ia/knowledge_base/documents_manifest.json -Force
```

Luego valida una tarea natural de prueba:

```powershell
python -m fabrica_agentes_ia.cli ask "Usando los agentes de fabrica_agentes_ia realiza revisar autenticacion en backend"
```

## Archivos de continuidad

- `APRENDIZAJE.md`: errores ya cometidos y reglas incorporadas.
- `HANDOFF.md`: estado para continuar el trabajo.
- `profiles/`: perfiles operativos por repo.
- `memory/`: historial JSONL de solicitudes naturales.

## Politica anti-alucinaciones

- Todo claim debe citar un `evidence_id`.
- Las citas se validan contra `evidence.jsonl`.
- Los documentos no extraidos no son evidencia.
- Los desconocidos se marcan como `unknown`.
- Las decisiones se registran en trazas o manifiestos.

## Politica de economia de tokens

- Ingerir documentos una vez.
- Seleccionar contexto por tarea.
- Usar `selected_context.md` en vez de documentos completos.
- Mantener JSON de agentes breve.
- Guardar paquetes de corrida autocontenidos.
