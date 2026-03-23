from __future__ import annotations
import uuid
from backend.agents.base import BaseAgent
from backend.schemas.models import Task


class PlannerAgent(BaseAgent):
    name = "planner"

    def create_plan(self, query: str) -> list[Task]:
        query_l = query.lower()
        topic = query.strip()

        planner_task = Task(
            id=str(uuid.uuid4()),
            agent="planner",
            title="Decompose user task",
            description="Break the request into executable stages",
            input={"query": query},
        )

        researcher = Task(
            id=str(uuid.uuid4()),
            agent="researcher",
            title="Research the topic",
            description="Fetch supporting information using tools",
            depends_on=[planner_task.id],
            input={"query": topic},
        )

        executor_input = {"query": topic, "mode": "general"}
        if "stock" in query_l or "price" in query_l or "market" in query_l:
            executor_input["mode"] = "finance"
        executor = Task(
            id=str(uuid.uuid4()),
            agent="executor",
            title="Execute analysis",
            description="Run structured computations or transformations",
            depends_on=[researcher.id],
            input=executor_input,
        )

        analyzer = Task(
            id=str(uuid.uuid4()),
            agent="analyzer",
            title="Generate insights",
            description="Transform data into concise insights",
            depends_on=[executor.id],
            input={"query": topic},
        )

        formatter = Task(
            id=str(uuid.uuid4()),
            agent="formatter",
            title="Format final answer",
            description="Prepare final human-readable response",
            depends_on=[analyzer.id],
            input={"query": topic},
        )

        return [planner_task, researcher, executor, analyzer, formatter]
