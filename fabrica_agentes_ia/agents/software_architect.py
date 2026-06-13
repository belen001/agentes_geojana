from __future__ import annotations

from fabrica_agentes_ia.core.models import AgentInput, AgentOutput

from .base import Agent


class SoftwareArchitectAgent(Agent):
    name = "software_architect"
    role = "Propone arquitectura respetando ADRs y restricciones documentadas."

    def _run(self, agent_input: AgentInput) -> AgentOutput:
        citations = [item.citation() for item in agent_input.evidence[:5]]
        return AgentOutput(
            agent_name=self.name,
            summary="Contrato arquitectonico preparado para revision humana o LLM externo.",
            claims=[
                {
                    "text": "Toda propuesta arquitectonica debe adjuntar una cita por decision relevante.",
                    "citations": citations,
                }
            ]
            if citations
            else [],
            artifacts={
                "architecture_contract": {
                    "required_sections": [
                        "contexto",
                        "decisiones",
                        "alternativas descartadas",
                        "riesgos",
                        "criterios de aceptacion",
                    ],
                    "citation_policy": "Cada decision debe citar evidence_id existente.",
                }
            },
        )
