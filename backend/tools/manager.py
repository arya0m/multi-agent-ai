from __future__ import annotations
from typing import Any
from .search import SearchTool
from .python_exec import PythonExecTool
from .finance import FinanceTool


class ToolManager:
    def __init__(self) -> None:
        self.tools = {
            "search": SearchTool(),
            "python_exec": PythonExecTool(),
            "finance": FinanceTool(),
        }

    def call(self, tool_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        return self.tools[tool_name].execute(payload)

    def available(self) -> list[str]:
        return sorted(self.tools.keys())
