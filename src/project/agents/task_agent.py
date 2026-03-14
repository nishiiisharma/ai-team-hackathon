from __future__ import annotations

from src.project.agents.base_agent import BaseAgent
from src.project.agents.orchestrator import AIBackboneOrchestrator


class TaskAgent(BaseAgent):
    def __init__(self, orchestrator: AIBackboneOrchestrator) -> None:
        self.orchestrator = orchestrator

    def run(self, query: str) -> str:
        result = self.orchestrator.handle_request(query=query, use_case="task")
        return result.content

