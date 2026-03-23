from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Literal
from datetime import datetime


class RunRequest(BaseModel):
    query: str = Field(..., min_length=3)
    use_memory: bool = True


class ToolCall(BaseModel):
    tool_name: str
    input: dict[str, Any]
    output: Any | None = None
    status: Literal["PENDING", "SUCCESS", "FAILED"] = "PENDING"
    error: str | None = None


class Task(BaseModel):
    id: str
    agent: Literal["planner", "researcher", "executor", "analyzer", "formatter"]
    title: str
    description: str
    status: Literal["PENDING", "RUNNING", "COMPLETED", "FAILED"] = "PENDING"
    depends_on: list[str] = Field(default_factory=list)
    input: dict[str, Any] = Field(default_factory=dict)
    output: Any | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    error: str | None = None


class LogEvent(BaseModel):
    run_id: str
    timestamp: datetime
    level: Literal["INFO", "ERROR", "WARN"] = "INFO"
    source: str
    message: str
    meta: dict[str, Any] = Field(default_factory=dict)


class RunResponse(BaseModel):
    run_id: str
    status: str
    final_output: str | None = None
    tasks: list[Task] = Field(default_factory=list)


class RunState(BaseModel):
    run_id: str
    query: str
    status: Literal["PENDING", "RUNNING", "COMPLETED", "FAILED"] = "PENDING"
    created_at: datetime
    updated_at: datetime
    tasks: list[Task] = Field(default_factory=list)
    final_output: str | None = None
