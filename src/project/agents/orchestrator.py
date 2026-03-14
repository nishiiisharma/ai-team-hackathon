from __future__ import annotations

from dataclasses import asdict
from typing import Any

from src.project.agents.engines import (
    ContextBuilder,
    CostPolicyEngine,
    ModelRouter,
    TaskComplexityEngine,
    UseCaseClassifier,
)
from src.project.config.settings import Settings
from src.project.handlers.error_handler import GuardrailViolationError
from src.project.handlers.response_handler import FinalResponse, ResponseFormatter
from src.project.llms.base import ModelRequest
from src.project.llms.model_selector import ModelSelector
from src.project.telemetry.logger import log_cost_event
from src.project.validators.guardrails import RiskComplianceValidator, ValidationGuardrail


class AIBackboneOrchestrator:
    def __init__(
        self,
        settings: Settings,
        classifier: UseCaseClassifier,
        complexity_engine: TaskComplexityEngine,
        cost_policy_engine: CostPolicyEngine,
        risk_validator: RiskComplianceValidator,
        context_builder: ContextBuilder,
        model_router: ModelRouter,
        model_selector: ModelSelector,
        guardrail: ValidationGuardrail,
        formatter: ResponseFormatter,
        logger: Any,
    ) -> None:
        self.settings = settings
        self.classifier = classifier
        self.complexity_engine = complexity_engine
        self.cost_policy_engine = cost_policy_engine
        self.risk_validator = risk_validator
        self.context_builder = context_builder
        self.model_router = model_router
        self.model_selector = model_selector
        self.guardrail = guardrail
        self.formatter = formatter
        self.logger = logger

    def handle_request(
        self,
        query: str,
        use_case: str | None = None,
        expected_output: str | None = None,
    ) -> FinalResponse:
        classification = self.classifier.classify(query=query, explicit_use_case=use_case)
        complexity = self.complexity_engine.evaluate(query=query)
        policy = self.cost_policy_engine.build_policy(
            complexity=complexity,
            budget_tier=self.settings.default_budget_tier,
        )

        risk_result = self.risk_validator.validate_input(query)
        if not risk_result.passed:
            raise GuardrailViolationError("; ".join(risk_result.reasons))

        context = self.context_builder.build(query=query)
        routed_role = self.model_router.route(use_case=classification, complexity=complexity)
        routed_model = self.model_selector.get_client(
            role=routed_role,
            complexity=complexity,
            budget_tier=policy.budget_tier,
        )

        base_prompt = self._build_prompt(query=query, context=context.context_text)
        attempts = 0
        max_retries = 2

        while True:
            attempts += 1
            response = routed_model.client.generate(
                ModelRequest(
                    prompt=base_prompt,
                    temperature=policy.temperature,
                    max_tokens=policy.max_tokens,
                )
            )

            checks = self._run_validations(
                response_text=response.text,
                expected_output=expected_output,
                use_case=classification,
                sources=context.sources,
            )

            if all(item.passed for item in checks):
                metadata = {
                    "classification": classification,
                    "complexity": asdict(complexity),
                    "policy": asdict(policy),
                    "sources": context.sources,
                    "model_role": routed_role,
                    "selected_model": routed_model.model_name,
                    "model_selection": routed_model.selection_metadata,
                    "model_name": response.model_name,
                    "attempts": attempts,
                }
                log_cost_event(
                    logger=self.logger,
                    data={
                        "model_name": response.model_name,
                        "prompt_tokens": response.prompt_tokens,
                        "completion_tokens": response.completion_tokens,
                        "attempts": attempts,
                    },
                    log_dir=self.settings.log_dir,
                )
                return self.formatter.format(content=response.text, metadata=metadata)

            if attempts > max_retries:
                reasons: list[str] = []
                for item in checks:
                    reasons.extend(item.reasons)
                raise GuardrailViolationError(" ; ".join(reasons))

            feedback = " ".join(reason for item in checks for reason in item.reasons)
            base_prompt = (
                f"{base_prompt}\n\n"
                f"Validation feedback: {feedback}\n"
                "Please regenerate a corrected response that satisfies these checks."
            )

    def _build_prompt(self, query: str, context: str) -> str:
        if context:
            return (
                "Use the following context to answer accurately and cite source IDs.\n\n"
                f"Context:\n{context}\n\n"
                f"User query:\n{query}\n"
            )
        return f"User query:\n{query}\n"

    def _run_validations(
        self,
        response_text: str,
        expected_output: str | None,
        use_case: str,
        sources: list[str],
    ) -> list[Any]:
        checks: list[Any] = []
        checks.append(self.guardrail.validate_tool_calls(response_text=response_text))
        checks.append(
            self.guardrail.detect_hallucination(
                response_text=response_text,
                expected_sources=sources,
            )
        )
        if expected_output == "json":
            checks.append(self.guardrail.validate_json(response_text=response_text))
        if use_case == "coding":
            checks.append(self.guardrail.validate_code(response_text=response_text))
        return checks

