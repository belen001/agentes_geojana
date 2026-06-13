from __future__ import annotations

from fabrica_agentes_ia.core.evidence import cited_claims_are_valid
from fabrica_agentes_ia.core.models import AgentInput, AgentOutput

from .base import Agent


class ReviewerAgent(Agent):
    name = "reviewer"
    role = "Busca riesgos, reclamos sin cita y regresiones."

    def _run(self, agent_input: AgentInput) -> AgentOutput:
        candidate = agent_input.context.get("candidate_output", {})
        claims = candidate.get("claims", []) if isinstance(candidate, dict) else []
        problems = cited_claims_are_valid(claims, agent_input.evidence)
        return AgentOutput(
            agent_name=self.name,
            summary="Revision completada.",
            artifacts={
                "valid": not problems,
                "problems": problems,
                "review_checklist": [
                    "Cada claim tiene evidencia.",
                    "No hay decisiones de dominio sin ADR o documento fuente.",
                    "La salida respeta presupuesto de tokens.",
                    "Las pruebas cubren el riesgo principal.",
                ],
            },
            warnings=problems,
        )
