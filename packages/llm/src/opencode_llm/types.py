from dataclasses import dataclass
from typing import Literal


@dataclass
class Message:
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    tool_calls: list[dict] | None = None
    tool_result: str | None = None
    tool_name: str | None = None


@dataclass
class StreamEvent:
    type: Literal["text", "tool_call", "tool_result", "error", "done"]
    content: str | None = None
    tool_name: str | None = None
    tool_args: dict | None = None
    tool_result: str | None = None


@dataclass
class ToolDef:
    name: str
    description: str
    parameters: dict
