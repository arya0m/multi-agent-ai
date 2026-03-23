from __future__ import annotations
import statistics
from typing import Any
from .base import BaseTool


class FinanceTool(BaseTool):
    name = "finance"

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        topic = str(payload.get("topic", "asset")).strip() or "asset"
        # Demo/fallback data so the project works even without external APIs.
        prices = payload.get("prices") or [210, 214, 212, 219, 225, 223, 228]
        change = round(((prices[-1] - prices[0]) / prices[0]) * 100, 2)
        avg = round(statistics.mean(prices), 2)
        trend = "upward" if prices[-1] >= prices[0] else "downward"
        return {
            "topic": topic,
            "prices": prices,
            "average": avg,
            "change_pct": change,
            "trend": trend,
            "volatility_range": max(prices) - min(prices),
        }
