from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    source_path: str
    source_sha256: str
    chunk_index: int
    text: str
    page: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def citation(self) -> str:
        page = f":p{self.page}" if self.page is not None else ""
        return f"{self.evidence_id}{page}"


@dataclass
class DocumentRecord:
    path: Path
    sha256: str
    kind: str
    extraction_status: str
    text: str = ""
    notes: list[str] = field(default_factory=list)


@dataclass
class AgentInput:
    task: str
    evidence: list[Evidence]
    constraints: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentOutput:
    agent_name: str
    summary: str
    claims: list[dict[str, Any]] = field(default_factory=list)
    decisions: list[dict[str, Any]] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    token_estimate: int = 0


@dataclass
class JobResult:
    job_name: str
    ok: bool
    output_path: Path | None = None
    details: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
