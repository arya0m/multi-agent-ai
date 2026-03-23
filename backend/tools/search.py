from __future__ import annotations
import re
import requests
from typing import Any
from .base import BaseTool


FALLBACK_KB = {
    "tesla": [
        "Tesla designs and manufactures electric vehicles, battery systems, and energy products.",
        "Common stock analysis themes: delivery numbers, margins, autonomy narrative, energy business, competition, and macro demand.",
        "A balanced analysis should consider volatility, valuation sensitivity, and execution risk."
    ],
    "ai": [
        "AI orchestration systems often use planner, executor, and tool-calling agents.",
        "Important evaluation dimensions include latency, hallucination control, reliability, and observability.",
        "Memory, retries, and human-in-the-loop fallbacks are common production features."
    ]
}


class SearchTool(BaseTool):
    name = "search"

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        query = str(payload.get("query", "")).strip()
        if not query:
            return {"results": [], "source": "none"}
        topic = re.sub(r"[^a-z0-9 ]", "", query.lower()).split()[0] if query else ""

        # Lightweight public API with graceful fallback.
        try:
            resp = requests.get(
                "https://en.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.quote(query),
                timeout=4,
                headers={"accept": "application/json"},
            )
            if resp.ok:
                data = resp.json()
                extract = data.get("extract")
                if extract:
                    return {
                        "results": [extract],
                        "source": "wikipedia",
                        "title": data.get("title", query),
                    }
        except Exception:
            pass

        results = FALLBACK_KB.get(topic, [
            f"No live web result available for '{query}'.",
            "Fallback mode is active, so the system is using internal heuristics.",
            "The platform still completed the full multi-agent execution path."
        ])
        return {"results": results, "source": "fallback", "title": query}
