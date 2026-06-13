from __future__ import annotations

import json
from pathlib import Path

from fabrica_agentes_ia.core.evidence import cited_claims_are_valid, load_evidence
from fabrica_agentes_ia.core.token_budget import estimate_tokens


def validate_run(run_dir: Path, max_agent_output_tokens: int = 3000) -> dict:
    problems: list[str] = []
    kb_path = run_dir / "knowledge_base" / "evidence.jsonl"
    evidence = load_evidence(kb_path) if kb_path.exists() else []

    if not evidence:
        problems.append("No hay evidencia extraida. Revisa dependencias de lectura de PDF/DOCX.")

    for path in run_dir.glob("*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        claims = payload.get("claims", [])
        problems.extend(f"{path.name}: {problem}" for problem in cited_claims_are_valid(claims, evidence))
        cost = estimate_tokens(json.dumps(payload, ensure_ascii=False))
        if cost > max_agent_output_tokens:
            problems.append(f"{path.name}: excede presupuesto de salida ({cost}>{max_agent_output_tokens})")

    trace = run_dir / "trace.jsonl"
    if not trace.exists():
        problems.append("No existe trace.jsonl.")

    return {
        "ok": not problems,
        "problems": problems,
        "evidence_count": len(evidence),
        "run_dir": str(run_dir),
    }
