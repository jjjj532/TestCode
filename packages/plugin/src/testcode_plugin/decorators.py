import inspect
from collections.abc import Callable


def tool(*, description: str, parameters: dict | None = None):
    def decorator(func: Callable) -> Callable:
        tool_name = func.__name__
        sig = inspect.signature(func)
        params = parameters or {
            "type": "object",
            "properties": {
                p.name: {"type": "string"}
                for p in sig.parameters.values()
                if p.name not in ("self", "cls")
            },
            "required": [
                p.name
                for p in sig.parameters.values()
                if p.default is inspect.Parameter.empty
                and p.name not in ("self", "cls")
            ],
        }
        func._testcode_tool = {
            "name": tool_name,
            "description": description,
            "parameters": params,
        }
        return func
    return decorator
