from __future__ import annotations


class BackboneError(Exception):
    """Base exception for backbone failures."""


class GuardrailViolationError(BackboneError):
    """Raised when guardrails fail after retry attempts."""

