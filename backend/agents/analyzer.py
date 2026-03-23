from __future__ import annotations
from typing import Any
from backend.agents.base import BaseAgent
from backend.schemas.models import Task


class AnalyzerAgent(BaseAgent):
    name = "analyzer"

    def execute(self, task: Task, context: dict[str, Any]) -> Any:
        research = context.get("researcher", {})
        execution = context.get("executor", {})
        query = task.input.get("query", "this topic")

        if execution.get("trend"):
            insights = [
                f"Analysis target: {query}",
                f"Trend appears {execution.get('trend')} with change of {execution.get('change_pct')}% over the sampled period.",
                f"Average observed price in the demo dataset: {execution.get('average')}.",
                f"Observed volatility range: {execution.get('volatility_range')} points.",
                "Interpret with caution because fallback/demo market data may be active when no external feed is connected.",
            ]
        else:
            evidence = research.get("results", [])
            metrics = execution.get("computed_summary", {})
            insights = [
                f"Analysis target: {query}",
                f"Collected {metrics.get('evidence_count', len(evidence))} evidence items.",
                f"Approximate evidence word count: {metrics.get('word_count', 0)}.",
                "Key takeaway: the platform successfully planned, researched, executed, analyzed, and prepared a formatted answer.",
                "This output is ideal for demonstrating multi-agent orchestration, not domain-perfect factual research.",
            ]

        return {"insights": insights}
