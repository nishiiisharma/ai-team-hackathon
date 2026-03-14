from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.project.agents.engines import (
    ContextBuilder,
    CostPolicyEngine,
    ModelRouter,
    TaskComplexityEngine,
    UseCaseClassifier,
)
from src.project.agents.orchestrator import AIBackboneOrchestrator
from src.project.config.settings import get_settings
from src.project.data_loaders.document_processor import DocumentProcessor
from src.project.handlers.response_handler import ResponseFormatter
from src.project.llms.model_selector import ModelSelector
from src.project.retrievers.semantic_retriever import SemanticRetriever
from src.project.telemetry.logger import get_logger
from src.project.validators.guardrails import RiskComplianceValidator, ValidationGuardrail
from src.project.vectordatabase.chroma_client import ChromaVectorStore


def build_orchestrator() -> AIBackboneOrchestrator:
    settings = get_settings()
    logger = get_logger(settings.log_dir)

    vector_store = ChromaVectorStore(
        persist_dir=settings.chroma_persist_dir,
        embedding_model=settings.default_embedding_model,
        api_key=settings.gemini_api_key,
    )
    retriever = SemanticRetriever(vector_store=vector_store)

    return AIBackboneOrchestrator(
        settings=settings,
        classifier=UseCaseClassifier(),
        complexity_engine=TaskComplexityEngine(),
        cost_policy_engine=CostPolicyEngine(),
        risk_validator=RiskComplianceValidator(),
        context_builder=ContextBuilder(retriever=retriever),
        model_router=ModelRouter(),
        model_selector=ModelSelector(settings=settings),
        guardrail=ValidationGuardrail(),
        formatter=ResponseFormatter(),
        logger=logger,
    )


def ingest_if_requested(ingest_path: str | None) -> None:
    if not ingest_path:
        return

    settings = get_settings()
    vector_store = ChromaVectorStore(
        persist_dir=settings.chroma_persist_dir,
        embedding_model=settings.default_embedding_model,
        api_key=settings.gemini_api_key,
    )
    processor = DocumentProcessor()

    path = Path(ingest_path)
    if not path.exists():
        raise FileNotFoundError(f"Ingest file not found: {ingest_path}")

    docs = processor.from_text_file(file_path=str(path))
    vector_store.add_documents(docs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Kombee AI Backbone - Phase 1")
    parser.add_argument("--query", required=True, help="Query to process")
    parser.add_argument(
        "--use-case",
        default=None,
        choices=["chat", "task", "coding", "reasoning"],
        help="Optional explicit use case override",
    )
    parser.add_argument(
        "--expected-output",
        default=None,
        choices=["json"],
        help="Expected output format for validation checks",
    )
    parser.add_argument(
        "--ingest",
        default=None,
        help="Optional text file to ingest into vector store before query",
    )
    args = parser.parse_args()

    ingest_if_requested(args.ingest)
    orchestrator = build_orchestrator()
    final_response = orchestrator.handle_request(
        query=args.query,
        use_case=args.use_case,
        expected_output=args.expected_output,
    )

    payload = {
        "content": final_response.content,
        "metadata": final_response.metadata,
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()

