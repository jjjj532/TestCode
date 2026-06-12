from collections.abc import AsyncGenerator

from opencode_core.agent.context import SystemContext
from opencode_core.tools.registry import ToolRegistry
from opencode_llm.types import Message, StreamEvent


class AgentLoop:
    def __init__(self, llm, tools: ToolRegistry):
        self.llm = llm
        self.tools = tools
        self.context = SystemContext()
        self.messages: list[Message] = []

    async def run(self, task: str) -> AsyncGenerator[StreamEvent, None]:
        system_msg = Message(role="system", content=self.context.collect())
        self.messages = [system_msg]
        self.messages.append(Message(role="user", content=task))

        max_iterations = 20
        for _ in range(max_iterations):
            tool_called = False
            async for event in self.llm.chat(self.messages, self.tools.list_defs()):
                yield event

                if event.type == "tool_call":
                    tool_called = True
                    try:
                        result = await self.tools.execute(event.tool_name, event.tool_args or {})
                    except ValueError as e:
                        result = str(e)
                    self.messages.append(Message(
                        role="tool",
                        content="",
                        tool_name=event.tool_name,
                        tool_result=result,
                    ))
                    yield StreamEvent(type="tool_result", tool_name=event.tool_name, tool_result=result)

                elif event.type == "done":
                    self.messages.append(Message(role="assistant", content=event.content or ""))

            if not tool_called:
                break

        yield StreamEvent(type="done", content="")
