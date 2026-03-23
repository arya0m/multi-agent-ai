from __future__ import annotations
from typing import Any
from backend.agents.base import BaseAgent
from backend.schemas.models import Task, ToolCall
from backend.tools.manager import ToolManager


class ExecutorAgent(BaseAgent):
    name = "executor"

    def __init__(self) -> None:
        self.tools = ToolManager()

    def execute(self, task: Task, context: dict[str, Any]) -> Any:
        mode = task.input.get("mode", "general")
        query = task.input.get("query", "topic")
        if mode == "finance":
            call = ToolCall(tool_name="finance", input={"topic": query})
            result = self.tools.call("finance", {"topic": query})
            call.output = result
            call.status = "SUCCESS"
            task.tool_calls.append(call)
            return result

        research_results = context.get("researcher", {}).get("results", [])
        code = (
            "items = " + repr(research_results) + "\n"
            "word_count = sum(len(x.split()) for x in items)\n"
            "print(f'Collected {len(items)} evidence items')\n"
        )
        call = ToolCall(tool_name="python_exec", input={"code": code})
        result = self.tools.call("python_exec", {"code": code})
        call.output = result
        call.status = "SUCCESS"
        task.tool_calls.append(call)
        return {
            "mode": mode,
            "computed_summary": {
                "evidence_count": len(research_results),
                "word_count": result.get("locals", {}).get("word_count", 0),
            },
            "stdout": result.get("stdout", ""),
        }
