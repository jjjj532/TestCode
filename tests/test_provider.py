import pytest
from opencode_llm.providers._anthropic import AnthropicProvider
from opencode_llm.registry import ProviderRegistry
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


def test_anthropic_requires_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        AnthropicProvider()


def test_anthropic_properties():
    provider = AnthropicProvider(api_key="test-key")
    assert provider.name == "anthropic"
    assert provider.default_model


def test_registry_register_and_get():
    registry = ProviderRegistry()
    provider = AnthropicProvider(api_key="test-key")
    registry.register("anthropic", provider)
    assert registry.get("anthropic") is provider
    assert registry.get("nonexistent") is None


def test_registry_list():
    registry = ProviderRegistry()
    provider = AnthropicProvider(api_key="test-key")
    registry.register("anthropic", provider)
    names = registry.list_providers()
    assert "anthropic" in names


from opencode_llm.providers._openai import OpenAIProvider


def test_openai_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        OpenAIProvider()


def test_openai_properties():
    provider = OpenAIProvider(api_key="test-key")
    assert provider.name == "openai"
    assert provider.default_model
