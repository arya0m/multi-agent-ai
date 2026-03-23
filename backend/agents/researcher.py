from __future__ import annotations
from typing import Any
from backend.agents.base import BaseAgent
from backend.schemas.models import Task, ToolCall
from backend.tools.manager import ToolManager


class ResearcherAgent(BaseAgent):
    name = "researcher"

    def __init__(self) -> None:
        self.tools = ToolManager()

    def execute(self, task: Task, context: dict[str, Any]) -> Any:
        query = task.input.get("query", "")
        call = ToolCall(tool_name="search", input={"query": query})
        try:
            result = self.tools.call("search", {"query": query})
            call.output = result
            call.status = "SUCCESS"
            task.tool_calls.append(call)
            return result
        except Exception as exc:
            call.status = "FAILED"
            call.error = str(exc)
            task.tool_calls.append(call)
            raise
