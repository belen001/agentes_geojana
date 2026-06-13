from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class LLMRequest:
    system: str
    prompt: str
    max_output_tokens: int
    temperature: float = 0.0


@dataclass
class LLMResponse:
    text: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class LLMClient(Protocol):
    def complete(self, request: LLMRequest) -> LLMResponse:
        """Ejecuta una completacion con el proveedor configurado."""


class NoopLLMClient:
    """Cliente deliberadamente mudo para evitar llamadas implicitas a IA."""

    def complete(self, request: LLMRequest) -> LLMResponse:
        raise RuntimeError(
            "No hay LLM configurado. Exporta prompts/evidencias o implementa un cliente LLMClient."
        )
