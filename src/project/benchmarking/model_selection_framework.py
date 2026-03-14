from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ModelSelectionDecision:
    model_name: str
    total_score: float
    score_breakdown: dict[str, float]
    role: str
    complexity: str
    budget_tier: str


class ModelSelectionBenchmarkFramework:
    def __init__(self, config_path: str) -> None:
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Benchmark config not found at: {config_path}"
            )
        self._config = self._load_yaml(path)

    def select_model(
        self,
        role: str,
        complexity_level: str,
        budget_tier: str,
    ) -> ModelSelectionDecision:
        models: dict[str, dict[str, float]] = self._config.get("models", {})
        weights: dict[str, float] = self._config.get("weights", {}).get(role, {})
        penalties: dict[str, float] = (
            self._config.get("budget_penalty", {}).get(budget_tier, {})
        )
        boosts: dict[str, float] = (
            self._config.get("complexity_boost", {})
            .get(complexity_level, {})
            .get(role, {})
        )

        if not models:
            raise ValueError("No models configured in benchmark config.")
        if not weights:
            raise ValueError(f"No role weights configured for role: {role}")

        best_model_name = ""
        best_score = float("-inf")
        best_breakdown: dict[str, float] = {}

        for model_name, metrics in models.items():
            score = 0.0
            breakdown: dict[str, float] = {}

            for metric_name, weight in weights.items():
                metric_value = float(metrics.get(metric_name, 0.0))
                metric_score = metric_value * float(weight)
                score += metric_score
                breakdown[metric_name] = round(metric_score, 4)

            for metric_name, boost in boosts.items():
                boost_value = float(metrics.get(metric_name, 0.0)) * float(boost)
                score += boost_value
                breakdown[f"boost_{metric_name}"] = round(boost_value, 4)

            penalty = float(penalties.get(model_name, 0.0))
            score -= penalty
            if penalty > 0:
                breakdown["budget_penalty"] = round(-penalty, 4)

            total = round(score, 4)
            breakdown["total"] = total
            if total > best_score:
                best_model_name = model_name
                best_score = total
                best_breakdown = breakdown

        return ModelSelectionDecision(
            model_name=best_model_name,
            total_score=best_score,
            score_breakdown=best_breakdown,
            role=role,
            complexity=complexity_level,
            budget_tier=budget_tier,
        )

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as file:
            content = yaml.safe_load(file) or {}
        if not isinstance(content, dict):
            raise ValueError("Benchmark config must be a mapping at root.")
        return content

