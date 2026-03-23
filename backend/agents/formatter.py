from __future__ import annotations
from typing import Any
from backend.agents.base import BaseAgent
from backend.schemas.models import Task


class FormatterAgent(BaseAgent):
    name = "formatter"

    def execute(self, task: Task, context: dict[str, Any]) -> Any:
        insights = context.get("analyzer", {}).get("insights", [])
        research = context.get("researcher", {})
        lines = ["# Final Response", ""]
        for idx, item in enumerate(insights, 1):
            lines.append(f"{idx}. {item}")
        if research.get("source"):
            lines += ["", f"Source mode: **{research.get('source')}**"]
        return {"markdown": "\n".join(lines)}
