from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from fabrica_agentes_ia.agents.document_ingestor import DocumentIngestorAgent
from fabrica_agentes_ia.agents.evidence_curator import EvidenceCuratorAgent
from fabrica_agentes_ia.agents.implementer import ImplementerAgent
from fabrica_agentes_ia.agents.planner import PlannerAgent
from fabrica_agentes_ia.agents.qa import QAAgent
from fabrica_agentes_ia.agents.reviewer import ReviewerAgent
from fabrica_agentes_ia.agents.software_architect import SoftwareArchitectAgent
from fabrica_agentes_ia.core.evidence import load_evidence
from fabrica_agentes_ia.core.evidence import render_pack
from fabrica_agentes_ia.core.models import AgentInput, AgentOutput
from fabrica_agentes_ia.core.trace import TraceLogger


AGENTS = {
    "document_ingestor": DocumentIngestorAgent,
    "evidence_curator": EvidenceCuratorAgent,
    "planner": PlannerAgent,
    "software_architect": SoftwareArchitectAgent,
    "implementer": ImplementerAgent,
    "reviewer": ReviewerAgent,
    "qa": QAAgent,
}


class Orchestrator:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.trace = TraceLogger(run_dir)

    def scan_documents(self, docs_dir: Path) -> Path:
        agent = DocumentIngestorAgent()
        output = agent.run(
            AgentInput(
                task="Ingestar documentacion del proyecto.",
                evidence=[],
                context={"docs_dir": str(docs_dir), "output_dir": str(self.run_dir / "knowledge_base")},
            )
        )
        self._write_output(output)
        self.trace.event("documents_scanned", output.artifacts)
        return Path(output.artifacts["evidence_path"])

    def run_task(self, task: str, evidence_path: Path, max_context_tokens: int = 6000) -> list[AgentOutput]:
        self._snapshot_evidence(evidence_path)
        evidence = load_evidence(evidence_path)
        outputs: list[AgentOutput] = []

        curator = EvidenceCuratorAgent()
        curated = curator.run(
            AgentInput(task=task, evidence=evidence, constraints={"max_context_tokens": max_context_tokens})
        )
        outputs.append(curated)
        selected_ids = set(curated.artifacts["selected_evidence_ids"])
        selected = [item for item in evidence if item.evidence_id in selected_ids]
        context_pack_path = self.run_dir / "selected_context.md"
        context_pack_path.write_text(render_pack(selected), encoding="utf-8")
        curated.artifacts["context_pack_path"] = str(context_pack_path)

        for agent_name in ["planner", "software_architect", "implementer", "qa"]:
            agent = AGENTS[agent_name]()
            output = agent.run(AgentInput(task=task, evidence=selected))
            outputs.append(output)

        review = ReviewerAgent().run(
            AgentInput(
                task="Revisar salidas de agentes.",
                evidence=selected,
                context={"candidate_output": _combined_claims(outputs)},
            )
        )
        outputs.append(review)

        for output in outputs:
            self._write_output(output)
            self.trace.event("agent_output", asdict(output))
        return outputs

    def _write_output(self, output: AgentOutput) -> None:
        path = self.run_dir / f"{output.agent_name}.json"
        path.write_text(json.dumps(asdict(output), ensure_ascii=False, indent=2), encoding="utf-8")

    def _snapshot_evidence(self, evidence_path: Path) -> None:
        target_dir = self.run_dir / "knowledge_base"
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / "evidence.jsonl"
        if evidence_path.resolve() != target.resolve():
            target.write_bytes(evidence_path.read_bytes())


def _combined_claims(outputs: list[AgentOutput]) -> dict:
    claims = []
    for output in outputs:
        claims.extend(output.claims)
    return {"claims": claims}
