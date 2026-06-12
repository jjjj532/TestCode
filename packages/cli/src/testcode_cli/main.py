import asyncio
import os

import typer
import uvicorn
from testcode_core.agent.loop import AgentLoop
from testcode_server.app import create_app as create_server_app
from testcode_tui.app import TestCodeApp
from testcode_core.tools.registry import ToolRegistry
from testcode_core.tools.bash import bash
from testcode_core.tools.file_read import file_read
from testcode_core.tools.file_write import file_write
from testcode_core.tools.file_edit import file_edit
from testcode_core.tools.glob_tool import glob_tool
from testcode_core.tools.grep_tool import grep_tool
from testcode_core.tools.web_fetch import web_fetch

app = typer.Typer()


def _register_tools(registry: ToolRegistry):
    registry.register(description="Execute a bash command", parameters={
        "type": "object", "properties": {
            "command": {"type": "string", "description": "Command to execute"},
            "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 120},
        }, "required": ["command"]
    })(bash)

    registry.register(description="Read a file", parameters={
        "type": "object", "properties": {
            "path": {"type": "string", "description": "File path"},
            "offset": {"type": "integer", "description": "Line offset", "default": 0},
            "limit": {"type": "integer", "description": "Max lines", "default": 2000},
        }, "required": ["path"]
    })(file_read)

    registry.register(description="Write a new file. Use for creating new files, NOT for editing existing files.", parameters={
        "type": "object", "properties": {
            "path": {"type": "string", "description": "File path"},
            "content": {"type": "string", "description": "File content"},
        }, "required": ["path", "content"]
    })(file_write)

    registry.register(description="Edit a file by replacing text. Use for surgical edits, not for large rewrites.", parameters={
        "type": "object", "properties": {
            "path": {"type": "string", "description": "File path"},
            "old_string": {"type": "string", "description": "Text to replace"},
            "new_string": {"type": "string", "description": "Replacement text"},
        }, "required": ["path", "old_string", "new_string"]
    })(file_edit)

    registry.register(description="Search files by glob pattern", parameters={
        "type": "object", "properties": {
            "pattern": {"type": "string", "description": "Glob pattern (e.g. **/*.py)"},
            "path": {"type": "string", "description": "Search directory (default cwd)"},
        }, "required": ["pattern"]
    })(glob_tool)

    registry.register(description="Search file contents with regex using ripgrep", parameters={
        "type": "object", "properties": {
            "pattern": {"type": "string", "description": "Regex pattern"},
            "path": {"type": "string", "description": "Search directory"},
            "include": {"type": "string", "description": "File glob filter (e.g. *.py)"},
        }, "required": ["pattern"]
    })(grep_tool)

    registry.register(description="Fetch content from a URL", parameters={
        "type": "object", "properties": {
            "url": {"type": "string", "description": "URL to fetch"},
        }, "required": ["url"]
    })(web_fetch)

    # Load plugin tools
    try:
        from testcode_plugin.loader import PluginLoader
        loader = PluginLoader()
        loader.discover()
        loader.load_tools(registry)
    except Exception:
        pass


def _get_provider():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        from testcode_llm.providers._anthropic import AnthropicProvider
        return AnthropicProvider(api_key=api_key)
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        from testcode_llm.providers._openai import OpenAIProvider
        return OpenAIProvider(api_key=api_key)
    raise ValueError("Set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable")


@app.command()
def run(prompt: str):
    """Run a single prompt and print the response"""
    async def _run():
        provider = _get_provider()
        registry = ToolRegistry()
        _register_tools(registry)
        loop = AgentLoop(llm=provider, tools=registry)
        async for event in loop.run(prompt):
            if event.type == "text":
                print(event.content, end="", flush=True)
            elif event.type == "tool_call":
                print(f"\n[Calling {event.tool_name}...]\n", end="", flush=True)
            elif event.type == "tool_result":
                tool_len = len(event.tool_result or "")
                print(f"\n[Tool result: {tool_len} chars]\n", end="", flush=True)
        print()

    asyncio.run(_run())


@app.command()
def list_tools():
    """List all available tools"""
    registry = ToolRegistry()
    _register_tools(registry)
    for td in registry.list_defs():
        print(f"  {td.name}: {td.description}")


@app.command()
def dev():
    """Start the TUI application"""
    provider = _get_provider()
    tui_app = TestCodeApp(llm_provider=provider)
    tui_app.run()


@app.command()
def server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Start the HTTP API server"""
    provider = _get_provider()
    server_app = create_server_app(db_path="testcode.db")
    server_app.state.llm = provider
    uvicorn.run(server_app, host=host, port=port, reload=reload)


@app.command()
def desktop(web: bool = False, host: str = "127.0.0.1", port: int = 8001, open_browser: bool = False):
    """Launch TestCode as a desktop app (--web to serve via browser)"""
    from testcode_desktop.main import serve_tui, run_tui
    if web:
        serve_tui(host=host, port=port, open_browser=open_browser)
    else:
        run_tui()


@app.command()
def list_plugins():
    """List installed plugins and their tools"""
    from testcode_plugin.loader import PluginLoader
    loader = PluginLoader()
    plugins = loader.discover()
    if not plugins:
        print("No plugins found")
        return
    for i, p in enumerate(plugins, 1):
        tool_names = []
        for fn in p.tools:
            meta = getattr(fn, "_testcode_tool", {})
            tool_names.append(meta.get("name", fn.__name__))
        print(f"  {i}. Tools: {', '.join(tool_names) or '(none)'}")


if __name__ == "__main__":
    app()
