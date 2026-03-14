from src.project.agents.engines import (
    CostPolicyEngine,
    ModelRouter,
    TaskComplexityEngine,
    UseCaseClassifier,
)
from src.project.validators.guardrails import ValidationGuardrail


def test_use_case_classifier_detects_coding() -> None:
    classifier = UseCaseClassifier()
    result = classifier.classify("Please debug this python code")
    assert result == "coding"


def test_task_complexity_levels() -> None:
    engine = TaskComplexityEngine()
    low = engine.evaluate("short query")
    medium = engine.evaluate(" ".join(["word"] * 50))
    high = engine.evaluate(" ".join(["word"] * 130))
    assert low.level == "low"
    assert medium.level == "medium"
    assert high.level == "high"


def test_cost_policy_low_budget() -> None:
    complexity_engine = TaskComplexityEngine()
    cost_engine = CostPolicyEngine()
    complexity = complexity_engine.evaluate("x")
    policy = cost_engine.build_policy(complexity=complexity, budget_tier="low")
    assert policy.max_tokens == 450
    assert policy.budget_tier == "low"


def test_model_router_prefers_reasoning_for_high_complexity() -> None:
    complexity_engine = TaskComplexityEngine()
    router = ModelRouter()
    complexity = complexity_engine.evaluate(" ".join(["analysis"] * 140))
    role = router.route(use_case="chat", complexity=complexity)
    assert role == "reasoning"


def test_guardrail_json_validation() -> None:
    guardrail = ValidationGuardrail()
    good = guardrail.validate_json('{"ok": true}')
    bad = guardrail.validate_json("{oops")
    assert good.passed is True
    assert bad.passed is False

