from __future__ import annotations

from fabrica_agentes_ia.core.models import AgentInput, AgentOutput

from .base import Agent


class ImplementerAgent(Agent):
    name = "implementer"
    role = "Prepara cambios de codigo pequenos, reversibles y auditables."

    def _run(self, agent_input: AgentInput) -> AgentOutput:
        citations = [item.citation() for item in agent_input.evidence[:3]]
        return AgentOutput(
            agent_name=self.name,
            summary="Contrato de implementacion generado.",
            claims=[
                {
                    "text": "La implementacion debe limitarse al alcance probado por la evidencia disponible.",
                    "citations": citations,
                }
            ]
            if citations
            else [],
            artifacts={
                "implementation_rules": [
                    "No editar archivos no relacionados con la tarea.",
                    "Registrar cada archivo modificado en trace.jsonl.",
                    "Agregar pruebas proporcionales al riesgo.",
                    "Detenerse si falta evidencia para una decision de dominio.",
                ]
            },
        )
