from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path

from .models import Evidence
from .token_budget import estimate_tokens


def save_evidence(path: Path, evidence: list[Evidence]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in evidence:
            handle.write(json.dumps(asdict(item), ensure_ascii=False) + "\n")


def load_evidence(path: Path) -> list[Evidence]:
    rows: list[Evidence] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(Evidence(**json.loads(line)))
    return rows


def keyword_select(task: str, evidence: list[Evidence], max_tokens: int = 6000) -> list[Evidence]:
    terms = _terms(task)
    scored: list[tuple[int, Evidence]] = []
    for item in evidence:
        text = item.text.lower()
        score = sum(text.count(term) for term in terms)
        if score:
            scored.append((score, item))
    if not scored:
        scored = [(1, item) for item in evidence[:8]]

    selected: list[Evidence] = []
    used = 0
    for _, item in sorted(scored, key=lambda row: row[0], reverse=True):
        cost = estimate_tokens(item.text)
        if used + cost > max_tokens:
            break
        selected.append(item)
        used += cost
    return selected


def render_pack(evidence: list[Evidence]) -> str:
    blocks = []
    for item in evidence:
        blocks.append(
            f"[{item.citation()}]\n"
            f"source={item.source_path}\n"
            f"sha256={item.source_sha256}\n"
            f"{item.text}"
        )
    return "\n\n---\n\n".join(blocks)


def cited_claims_are_valid(claims: list[dict], evidence: list[Evidence]) -> list[str]:
    valid = {item.evidence_id for item in evidence}
    problems: list[str] = []
    for index, claim in enumerate(claims):
        citations = claim.get("citations") or []
        if not citations:
            problems.append(f"claim[{index}] no tiene citas")
            continue
        for citation in citations:
            evidence_id = str(citation).split(":")[0]
            if evidence_id not in valid:
                problems.append(f"claim[{index}] cita evidencia inexistente: {citation}")
    return problems


def _terms(text: str) -> list[str]:
    stopwords = {
        "para",
        "como",
        "con",
        "los",
        "las",
        "del",
        "una",
        "uno",
        "por",
        "que",
        "de",
        "la",
        "el",
        "en",
        "y",
        "o",
    }
    terms = re.findall(r"[a-zA-Z0-9_áéíóúñÁÉÍÓÚÑ-]{4,}", text.lower())
    return [term for term in terms if term not in stopwords]
