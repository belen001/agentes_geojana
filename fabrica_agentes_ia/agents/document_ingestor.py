from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from fabrica_agentes_ia.core.documents import chunk_document, discover_documents, extract_document
from fabrica_agentes_ia.core.evidence import save_evidence
from fabrica_agentes_ia.core.models import AgentInput, AgentOutput, DocumentRecord

from .base import Agent


class DocumentIngestorAgent(Agent):
    name = "document_ingestor"
    role = "Procesa documentos del proyecto y produce evidencia trazable."

    def ingest(self, docs_dir: Path, output_dir: Path) -> tuple[list[DocumentRecord], Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        records = [extract_document(path) for path in discover_documents(docs_dir)]
        evidence = []
        for record in records:
            evidence.extend(chunk_document(record))

        evidence_path = output_dir / "evidence.jsonl"
        manifest_path = output_dir / "documents_manifest.json"
        save_evidence(evidence_path, evidence)
        manifest_path.write_text(
            _manifest_json(records),
            encoding="utf-8",
        )
        return records, evidence_path

    def _run(self, agent_input: AgentInput) -> AgentOutput:
        docs_dir = Path(agent_input.context["docs_dir"])
        output_dir = Path(agent_input.context["output_dir"])
        records, evidence_path = self.ingest(docs_dir, output_dir)
        failed = [record for record in records if record.extraction_status != "ok"]
        return AgentOutput(
            agent_name=self.name,
            summary=f"Procesados {len(records)} documentos. Evidencia: {evidence_path}",
            artifacts={
                "evidence_path": str(evidence_path),
                "documents": [_record_summary(record) for record in records],
            },
            warnings=[
                f"{record.path}: {record.extraction_status} ({'; '.join(record.notes)})"
                for record in failed
            ],
        )


def _manifest_json(records: list[DocumentRecord]) -> str:
    import json

    payload = [_record_summary(record) for record in records]
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _record_summary(record: DocumentRecord) -> dict:
    row = asdict(record)
    row["path"] = str(record.path)
    row["text_chars"] = len(record.text)
    row.pop("text", None)
    return row
