# Phase 1 Architecture (Kombee AI Backbone)

## Objective

Build a reusable AI orchestration backbone that provides model routing, validation,
cost control, and observability for future Kombee AI applications.

## Implemented flow

1. User query enters `main.py` (CLI API-gateway equivalent).
2. `UseCaseClassifier` classifies request type.
3. `AIBackboneOrchestrator` runs:
   - `TaskComplexityEngine`
   - `CostPolicyEngine`
   - `RiskComplianceValidator`
   - `ContextBuilder` (RAG retrieval via Chroma)
   - `ModelRouter`
4. Selected model executes via `ModelSelector` and Gemini client.
5. Guardrails run:
   - JSON validation
   - Code syntax check
   - Hallucination (citation check)
   - Tool call safety check
6. Self-healing retry loop runs if checks fail (max retries = 2).
7. Response is formatted and usage/cost logs are written.

## Multi-model strategy

Current execution uses Gemini due free-tier constraints.
Model role abstraction is implemented:

- `reasoning`
- `coding`
- `lightweight`

## Reference framework alignment

Model selection now follows a configurable benchmark framework:

- `src/project/config/model_benchmark.yaml` defines:
  - candidate models
  - weighted scoring by role (`lightweight`, `coding`, `reasoning`)
  - budget-based penalties
  - complexity boosts for high-complexity tasks
- `src/project/benchmarking/model_selection_framework.py` calculates per-model
  weighted scores and selects the best candidate.
- `ModelSelector` uses this decision to choose the execution model and stores
  full selection metadata in the final response.

This ensures model routing is benchmark-driven instead of static.

## RAG design

- `DocumentProcessor` chunks input text.
- Chunks are embedded using Gemini embeddings.
- Vectors are stored in Chroma.
- Retriever returns top-k context snippets with source labels.

## Guardrails and reliability

- Sensitive input patterns are blocked early.
- Output format and code validity are checked.
- Source citation is required when context exists.
- Unsafe tool/database commands are blocked.

## Observability

- `logs/app.log` captures operational logs.
- `logs/llm_usage.log` stores usage token events for cost analysis.

