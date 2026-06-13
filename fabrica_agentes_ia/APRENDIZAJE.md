# Aprendizaje de la fabrica

Este archivo registra errores detectados durante la construccion de la fabrica y la regla que queda incorporada para no repetirlos.

## 1. No serializar objetos internos directamente

Error observado: el ingestor intento escribir `Path` dentro de JSON y fallo con `Object of type WindowsPath is not JSON serializable`.

Aprendizaje:

- Todo artefacto persistido debe ser JSON puro: `str`, `int`, `float`, `bool`, `list`, `dict` o `null`.
- Antes de escribir salidas de agente, convertir rutas a `str`.
- El arnes debe ejecutarse despues de cambios en modelos o artefactos.

## 2. No guardar contexto largo dentro del JSON del agente

Error observado: `evidence_curator.json` excedio el presupuesto porque incluia el contexto completo.

Aprendizaje:

- Los JSON de agente deben ser indices, decisiones y resumen.
- Los contextos largos van en archivos dedicados como `selected_context.md`.
- El presupuesto de salida aplica tambien a artefactos generados por agentes.

## 3. Las corridas deben ser autocontenidas

Error observado: al usar `--use-packaged-context`, el validador no encontraba evidencias dentro del run.

Aprendizaje:

- Cada corrida debe guardar snapshot de `evidence.jsonl`.
- La validacion debe poder ejecutarse sin depender del estado externo.
- Usar evidencia empaquetada no significa perder trazabilidad.

## 4. No entregar artefactos temporales como parte estable

Error observado: las corridas `smoke` y `portable-smoke` eran utiles para validar, pero no para copiar a tres repositorios.

Aprendizaje:

- Mantener `knowledge_base/` como base portable.
- Mantener `runs/` vacio salvo `.gitkeep`.
- Ignorar futuras corridas con `.gitignore`.

## 5. Lenguaje natural necesita un paquete intermedio

Riesgo detectado: pedir "Usando la fabrica realiza task xxx" puede mezclar intencion, repositorio y reglas.

Aprendizaje:

- La entrada natural debe transformarse primero en `task.md`, `selected_context.md`, `execution_prompt.md` y `manifest.json`.
- Si no se detecta repositorio, se marca `unknown` y no se inventa.
- El agente implementador debe leer el repo objetivo antes de editar.

## 6. La intencion debe rutear el workflow

Mejora aplicada: `ask` ahora clasifica la solicitud en `implement`, `review`, `plan`, `test`, `debug`, `docs`, `context` o `unknown`.

Aprendizaje:

- No toda tarea natural debe terminar en cambios de codigo.
- Un "revisa" debe activar modo sin modificaciones.
- Una tarea que menciona varios repos queda bloqueada hasta elegir uno.
- El prompt compilado debe decir modo, repo, plan, criterios y bloqueos.

## Regla operativa

Despues de cada mejora a la fabrica, ejecutar al menos:

```powershell
python -m compileall fabrica_agentes_ia
python -m fabrica_agentes_ia.cli ask "Usando los agentes de fabrica_agentes_ia realiza task de prueba en backend"
```
