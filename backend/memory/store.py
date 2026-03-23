from __future__ import annotations
from collections import defaultdict
from typing import Any


class MemoryStore:
    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = defaultdict(dict)

    def get(self, run_id: str, key: str, default: Any = None) -> Any:
        return self._sessions.get(run_id, {}).get(key, default)

    def set(self, run_id: str, key: str, value: Any) -> None:
        self._sessions[run_id][key] = value

    def append(self, run_id: str, key: str, value: Any) -> None:
        if key not in self._sessions[run_id]:
            self._sessions[run_id][key] = []
        self._sessions[run_id][key].append(value)

    def snapshot(self, run_id: str) -> dict[str, Any]:
        return dict(self._sessions.get(run_id, {}))


memory_store = MemoryStore()
