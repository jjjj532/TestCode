from collections.abc import Callable
from functools import wraps

from testcode_llm.types import ToolDef


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, tuple[Callable, ToolDef]] = {}

    def register(self, *, description: str, parameters: dict):
        def decorator(func: Callable) -> Callable:
            name = func.__name__
            tool_def = ToolDef(name=name, description=description, parameters=parameters)
            self._tools[name] = (func, tool_def)

            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return func
        return decorator

    def get(self, name: str) -> ToolDef | None:
        pair = self._tools.get(name)
        return pair[1] if pair else None

    async def execute(self, name: str, args: dict) -> str:
        pair = self._tools.get(name)
        if not pair:
            raise ValueError(f"Unknown tool: {name}")
        func, _ = pair
        result = await func(**args)
        return str(result)

    def list_defs(self) -> list[ToolDef]:
        return [td for _, td in self._tools.values()]
