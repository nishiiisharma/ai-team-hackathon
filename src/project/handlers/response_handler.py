from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FinalResponse:
    content: str
    metadata: dict[str, Any]


class ResponseFormatter:
    def format(self, content: str, metadata: dict[str, Any]) -> FinalResponse:
        return FinalResponse(content=content.strip(), metadata=metadata)

