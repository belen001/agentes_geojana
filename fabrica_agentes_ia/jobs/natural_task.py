from __future__ import annotations

from pathlib import Path

from fabrica_agentes_ia.core.natural_language import build_natural_task_package


def run(
    request: str,
    evidence_path: str = "fabrica_agentes_ia/knowledge_base/evidence.jsonl",
    out_dir: str = "fabrica_agentes_ia/runs/natural_task",
    repo: str | None = None,
    mode: str | None = None,
) -> dict:
    return build_natural_task_package(
        request_text=request,
        evidence_path=Path(evidence_path),
        out_dir=Path(out_dir),
        repositories_config=Path("fabrica_agentes_ia/config/repositories.json"),
        current_dir=Path.cwd(),
        repo_override=repo,
        mode_override=mode,
        memory_path=Path("fabrica_agentes_ia/memory/natural_tasks.jsonl"),
    )
