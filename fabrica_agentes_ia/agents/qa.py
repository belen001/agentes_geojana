from __future__ import annotations

from fabrica_agentes_ia.core.models import AgentInput, AgentOutput

from .base import Agent


class QAAgent(Agent):
    name = "qa"
    role = "Define pruebas y criterios de aceptacion verificables."

    def _run(self, agent_input: AgentInput) -> AgentOutput:
        citations = [item.citation() for item in agent_input.evidence[:2]]
        return AgentOutput(
            agent_name=self.name,
            summary="Checklist de QA generado.",
            claims=[
                {
                    "text": "Los criterios de aceptacion deben derivarse de evidencia disponible o marcarse como supuestos.",
                    "citations": citations,
                }
            ]
            if citations
            else [],
            artifacts={
                "qa_checklist": [
                    "Prueba feliz del flujo principal.",
                    "Prueba de error o ausencia de datos.",
                    "Validacion de trazas y evidencias.",
                    "Revision de presupuesto de tokens.",
                ]
            },
        )
