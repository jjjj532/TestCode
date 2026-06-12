from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field


@dataclass
class PluginHooks:
    tools: list[Callable[..., Awaitable[str]]] = field(default_factory=list)
    commands: list[Callable] = field(default_factory=list)
    on_startup: list[Callable[[], Awaitable[None]]] = field(default_factory=list)
    on_shutdown: list[Callable[[], Awaitable[None]]] = field(default_factory=list)
