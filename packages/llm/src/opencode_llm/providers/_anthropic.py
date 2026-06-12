import os
from collections.abc import AsyncGenerator

from opencode_llm.provider import LLMProvider
from opencode_llm.types import Message, StreamEvent, ToolDef


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self._api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")
        self._model = model or "claude-sonnet-4-20250514"
        self._client = None

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def default_model(self) -> str:
        return self._model

    async def chat(
        self,
        messages: list[Message],
        tools: list[ToolDef] | None = None,
        stream: bool = True,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> AsyncGenerator[StreamEvent, None]:
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            raise ImportError("Install opencode-llm[anthropic] to use Anthropic")

        if self._client is None:
            self._client = AsyncAnthropic(api_key=self._api_key)

        formatted = self._to_provider(messages)
        kwargs = dict(model=self._model, messages=formatted, max_tokens=max_tokens, temperature=temperature)

        if tools:
            kwargs["tools"] = [{"name": t.name, "description": t.description, "input_schema": t.parameters} for t in tools]

        async with self._client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield StreamEvent(type="text", content=text)
            final = await stream.get_final_message()
            for block in final.content:
                if block.type == "tool_use":
                    yield StreamEvent(type="tool_call", tool_name=block.name, tool_args=block.input)
            yield StreamEvent(type="done", content=final.content[0].text if final.content else "")

    @staticmethod
    def _to_provider(messages: list[Message]) -> list[dict]:
        result = []
        for m in messages:
            entry = {"role": m.role, "content": m.content}
            if m.role == "tool":
                entry["role"] = "user"
                entry["content"] = [{"type": "tool_result", "tool_use_id": m.tool_name or "", "content": m.tool_result or ""}]
            result.append(entry)
        return result
