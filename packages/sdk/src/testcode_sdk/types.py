from dataclasses import dataclass


@dataclass
class Session:
    id: str
    title: str
    model: str
    created_at: str


@dataclass
class Message:
    id: int
    role: str
    content: str
    tool_name: str | None = None
    created_at: str = ""


@dataclass
class ToolInfo:
    name: str
    description: str
