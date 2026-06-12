import pytest
from opencode_core.tools.registry import ToolRegistry


def test_register_and_execute():
    registry = ToolRegistry()

    @registry.register(description="Add two numbers", parameters={
        "type": "object",
        "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
        "required": ["a", "b"]
    })
    async def add(a: float, b: float) -> str:
        return str(a + b)

    tool = registry.get("add")
    assert tool is not None
    assert tool.description == "Add two numbers"


@pytest.mark.asyncio
async def test_execute_tool():
    registry = ToolRegistry()

    @registry.register(description="Echo", parameters={
        "type": "object", "properties": {"msg": {"type": "string"}}, "required": ["msg"]
    })
    async def echo(msg: str) -> str:
        return msg

    result = await registry.execute("echo", {"msg": "hello"})
    assert result == "hello"


@pytest.mark.asyncio
async def test_execute_nonexistent():
    registry = ToolRegistry()
    with pytest.raises(ValueError, match="Unknown tool"):
        await registry.execute("nope", {})


def test_list_defs():
    registry = ToolRegistry()

    @registry.register(description="Tool A", parameters={"type": "object", "properties": {}})
    async def tool_a() -> str: return "a"

    @registry.register(description="Tool B", parameters={"type": "object", "properties": {}})
    async def tool_b() -> str: return "b"

    defs = registry.list_defs()
    names = [d.name for d in defs]
    assert "tool_a" in names
    assert "tool_b" in names
