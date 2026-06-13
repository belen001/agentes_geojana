from __future__ import annotations

from fabrica_agentes_ia.core.models import AgentInput, AgentOutput

from .base import Agent


class PlannerAgent(Agent):
    name = "planner"
    role = "Convierte una solicitud en un plan verificable y citando evidencia."

    def _run(self, agent_input: AgentInput) -> AgentOutput:
        citations = [item.citation() for item in agent_input.evidence[:3]]
        plan = [
            "Confirmar alcance y restricciones usando solo la evidencia seleccionada.",
            "Dividir el trabajo en cambios pequenos con criterios de aceptacion.",
            "Ejecutar implementacion y pruebas con registro de decisiones.",
            "Revisar reclamos contra citas antes de entregar.",
        ]
        return AgentOutput(
            agent_name=self.name,
            summary="Plan de ejecucion trazable generado.",
            claims=[
                {
                    "text": "El plan depende de las evidencias seleccionadas para evitar supuestos no verificados.",
                    "citations": citations,
                }
            ]
            if citations
            else [],
            decisions=[
                {
                    "decision": "No generar afirmaciones de dominio sin evidencia.",
                    "reason": "El proyecto exige trazabilidad y control de alucinaciones.",
                }
            ],
            artifacts={"plan": plan, "task": agent_input.task},
        )
