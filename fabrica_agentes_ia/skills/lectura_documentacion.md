# Skill: lectura de documentacion

Objetivo: convertir documentos fuente en evidencias citables.

Reglas:

- Procesar `documentos/` antes de planificar o implementar.
- Guardar `sha256`, ruta y estado de extraccion por archivo.
- No usar un PDF como fuente si su estado es `not_extracted` o `failed`.
- Preferir chunks pequenos y reutilizables sobre pegar documentos completos en prompts.

Salida esperada:

- `knowledge_base/documents_manifest.json`
- `knowledge_base/evidence.jsonl`
