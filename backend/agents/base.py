from __future__ import annotations
from typing import Any
from backend.schemas.models import Task


class BaseAgent:
    name: str = "base"

    def execute(self, task: Task, context: dict[str, Any]) -> Any:
        raise NotImplementedError
