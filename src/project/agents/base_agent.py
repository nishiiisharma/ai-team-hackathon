from __future__ import annotations

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    @abstractmethod
    def run(self, query: str) -> str:
        """Run agent with a query string."""

