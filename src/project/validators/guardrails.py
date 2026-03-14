from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailResult:
    passed: bool
    reasons: list[str]


class RiskComplianceValidator:
    BLOCKED_PATTERNS = [
        r"\bpassword\b",
        r"\bcredit\s*card\b",
        r"\bssn\b",
    ]

    def validate_input(self, text: str) -> GuardrailResult:
        reasons: list[str] = []
        lowered = text.lower()
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, lowered):
                reasons.append(f"Blocked sensitive pattern matched: {pattern}")
        return GuardrailResult(passed=not reasons, reasons=reasons)


class ValidationGuardrail:
    def validate_json(self, response_text: str) -> GuardrailResult:
        try:
            json.loads(response_text)
        except json.JSONDecodeError as error:
            return GuardrailResult(
                passed=False,
                reasons=[f"JSON validation failed: {error.msg}"],
            )
        return GuardrailResult(passed=True, reasons=[])

    def validate_code(self, response_text: str) -> GuardrailResult:
        try:
            ast.parse(response_text)
        except SyntaxError as error:
            return GuardrailResult(
                passed=False,
                reasons=[f"Code syntax check failed at line {error.lineno}"],
            )
        return GuardrailResult(passed=True, reasons=[])

    def detect_hallucination(
        self,
        response_text: str,
        expected_sources: list[str],
    ) -> GuardrailResult:
        if not expected_sources:
            return GuardrailResult(passed=True, reasons=[])

        if any(source in response_text for source in expected_sources):
            return GuardrailResult(passed=True, reasons=[])

        return GuardrailResult(
            passed=False,
            reasons=["Response has no citation from retrieved context."],
        )

    def validate_tool_calls(self, response_text: str) -> GuardrailResult:
        disallowed = ["rm -rf", "DROP TABLE", "DELETE FROM users"]
        for token in disallowed:
            if token.lower() in response_text.lower():
                return GuardrailResult(
                    passed=False,
                    reasons=[f"Disallowed tool/database operation detected: {token}"],
                )
        return GuardrailResult(passed=True, reasons=[])

