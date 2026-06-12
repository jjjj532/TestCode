import pytest
from testcode_core.tools.registry import ToolRegistry
from testcode_plugin.hooks import PluginHooks
from testcode_plugin.decorators import tool
from testcode_plugin.loader import PluginLoader


def test_plugin_hooks_defaults():
    p = PluginHooks()
    assert p.tools == []
    assert p.commands == []
    assert p.on_startup == []
    assert p.on_shutdown == []


def test_plugin_hooks_with_tools():
    async def my_tool(x: str) -> str:
        return x

    p = PluginHooks(tools=[my_tool])
    assert len(p.tools) == 1


@pytest.mark.asyncio
async def test_tool_decorator():
    @tool(description="Add two numbers")
    async def add(a: int, b: int) -> int:
        return a + b

    assert hasattr(add, "_testcode_tool")
    assert add._testcode_tool["name"] == "add"
    assert add._testcode_tool["description"] == "Add two numbers"
    assert "a" in add._testcode_tool["parameters"]["required"]
    assert "b" in add._testcode_tool["parameters"]["required"]
    assert await add(1, 2) == 3


@pytest.mark.asyncio
async def test_tool_decorator_no_params():
    @tool(description="Simple")
    async def ping() -> str:
        return "pong"

    assert ping._testcode_tool["name"] == "ping"
    assert await ping() == "pong"


def test_tool_metadata_isolation():
    @tool(description="A")
    async def fn_a():
        ...

    @tool(description="B")
    async def fn_b():
        ...

    assert fn_a._testcode_tool["description"] == "A"
    assert fn_b._testcode_tool["description"] == "B"


def test_loader_discover_no_plugins():
    loader = PluginLoader(group="testcode.nonexistent")
    plugins = loader.discover()
    assert plugins == []


def test_loader_load_tools():
    @tool(description="Plugin tool")
    async def plugin_tool(data: str) -> str:
        return data

    plugin = PluginHooks(tools=[plugin_tool])
    loader = PluginLoader(group="testcode.nonexistent")
    loader._plugins = [plugin]

    registry = ToolRegistry()
    count = loader.load_tools(registry)
    assert count == 1
    assert registry.get("plugin_tool") is not None
    assert registry.get("plugin_tool").description == "Plugin tool"


@pytest.mark.asyncio
async def test_execute_plugin_tool():
    @tool(description="Upper case")
    async def upper(text: str) -> str:
        return text.upper()

    plugin = PluginHooks(tools=[upper])
    loader = PluginLoader()
    loader._plugins = [plugin]

    registry = ToolRegistry()
    loader.load_tools(registry)

    result = await registry.execute("upper", {"text": "hello"})
    assert result == "HELLO"


def test_plugin_tool_integration_with_registry():
    @tool(description="Echo")
    async def echo(msg: str) -> str:
        return msg

    plugin = PluginHooks(tools=[echo])
    loader = PluginLoader()
    loader._plugins = [plugin]

    registry = ToolRegistry()
    count = loader.load_tools(registry)

    defs = registry.list_defs()
    names = [d.name for d in defs]
    assert "echo" in names
    assert count == 1


def test_discover_real_plugin():
    """Test discovery of a real installed plugin via entry_points."""
    loader = PluginLoader(group="testcode.plugins")
    plugins = loader.discover()
    if plugins:
        assert all(isinstance(p, PluginHooks) for p in plugins)


def test_tool_decorator_preserves_function():
    @tool(description="Identity")
    async def identity(x: str) -> str:
        return x

    assert identity.__name__ == "identity"


@pytest.mark.asyncio
async def test_loader_load_multiple_plugins():
    @tool(description="Tool A")
    async def tool_a(x: str) -> str:
        return x

    @tool(description="Tool B")
    async def tool_b(y: str) -> str:
        return y

    p1 = PluginHooks(tools=[tool_a])
    p2 = PluginHooks(tools=[tool_b])
    loader = PluginLoader()
    loader._plugins = [p1, p2]

    registry = ToolRegistry()
    count = loader.load_tools(registry)
    assert count == 2
    assert registry.get("tool_a") is not None
    assert registry.get("tool_b") is not None
