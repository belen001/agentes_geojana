# Handoff de la fabrica de agentes IA

## Estado actual

La fabrica esta lista para copiarse o referenciarse desde los tres repositorios de Geojana:

- `frontend_desktop` o alias `froneend_desktop`
- `frontend_mobile`
- `backend`

La base tecnica portable esta en:

```text
fabrica_agentes_ia/knowledge_base/evidence.jsonl
```

Verificacion realizada:

- 20 documentos extraidos correctamente.
- 110 evidencias generadas.
- Pipeline portable validado con `ok: true`.
- Corridas temporales eliminadas.

## Como continuar

Para una tarea natural:

```powershell
python -m fabrica_agentes_ia.cli ask "Usando los agentes de fabrica_agentes_ia realiza crear login en frontend_mobile"
```

El comando genera un paquete con:

- `task.md`
- `selected_context.md`
- `execution_plan.md`
- `ambiguity_report.md`
- `compiled_prompt.md`
- `execution_prompt.md`
- `manifest.json`

Ese paquete es lo que debe leer el agente de codigo antes de modificar un repositorio.

## Decisiones importantes

- `knowledge_base/` es la fuente portable estable.
- `runs/` es temporal y queda ignorado salvo `.gitkeep`.
- Los claims deben citar `evidence_id`.
- Si falta evidencia, se usa `unknown`.
- Los tres repos deben trabajarse de a uno por tarea.
- `ask` clasifica modo natural: implement, review, plan, test, debug, docs, context o unknown.
- El unico documento de uso es `README.md`.

## Riesgos pendientes

- La fabrica conoce la documentacion, pero no ha leido todavia el codigo real de los tres repos.
- Si los repos contradicen la documentacion, se debe registrar la contradiccion y pedir decision.
- La integracion con un LLM real queda como adaptador pendiente en `core/llm.py`.

## Siguiente mejora natural

Agregar conectores por repo para detectar automaticamente framework, comandos de test y estructura del proyecto cuando la fabrica se ejecute dentro de cada repositorio.
