from __future__ import annotations

from abc import ABC, abstractmethod

from fabrica_agentes_ia.core.evidence import cited_claims_are_valid
from fabrica_agentes_ia.core.models import AgentInput, AgentOutput
from fabrica_agentes_ia.core.token_budget import estimate_tokens


class Agent(ABC):
    name = "agent"
    role = "Agente base"

    def run(self, agent_input: AgentInput) -> AgentOutput:
        output = self._run(agent_input)
        output.agent_name = self.name
        output.token_estimate = estimate_tokens(output.summary + str(output.artifacts))
        problems = cited_claims_are_valid(output.claims, agent_input.evidence)
        output.warnings.extend(problems)
        return output

    @abstractmethod
    def _run(self, agent_input: AgentInput) -> AgentOutput:
        raise NotImplementedError
