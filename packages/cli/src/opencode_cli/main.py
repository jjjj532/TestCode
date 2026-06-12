import asyncio
import os

import typer
from opencode_core.agent.loop import AgentLoop
from opencode_core.tools.registry import ToolRegistry
from opencode_core.tools.bash import bash
from opencode_core.tools.file_read import file_read
from opencode_core.tools.file_write import file_write
from opencode_core.tools.file_edit import file_edit
from opencode_core.tools.glob_tool import glob_tool
from opencode_core.tools.grep_tool import grep_tool
from opencode_core.tools.web_fetch import web_fetch

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


def _get_provider():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        from opencode_llm.providers._anthropic import AnthropicProvider
        return AnthropicProvider(api_key=api_key)
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        from opencode_llm.providers._openai import OpenAIProvider
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


if __name__ == "__main__":
    app()
