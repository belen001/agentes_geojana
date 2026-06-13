from __future__ import annotations

from pathlib import Path

from fabrica_agentes_ia.orchestrator import Orchestrator


def run(task: str, docs_dir: str = "documentos", run_dir: str = "fabrica_agentes_ia/runs/manual") -> dict:
    orchestrator = Orchestrator(Path(run_dir))
    evidence_path = orchestrator.scan_documents(Path(docs_dir))
    outputs = orchestrator.run_task(task, evidence_path)
    return {"run_dir": run_dir, "agents": [output.agent_name for output in outputs]}
