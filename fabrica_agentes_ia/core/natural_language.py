from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fabrica_agentes_ia.core.evidence import keyword_select, load_evidence, render_pack


INTENT_KEYWORDS = {
    "implement": ["crear", "implementar", "agregar", "anadir", "añadir", "desarrollar", "corregir", "arreglar"],
    "review": ["revisar", "revisa", "auditar", "audita", "comparar", "verificar", "valida", "validar"],
    "plan": ["planificar", "planifica", "disenar", "diseñar", "proponer", "arquitectura"],
    "test": ["test", "tests", "prueba", "pruebas", "coverage", "cobertura"],
    "debug": ["debug", "depurar", "falla", "fallo", "error", "bug", "excepcion", "excepción"],
    "docs": ["documentar", "documenta", "readme", "docs", "documentacion", "documentación"],
    "context": ["contexto", "solo contexto", "evidencia", "evidencias"],
}

MODE_WORKFLOW = {
    "implement": [
        "Leer estructura y convenciones del repo objetivo.",
        "Generar contexto minimo desde evidence.jsonl.",
        "Ubicar archivos afectados y confirmar alcance.",
        "Implementar cambios pequenos.",
        "Ejecutar pruebas o validaciones disponibles.",
        "Entregar resumen con evidence_id y supuestos unknown.",
    ],
    "review": [
        "Leer codigo relevante sin modificar archivos.",
        "Comparar comportamiento contra selected_context.md.",
        "Listar hallazgos por severidad.",
        "Citar evidence_id por cada hallazgo de dominio.",
        "Separar hechos, riesgos, supuestos y preguntas.",
    ],
    "plan": [
        "Seleccionar evidencia relevante.",
        "Separar alcance, decisiones, riesgos y criterios de aceptacion.",
        "Marcar unknown donde falte evidencia.",
        "Proponer pasos pequenos por repo.",
    ],
    "test": [
        "Identificar comandos de prueba del repo.",
        "Seleccionar flujos de mayor riesgo.",
        "Crear o ajustar pruebas proporcionales.",
        "Ejecutar pruebas tocadas y reportar resultado.",
    ],
    "debug": [
        "Reproducir o localizar el fallo.",
        "Cruzar el comportamiento esperado con evidencia.",
        "Aplicar correccion minima.",
        "Ejecutar prueba de regresion.",
    ],
    "docs": [
        "Leer documentacion existente del repo.",
        "Actualizar solo documentos relacionados.",
        "Citar evidence_id cuando se describan reglas de dominio.",
        "Evitar duplicar informacion ya centralizada.",
    ],
    "context": [
        "Seleccionar evidencia relevante.",
        "Generar selected_context.md.",
        "No modificar codigo.",
        "Entregar lista de evidence_id seleccionados.",
    ],
    "unknown": [
        "Aclarar intencion antes de modificar archivos.",
        "Generar selected_context.md si hay suficientes terminos.",
        "Marcar dudas como unknown.",
    ],
}


@dataclass
class NaturalTask:
    raw_request: str
    task: str
    mode: str
    repository: str | None
    repository_source: str
    mentioned_repositories: list[str]
    confidence: str
    warnings: list[str]
    blocking_issues: list[str]
    assumptions: list[str]
    acceptance_criteria: list[str]
    execution_plan: list[str]
    repo_profile: dict[str, Any] | None


def parse_natural_request(
    text: str,
    repositories_config: Path | None = None,
    current_dir: Path | None = None,
    repo_override: str | None = None,
    mode_override: str | None = None,
) -> NaturalTask:
    normalized = " ".join(text.strip().split())
    repositories = _load_repositories(repositories_config)
    repo_matches = _detect_repositories(normalized, repositories)
    repository, repository_source = _resolve_repository(repo_matches, repositories, current_dir, repo_override)
    mode = mode_override or _detect_mode(normalized)
    task = _strip_invocation_noise(normalized)
    repo_profile = _repo_profile(repository, repositories)

    warnings: list[str] = []
    blocking_issues: list[str] = []
    assumptions: list[str] = []

    if len(repo_matches) > 1 and repo_override is None:
        blocking_issues.append(
            "La solicitud menciona mas de un repositorio. Divide la tarea o usa --repo para elegir uno."
        )

    if repository is None:
        warnings.append("No se detecto repositorio objetivo. Usa --repo o menciona frontend_mobile, frontend_desktop o backend.")

    if mode == "unknown":
        warnings.append("No se detecto una intencion clara. Usa verbos como implementar, revisar, planificar, probar o debuggear.")

    if " y " in task.lower() and any(word in task.lower() for word in ["backend", "frontend", "mobile", "desktop"]):
        assumptions.append("La tarea puede cruzar repositorios; se debe trabajar un repo a la vez.")

    confidence = _confidence(repository, mode, blocking_issues)
    acceptance_criteria = _acceptance_criteria(mode, repository)
    execution_plan = _execution_plan(mode, repo_profile)

    return NaturalTask(
        raw_request=text,
        task=task,
        mode=mode,
        repository=repository,
        repository_source=repository_source,
        mentioned_repositories=repo_matches,
        confidence=confidence,
        warnings=warnings,
        blocking_issues=blocking_issues,
        assumptions=assumptions,
        acceptance_criteria=acceptance_criteria,
        execution_plan=execution_plan,
        repo_profile=repo_profile,
    )


def build_natural_task_package(
    request_text: str,
    evidence_path: Path,
    out_dir: Path,
    repositories_config: Path | None = None,
    max_context_tokens: int = 6000,
    current_dir: Path | None = None,
    repo_override: str | None = None,
    mode_override: str | None = None,
    memory_path: Path | None = None,
) -> dict[str, Any]:
    natural_task = parse_natural_request(
        request_text,
        repositories_config,
        current_dir=current_dir,
        repo_override=repo_override,
        mode_override=mode_override,
    )
    evidence = load_evidence(evidence_path)
    selected = keyword_select(_selection_query(natural_task), evidence, max_tokens=max_context_tokens)

    out_dir.mkdir(parents=True, exist_ok=True)
    selected_context = render_pack(selected)
    compiled_prompt = _compiled_prompt(natural_task)
    (out_dir / "selected_context.md").write_text(selected_context, encoding="utf-8")
    (out_dir / "task.md").write_text(_task_markdown(natural_task), encoding="utf-8")
    (out_dir / "execution_plan.md").write_text(_execution_plan_markdown(natural_task), encoding="utf-8")
    (out_dir / "ambiguity_report.md").write_text(_ambiguity_report(natural_task), encoding="utf-8")
    (out_dir / "compiled_prompt.md").write_text(compiled_prompt, encoding="utf-8")
    (out_dir / "execution_prompt.md").write_text(compiled_prompt, encoding="utf-8")

    manifest = {
        "task": natural_task.task,
        "mode": natural_task.mode,
        "repository": natural_task.repository,
        "repository_source": natural_task.repository_source,
        "confidence": natural_task.confidence,
        "warnings": natural_task.warnings,
        "blocking_issues": natural_task.blocking_issues,
        "assumptions": natural_task.assumptions,
        "acceptance_criteria": natural_task.acceptance_criteria,
        "evidence_path": str(evidence_path),
        "selected_evidence_ids": [item.evidence_id for item in selected],
        "selected_count": len(selected),
        "files": {
            "task": str(out_dir / "task.md"),
            "selected_context": str(out_dir / "selected_context.md"),
            "execution_plan": str(out_dir / "execution_plan.md"),
            "ambiguity_report": str(out_dir / "ambiguity_report.md"),
            "compiled_prompt": str(out_dir / "compiled_prompt.md"),
            "execution_prompt": str(out_dir / "execution_prompt.md"),
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    if memory_path is not None:
        _append_memory(memory_path, natural_task, manifest)
    return manifest


def _load_repositories(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("repositories", [])


def _detect_repositories(text: str, repositories: list[dict[str, Any]]) -> list[str]:
    lower = text.lower()
    matches: list[str] = []
    for repo in repositories:
        names = [repo["name"], *repo.get("aliases", [])]
        if any(name.lower() in lower for name in names):
            matches.append(repo["name"])
    return sorted(set(matches))


def _resolve_repository(
    repo_matches: list[str],
    repositories: list[dict[str, Any]],
    current_dir: Path | None,
    repo_override: str | None,
) -> tuple[str | None, str]:
    if repo_override:
        canonical = _canonical_repo(repo_override, repositories)
        return canonical or repo_override, "override"
    if len(repo_matches) == 1:
        return repo_matches[0], "request"
    detected = _detect_repo_from_path(current_dir, repositories)
    if detected:
        return detected, "current_dir"
    return None, "unknown"


def _canonical_repo(name: str, repositories: list[dict[str, Any]]) -> str | None:
    lower = name.lower()
    for repo in repositories:
        names = [repo["name"], *repo.get("aliases", [])]
        if any(item.lower() == lower for item in names):
            return repo["name"]
    return None


def _detect_repo_from_path(current_dir: Path | None, repositories: list[dict[str, Any]]) -> str | None:
    if current_dir is None:
        return None
    parts = {part.lower() for part in current_dir.resolve().parts}
    for repo in repositories:
        names = [repo["name"], *repo.get("aliases", [])]
        if any(name.lower() in parts for name in names):
            return repo["name"]
    return None


def _detect_mode(text: str) -> str:
    lower = text.lower()
    if "solo contexto" in lower:
        return "context"
    for mode, keywords in INTENT_KEYWORDS.items():
        if any(keyword in lower for keyword in keywords):
            return mode
    return "unknown"


def _strip_invocation_noise(text: str) -> str:
    patterns = [
        r"^usando\s+los?\s+agentes?\s+de\s+\S+\s+realiza\s*:?\s*",
        r"^usando\s+la\s+fabrica\s+realiza\s*:?\s*",
        r"^realiza\s+task\s*:?\s*",
        r"^task\s*:?\s*",
    ]
    task = text
    for pattern in patterns:
        task = re.sub(pattern, "", task, flags=re.IGNORECASE)
    return task.strip().strip('"')


def _repo_profile(repository: str | None, repositories: list[dict[str, Any]]) -> dict[str, Any] | None:
    if repository is None:
        return None
    for repo in repositories:
        if repo["name"] == repository:
            return repo
    return None


def _confidence(repository: str | None, mode: str, blocking_issues: list[str]) -> str:
    if blocking_issues:
        return "blocked"
    if repository and mode != "unknown":
        return "high"
    if repository or mode != "unknown":
        return "medium"
    return "low"


def _acceptance_criteria(mode: str, repository: str | None) -> list[str]:
    criteria = [
        "Cada decision de dominio cita evidence_id.",
        "Los supuestos se marcan como unknown.",
        "La salida final indica archivos tocados o confirma que no hubo cambios.",
    ]
    if repository:
        criteria.append(f"La tarea se limita al repositorio {repository}.")
    if mode == "implement":
        criteria.extend(["Los cambios son pequenos y probados.", "No se cambian contratos compartidos sin confirmacion."])
    elif mode == "review":
        criteria.extend(["No se modifican archivos.", "Los hallazgos se ordenan por severidad."])
    elif mode == "context":
        criteria.append("Solo se genera contexto; no se modifica codigo.")
    return criteria


def _execution_plan(mode: str, repo_profile: dict[str, Any] | None) -> list[str]:
    plan = list(MODE_WORKFLOW.get(mode, MODE_WORKFLOW["unknown"]))
    if repo_profile:
        focus = ", ".join(repo_profile.get("context_focus", []))
        if focus:
            plan.insert(1, f"Priorizar contexto de: {focus}.")
    return plan


def _selection_query(task: NaturalTask) -> str:
    focus = ""
    if task.repo_profile:
        focus = " ".join(task.repo_profile.get("context_focus", []))
    return f"{task.mode} {task.repository or ''} {task.task} {focus}".strip()


def _task_markdown(task: NaturalTask) -> str:
    repo = task.repository or "unknown"
    warnings = "\n".join(f"- {warning}" for warning in task.warnings) or "- Sin advertencias."
    blocking = "\n".join(f"- {issue}" for issue in task.blocking_issues) or "- Sin bloqueos."
    assumptions = "\n".join(f"- {item}" for item in task.assumptions) or "- Sin supuestos iniciales."
    criteria = "\n".join(f"- {item}" for item in task.acceptance_criteria)
    return f"""# Tarea natural

## Modo

{task.mode}

## Repositorio objetivo

{repo}

Fuente de deteccion: `{task.repository_source}`

## Solicitud

{task.task}

## Criterios de aceptacion

{criteria}

## Advertencias

{warnings}

## Bloqueos

{blocking}

## Supuestos

{assumptions}
"""


def _execution_plan_markdown(task: NaturalTask) -> str:
    plan = "\n".join(f"{index}. {step}" for index, step in enumerate(task.execution_plan, start=1))
    policies = "- Sin perfil de repositorio."
    if task.repo_profile:
        policies = "\n".join(f"- {policy}" for policy in task.repo_profile.get("agent_policy", []))
    return f"""# Plan de ejecucion

## Pasos

{plan}

## Politicas del repositorio

{policies}
"""


def _ambiguity_report(task: NaturalTask) -> str:
    warnings = "\n".join(f"- {warning}" for warning in task.warnings) or "- Sin advertencias."
    blocking = "\n".join(f"- {issue}" for issue in task.blocking_issues) or "- Sin bloqueos."
    return f"""# Reporte de ambiguedad

Confianza: `{task.confidence}`

## Advertencias

{warnings}

## Bloqueos

{blocking}

## Regla

Si existe un bloqueo, no implementes cambios. Genera preguntas concretas o divide la tarea.
"""


def _compiled_prompt(task: NaturalTask) -> str:
    repo = task.repository or "unknown"
    plan = "\n".join(f"{index}. {step}" for index, step in enumerate(task.execution_plan, start=1))
    criteria = "\n".join(f"- {item}" for item in task.acceptance_criteria)
    policies = "- Sin perfil de repositorio."
    if task.repo_profile:
        policies = "\n".join(f"- {policy}" for policy in task.repo_profile.get("agent_policy", []))
    return f"""# Prompt compilado para agente de codigo

Usa `selected_context.md` como contexto tecnico de Geojana.

Modo: `{task.mode}`
Repositorio objetivo: `{repo}`
Confianza: `{task.confidence}`

## Tarea

```text
{task.task}
```

## Plan

{plan}

## Criterios de aceptacion

{criteria}

## Politicas del repositorio

{policies}

## Reglas globales

- Lee primero el repo objetivo.
- No afirmes hechos de dominio sin `evidence_id`.
- Si falta evidencia, escribe `unknown` y crea una pregunta o TODO.
- No trabajes varios repos en una misma ejecucion.
- Si `ambiguity_report.md` contiene bloqueos, no edites codigo.
- Ejecuta pruebas o validaciones disponibles cuando el modo implique cambios.
"""


def _append_memory(memory_path: Path, task: NaturalTask, manifest: dict[str, Any]) -> None:
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "task": asdict(task),
        "manifest": {
            "mode": manifest["mode"],
            "repository": manifest["repository"],
            "confidence": manifest["confidence"],
            "selected_count": manifest["selected_count"],
        },
    }
    with memory_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
