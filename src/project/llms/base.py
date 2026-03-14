from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelRequest:
    prompt: str
    temperature: float
    max_tokens: int


@dataclass(frozen=True)
class ModelResponse:
    text: str
    model_name: str
    prompt_tokens: int
    completion_tokens: int


class BaseLLMClient(ABC):
    @abstractmethod
    def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate a response from the underlying model."""

