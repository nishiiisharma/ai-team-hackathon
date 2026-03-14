from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any


def get_logger(log_dir: str) -> logging.Logger:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("kombee_ai_backbone")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(Path(log_dir) / "app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def log_cost_event(logger: logging.Logger, data: dict[str, Any], log_dir: str) -> None:
    usage_path = Path(log_dir) / "llm_usage.log"
    usage_path.parent.mkdir(parents=True, exist_ok=True)
    with usage_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=True) + "\n")
    logger.info("Cost event logged: %s", data)

