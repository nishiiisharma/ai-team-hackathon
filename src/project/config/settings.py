from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    chroma_persist_dir: str
    default_budget_tier: str
    log_dir: str
    default_embedding_model: str
    default_llm_model: str
    benchmark_config_path: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY is required in environment.")

    return Settings(
        gemini_api_key=gemini_api_key,
        chroma_persist_dir=os.getenv(
            "CHROMA_PERSIST_DIR",
            "./data/vectorstore/chroma",
        ),
        default_budget_tier=os.getenv("DEFAULT_BUDGET_TIER", "balanced"),
        log_dir=os.getenv("LOG_DIR", "./logs"),
        default_embedding_model=os.getenv(
            "DEFAULT_EMBEDDING_MODEL",
            "embedding-001",
        ),
        default_llm_model=os.getenv(
            "DEFAULT_LLM_MODEL",
            "gemini-2.5-flash",
        ),
        benchmark_config_path=os.getenv(
            "BENCHMARK_CONFIG_PATH",
            "./src/project/config/model_benchmark.yaml",
        ),
    )

