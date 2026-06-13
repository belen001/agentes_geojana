from __future__ import annotations

from fabrica_agentes_ia.core.evidence import keyword_select
from fabrica_agentes_ia.core.models import AgentInput, AgentOutput

from .base import Agent


class EvidenceCuratorAgent(Agent):
    name = "evidence_curator"
    role = "Selecciona solo evidencia relevante para ahorrar tokens."

    def _run(self, agent_input: AgentInput) -> AgentOutput:
        max_tokens = int(agent_input.constraints.get("max_context_tokens", 6000))
        selected = keyword_select(agent_input.task, agent_input.evidence, max_tokens=max_tokens)
        return AgentOutput(
            agent_name=self.name,
            summary=f"Seleccionadas {len(selected)} evidencias relevantes.",
            claims=[
                {
                    "text": "La seleccion de contexto se hizo por coincidencia deterministica de terminos.",
                    "citations": [item.citation() for item in selected[:1]],
                }
            ]
            if selected
            else [],
            artifacts={
                "selected_evidence_ids": [item.evidence_id for item in selected],
                "context_pack_preview": "\n\n".join(item.text[:300] for item in selected[:3]),
            },
        )
