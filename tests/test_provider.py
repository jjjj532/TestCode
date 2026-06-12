import pytest
from opencode_llm.types import Message, StreamEvent, ToolDef
from opencode_llm.provider import LLMProvider


class MockProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "mock"

    @property
    def default_model(self) -> str:
        return "mock-model"

    async def chat(self, messages, tools=None, stream=True, **kwargs):
        yield StreamEvent(type="text", content="mock response")
        yield StreamEvent(type="done", content="mock response")


@pytest.mark.asyncio
async def test_mock_provider():
    provider = MockProvider()
    assert provider.name == "mock"
    assert provider.default_model == "mock-model"
    events = [e async for e in provider.chat([Message(role="user", content="hi")])]
    assert len(events) == 2
    assert events[0].type == "text"
    assert events[1].type == "done"


@pytest.mark.asyncio
async def test_provider_accepts_tools():
    provider = MockProvider()
    tools = [ToolDef(name="bash", description="Run a command", parameters={"type": "object"})]
    events = [e async for e in provider.chat([], tools=tools)]
    assert len(events) == 2
