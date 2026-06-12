from testcode_plugin import PluginHooks, tool


@tool(description="Test greet tool")
async def greet(name: str) -> str:
    return f"Hello, {name}!"


@tool(description="Test echo tool")
async def echo(msg: str) -> str:
    return msg


plugin = PluginHooks(tools=[greet, echo])
