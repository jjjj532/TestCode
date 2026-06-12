import os
from collections.abc import AsyncGenerator

from testcode_llm.provider import LLMProvider
from testcode_llm.types import Message, StreamEvent, ToolDef


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self._api_key:
            raise ValueError("OPENAI_API_KEY is required")
        self._model = model or "gpt-4o"
        self._client = None

    @property
    def name(self) -> str:
        return "openai"

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
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError("Install testcode-llm[openai] to use OpenAI")

        if self._client is None:
            self._client = AsyncOpenAI(api_key=self._api_key)

        formatted = self._to_provider(messages)
        kwargs = dict(model=self._model, messages=formatted, max_tokens=max_tokens, temperature=temperature, stream=True)

        if tools:
            kwargs["tools"] = [{"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.parameters}} for t in tools]

        response = await self._client.chat.completions.create(**kwargs)
        full_content = ""
        async for chunk in response:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                full_content += delta.content
                yield StreamEvent(type="text", content=delta.content)
            if delta and delta.tool_calls:
                for tc in delta.tool_calls:
                    if tc.function:
                        yield StreamEvent(type="tool_call", tool_name=tc.function.name, tool_args={})
        yield StreamEvent(type="done", content=full_content)

    @staticmethod
    def _to_provider(messages: list[Message]) -> list[dict]:
        result = []
        for m in messages:
            entry = {"role": m.role, "content": m.content}
            if m.role == "tool":
                entry["role"] = "tool"
                entry["tool_call_id"] = m.tool_name or ""
                entry["content"] = m.tool_result or ""
            result.append(entry)
        return result
