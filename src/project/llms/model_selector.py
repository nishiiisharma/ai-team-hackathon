from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass

from src.project.benchmarking.model_selection_framework import (
    ModelSelectionBenchmarkFramework,
)
from src.project.config.settings import Settings
from src.project.agents.engines import ComplexityResult
from src.project.llms.base import BaseLLMClient
from src.project.llms.gemini_client import GeminiClient


@dataclass(frozen=True)
class RoutedModel:
    role: str
    model_name: str
    client: BaseLLMClient
    selection_metadata: dict[str, object]


class ModelSelector:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.framework = ModelSelectionBenchmarkFramework(
            config_path=settings.benchmark_config_path
        )

    def get_client(
        self,
        role: str,
        complexity: ComplexityResult,
        budget_tier: str,
    ) -> RoutedModel:
        # Active implementation for hackathon free-tier constraint.
        if role in {"reasoning", "coding", "lightweight"}:
            decision = self.framework.select_model(
                role=role,
                complexity_level=complexity.level,
                budget_tier=budget_tier,
            )
            return RoutedModel(
                role=role,
                model_name=decision.model_name,
                client=GeminiClient(
                    api_key=self.settings.gemini_api_key,
                    model_name=decision.model_name,
                ),
                selection_metadata=asdict(decision),
            )

        # Future model routing examples (kept as comments per requirement):
        # if role == "reasoning":
        #     return OpenAIClient(model_name="gpt-4.1")
        # if role == "coding":
        #     return AnthropicClient(model_name="claude-3-7-sonnet")
        # if role == "lightweight":
        #     return OpenAIClient(model_name="gpt-4.1-mini")

        raise ValueError(f"Unsupported model role: {role}")

