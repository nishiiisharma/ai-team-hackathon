from __future__ import annotations

from dataclasses import dataclass

from src.project.retrievers.semantic_retriever import RetrievalResult, SemanticRetriever


@dataclass(frozen=True)
class ComplexityResult:
    level: str
    score: int


class UseCaseClassifier:
    def classify(self, query: str, explicit_use_case: str | None = None) -> str:
        if explicit_use_case:
            return explicit_use_case

        lowered = query.lower()
        if any(keyword in lowered for keyword in ("code", "python", "bug", "refactor")):
            return "coding"
        if any(keyword in lowered for keyword in ("analyze", "reason", "compare", "decision")):
            return "reasoning"
        return "chat"


class TaskComplexityEngine:
    def evaluate(self, query: str) -> ComplexityResult:
        score = len(query.split())
        if score >= 120:
            return ComplexityResult(level="high", score=score)
        if score >= 40:
            return ComplexityResult(level="medium", score=score)
        return ComplexityResult(level="low", score=score)


@dataclass(frozen=True)
class CostPolicy:
    max_tokens: int
    temperature: float
    budget_tier: str


class CostPolicyEngine:
    def build_policy(self, complexity: ComplexityResult, budget_tier: str) -> CostPolicy:
        if budget_tier == "low":
            return CostPolicy(max_tokens=450, temperature=0.1, budget_tier="low")
        if complexity.level == "high":
            return CostPolicy(max_tokens=1500, temperature=0.2, budget_tier=budget_tier)
        if complexity.level == "medium":
            return CostPolicy(max_tokens=900, temperature=0.2, budget_tier=budget_tier)
        return CostPolicy(max_tokens=500, temperature=0.1, budget_tier=budget_tier)


class ContextBuilder:
    def __init__(self, retriever: SemanticRetriever) -> None:
        self.retriever = retriever

    def build(self, query: str) -> RetrievalResult:
        return self.retriever.retrieve(query=query, top_k=4)


class ModelRouter:
    def route(self, use_case: str, complexity: ComplexityResult) -> str:
        if use_case == "coding":
            return "coding"
        if use_case == "reasoning" or complexity.level == "high":
            return "reasoning"
        return "lightweight"

