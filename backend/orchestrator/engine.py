from __future__ import annotations
import asyncio
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Callable, Awaitable
from backend.agents.planner import PlannerAgent
from backend.agents.researcher import ResearcherAgent
from backend.agents.executor import ExecutorAgent
from backend.agents.analyzer import AnalyzerAgent
from backend.agents.formatter import FormatterAgent
from backend.memory.store import memory_store
from backend.schemas.models import RunState, Task, LogEvent


LogCallback = Callable[[LogEvent], Awaitable[None] | None]


class Orchestrator:
    def __init__(self) -> None:
        self.planner = PlannerAgent()
        self.agents = {
            "researcher": ResearcherAgent(),
            "executor": ExecutorAgent(),
            "analyzer": AnalyzerAgent(),
            "formatter": FormatterAgent(),
        }

    async def _emit(self, cb: LogCallback | None, event: LogEvent) -> None:
        if cb is None:
            return
        out = cb(event)
        if asyncio.iscoroutine(out):
            await out

    async def run(self, run_id: str, query: str, log_cb: LogCallback | None = None) -> RunState:
        now = datetime.now(timezone.utc)
        tasks = self.planner.create_plan(query)
        state = RunState(
            run_id=run_id,
            query=query,
            status="RUNNING",
            created_at=now,
            updated_at=now,
            tasks=tasks,
        )
        context: dict[str, Any] = {}
        await self._emit(log_cb, LogEvent(run_id=run_id, timestamp=datetime.now(timezone.utc), source="planner", message=f"Generated {len(tasks)} tasks"))

        for task in state.tasks:
            task.status = "RUNNING"
            state.updated_at = datetime.now(timezone.utc)
            await self._emit(log_cb, LogEvent(run_id=run_id, timestamp=datetime.now(timezone.utc), source=task.agent, message=f"Started: {task.title}"))
            try:
                if task.agent == "planner":
                    task.output = {"message": "Plan generated successfully"}
                else:
                    agent = self.agents[task.agent]
                    task.output = agent.execute(task, context)
                    context[task.agent] = task.output
                    memory_store.set(run_id, task.agent, task.output)
                task.status = "COMPLETED"
                await self._emit(log_cb, LogEvent(run_id=run_id, timestamp=datetime.now(timezone.utc), source=task.agent, message=f"Completed: {task.title}"))
                if task.tool_calls:
                    for call in task.tool_calls:
                        await self._emit(log_cb, LogEvent(
                            run_id=run_id,
                            timestamp=datetime.now(timezone.utc),
                            source=task.agent,
                            message=f"Tool call {call.tool_name}: {call.status}",
                            meta={"tool": call.tool_name, "input": call.input, "output": call.output},
                        ))
            except Exception as exc:
                task.status = "FAILED"
                task.error = str(exc)
                state.status = "FAILED"
                await self._emit(log_cb, LogEvent(run_id=run_id, timestamp=datetime.now(timezone.utc), level="ERROR", source=task.agent, message=f"Failed: {exc}"))
                break

        if state.status != "FAILED":
            state.status = "COMPLETED"
            state.final_output = context.get("formatter", {}).get("markdown")
        state.updated_at = datetime.now(timezone.utc)
        return state
