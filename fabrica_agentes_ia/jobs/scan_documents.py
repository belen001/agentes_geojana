from __future__ import annotations

from pathlib import Path

from fabrica_agentes_ia.orchestrator import Orchestrator


def run(docs_dir: str = "documentos", run_dir: str = "fabrica_agentes_ia/runs/manual") -> Path:
    return Orchestrator(Path(run_dir)).scan_documents(Path(docs_dir))
