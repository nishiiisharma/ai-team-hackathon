# Kombee AI Backbone (Phase 1 + Phase 2 Starter)

This repository contains the **Phase 1 implementation** and **Phase 2 practical demonstration pipeline** for Kombee AI Engineering Hackathon 2.0.

## What is implemented

- Use case classification layer
- AI orchestrator core:
  - Task complexity engine
  - Cost policy engine
  - Risk and compliance validator
  - Context builder (RAG)
  - Model router
- Benchmark-driven model selection framework
- Multi-model execution abstraction (Gemini role-based routing)
- Validation and guardrails:
  - JSON validator
  - Code lint/compile check (Python syntax check)
  - Hallucination detector (citation-presence heuristic)
  - Tool call validator
- Self-healing loop (maximum 2 retries)
- Response formatter
- Observability and cost logging
- Phase 2 restaurant inventory assistant:
  - Menu ingestion (PDF/text)
  - AI dish + ingredient extraction
  - Vector storage of dish-ingredient knowledge
  - Dummy DB generation (users/products/orders/order_details)
  - Historical quantity prediction and final cart output

## Tech stack

- LangChain
- Google Gemini (free-tier compatible)
- Chroma vector database

## Quick start

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment:

   ```bash
   copy .env.example .env
   ```

3. Add your Gemini API key in `.env`:

   ```env
   GEMINI_API_KEY=your_key_here
   ```

4. Run a sample request:

   ```bash
   python -m src.project.main --query "Explain RAG in JSON format"
   ```

## Phase 2 quick start

1. Set PostgreSQL URL in `.env`:

   ```env
   PHASE2_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/kombee_phase2
   ```

2. Generate dummy data (PDF requirement: users/products/orders/order_details):

   ```bash
   python -m scripts.generate_phase2_data
   ```

3. Run Phase 2 assistant:

   ```bash
   python -m src.project.phase2.main --menu-path ./examples/sample_menu.txt --user-id 1
   ```

## Structure (Phase 1 relevant)

- `src/project/main.py` - CLI entry point
- `src/project/agents/orchestrator.py` - central orchestration flow
- `src/project/agents/engines.py` - complexity/cost/risk/context/routing engines
- `src/project/llms/` - Gemini client and model selector
- `src/project/benchmarking/model_selection_framework.py` - weighted model benchmark selector
- `src/project/config/model_benchmark.yaml` - benchmark/scoring configuration
- `src/project/retrievers/semantic_retriever.py` - retrieval pipeline
- `src/project/vectordatabase/chroma_client.py` - Chroma wrapper
- `src/project/validators/guardrails.py` - response validation checks
- `src/project/handlers/response_handler.py` - output formatting
- `src/project/telemetry/logger.py` - observability and cost logging
- `src/project/phase2/` - practical demonstration pipeline
- `scripts/generate_phase2_data.py` - dummy database generation script

## Notes

- Free API key constraints are respected by using Gemini.
- Model selection is benchmark-driven (weights, penalties, complexity boosts).
