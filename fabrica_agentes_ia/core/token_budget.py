from __future__ import annotations

from dataclasses import dataclass


def estimate_tokens(text: str) -> int:
    """Estimacion conservadora y barata: 1 token cada 4 caracteres."""
    return max(1, (len(text) + 3) // 4)


@dataclass
class TokenBudget:
    name: str
    max_input_tokens: int
    max_output_tokens: int
    reserve_tokens: int = 512

    def fit_context(self, chunks: list[str]) -> list[str]:
        budget = max(0, self.max_input_tokens - self.reserve_tokens)
        selected: list[str] = []
        used = 0
        for chunk in chunks:
            cost = estimate_tokens(chunk)
            if used + cost > budget:
                break
            selected.append(chunk)
            used += cost
        return selected

    def assert_output_budget(self, text: str) -> None:
        used = estimate_tokens(text)
        if used > self.max_output_tokens:
            raise ValueError(
                f"Salida fuera de presupuesto para {self.name}: "
                f"{used}>{self.max_output_tokens} tokens estimados"
            )
