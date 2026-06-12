import pytest
from opencode_core.agent.context import SystemContext
from opencode_core.agent.loop import AgentLoop
from opencode_core.tools.registry import ToolRegistry
from opencode_llm.types import Message, StreamEvent


def test_system_context():
    ctx = SystemContext()
    text = ctx.collect()
    assert "Platform" in text
    assert "python" in text.lower() or "darwin" in text.lower() or "linux" in text.lower()
    assert "CWD" in text


@pytest.mark.asyncio
async def test_agent_loop_with_mock():
    class MockProvider:
        name = "mock"
        default_model = "mock-model"
        async def chat(self, messages, tools=None, stream=True, **kwargs):
            yield StreamEvent(type="text", content="Hello from mock")
            yield StreamEvent(type="done", content="Hello from mock")

    registry = ToolRegistry()
    loop = AgentLoop(llm=MockProvider(), tools=registry)
    events = [e async for e in loop.run("say hello")]
    assert any(e.type == "text" for e in events)
    assert any(e.type == "done" for e in events)


@pytest.mark.asyncio
async def test_agent_loop_tool_calling():
    class MockProvider:
        name = "mock"
        default_model = "mock-model"
        def __init__(self):
            self.call_count = 0
        async def chat(self, messages, tools=None, stream=True, **kwargs):
            self.call_count += 1
            if self.call_count == 1:
                yield StreamEvent(type="tool_call", tool_name="mock_tool", tool_args={"x": "1"})
            else:
                yield StreamEvent(type="text", content="done")
                yield StreamEvent(type="done", content="done")

    registry = ToolRegistry()
    @registry.register(description="Mock", parameters={
        "type": "object", "properties": {"x": {"type": "string"}}, "required": ["x"]
    })
    async def mock_tool(x: str) -> str:
        return f"result: {x}"

    loop = AgentLoop(llm=MockProvider(), tools=registry)
    events = [e async for e in loop.run("use tool")]
    tool_results = [e for e in events if e.type == "tool_result"]
    assert len(tool_results) == 1
    assert "result: 1" in tool_results[0].tool_result
