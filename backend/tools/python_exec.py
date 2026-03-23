from __future__ import annotations
import contextlib
import io
from typing import Any
from .base import BaseTool


class PythonExecTool(BaseTool):
    name = "python_exec"

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        code = str(payload.get("code", "")).strip()
        if not code:
            return {"stdout": "", "result": None}

        allowed_builtins = {
            "print": print,
            "len": len,
            "sum": sum,
            "min": min,
            "max": max,
            "range": range,
            "sorted": sorted,
            "round": round,
        }
        local_vars: dict[str, Any] = {}
        stdout_buffer = io.StringIO()
        with contextlib.redirect_stdout(stdout_buffer):
            exec(code, {"__builtins__": allowed_builtins}, local_vars)
        return {"stdout": stdout_buffer.getvalue(), "locals": local_vars}
