from src.project.benchmarking.model_selection_framework import (
    ModelSelectionBenchmarkFramework,
)


def test_framework_selects_best_for_low_budget_lightweight() -> None:
    framework = ModelSelectionBenchmarkFramework(
        config_path="./src/project/config/model_benchmark.yaml"
    )
    decision = framework.select_model(
        role="lightweight",
        complexity_level="low",
        budget_tier="low",
    )
    assert decision.model_name == "gemini-2.5-flash-lite"
    assert decision.total_score > 0


def test_framework_prefers_reasoning_strength_for_high_complexity() -> None:
    framework = ModelSelectionBenchmarkFramework(
        config_path="./src/project/config/model_benchmark.yaml"
    )
    decision = framework.select_model(
        role="reasoning",
        complexity_level="high",
        budget_tier="balanced",
    )
    assert decision.model_name in {
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-3-flash-preview",
    }
    assert "total" in decision.score_breakdown

