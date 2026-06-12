from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Horizontal

from opencode_tui.widgets.chat_view import ChatView
from opencode_tui.widgets.input_area import InputArea
from opencode_tui.widgets.status_bar import OpenCodeStatusBar
from opencode_tui.widgets.session_list import SessionList
from opencode_core.agent.loop import AgentLoop
from opencode_core.tools.registry import ToolRegistry
from opencode_core.tools.bash import bash
from opencode_core.tools.file_read import file_read
from opencode_core.tools.file_write import file_write
from opencode_core.tools.file_edit import file_edit
from opencode_core.tools.glob_tool import glob_tool
from opencode_core.tools.grep_tool import grep_tool
from opencode_core.tools.web_fetch import web_fetch


def _build_registry() -> ToolRegistry:
    r = ToolRegistry()
    for td, fn in [
        ({"description": "Execute a bash command", "parameters": {"type": "object", "properties": {"command": {"type": "string"}, "timeout": {"type": "integer", "default": 120}}, "required": ["command"]}}, bash),
        ({"description": "Read a file", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "offset": {"type": "integer", "default": 0}, "limit": {"type": "integer", "default": 2000}}, "required": ["path"]}}, file_read),
        ({"description": "Write a new file", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}, file_write),
        ({"description": "Edit a file by replacing text", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "old_string": {"type": "string"}, "new_string": {"type": "string"}}, "required": ["path", "old_string", "new_string"]}}, file_edit),
        ({"description": "Search files by glob pattern", "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}}, "required": ["pattern"]}}, glob_tool),
        ({"description": "Search file contents with regex", "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}, "include": {"type": "string"}}, "required": ["pattern"]}}, grep_tool),
        ({"description": "Fetch content from a URL", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}, web_fetch),
    ]:
        r.register(**td)(fn)
    return r


class MainScreen(Screen):
    def __init__(self, store, llm_provider):
        super().__init__()
        self.store = store
        self.llm = llm_provider
        self.current_session_id = None
        self.registry = _build_registry()

    def compose(self) -> ComposeResult:
        yield OpenCodeStatusBar(id="status-bar")
        with Horizontal():
            yield SessionList(id="session-list")
            yield ChatView(id="chat-view")
        yield InputArea(id="input-area")

    async def on_mount(self) -> None:
        sessions = await self.store.list_sessions()
        self.query_one(SessionList).set_sessions(sessions)
        self.query_one(OpenCodeStatusBar).model_name = self.llm.default_model
        self.query_one(OpenCodeStatusBar).session_count = len(sessions)
        session = await self.store.create_session(model=self.llm.default_model)
        self.current_session_id = session.id
        sessions = await self.store.list_sessions()
        self.query_one(SessionList).set_sessions(sessions)

    async def on_input_area_submitted(self, message: InputArea.Submitted) -> None:
        chat = self.query_one(ChatView)
        chat.add_user_message(message.text)
        await self.store.add_message(self.current_session_id, role="user", content=message.text)

        loop = AgentLoop(llm=self.llm, tools=self.registry)
        full_response = ""
        async for event in loop.run(message.text):
            if event.type == "text":
                full_response += (event.content or "")
            elif event.type == "tool_call":
                chat.add_tool_call(event.tool_name, event.tool_args)
            elif event.type == "tool_result":
                rlen = len(event.tool_result or "")
                chat.add_tool_result(f"[Tool result: {rlen} chars]")

        if full_response:
            chat.add_assistant_message(full_response)
            await self.store.add_message(self.current_session_id, role="assistant", content=full_response)
