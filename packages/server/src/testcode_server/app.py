import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from testcode_core.agent.loop import AgentLoop
from testcode_core.session.store import SessionStore
from testcode_core.tools.registry import ToolRegistry
from testcode_core.tools.bash import bash
from testcode_core.tools.file_read import file_read
from testcode_core.tools.file_write import file_write
from testcode_core.tools.file_edit import file_edit
from testcode_core.tools.glob_tool import glob_tool
from testcode_core.tools.grep_tool import grep_tool
from testcode_core.tools.web_fetch import web_fetch


class MessageRequest(BaseModel):
    text: str


class SessionCreate(BaseModel):
    model: str = ""
    title: str = ""


def _build_registry() -> ToolRegistry:
    r = ToolRegistry()
    for td, fn in [
        ({"description": "Execute a bash command", "parameters": {"type": "object", "properties": {"command": {"type": "string", "description": "Command to execute"}, "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 120}}, "required": ["command"]}}, bash),
        ({"description": "Read a file", "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "File path"}, "offset": {"type": "integer", "description": "Line offset", "default": 0}, "limit": {"type": "integer", "description": "Max lines", "default": 2000}}, "required": ["path"]}}, file_read),
        ({"description": "Write a new file. Use for creating new files, NOT for editing existing files.", "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "File path"}, "content": {"type": "string", "description": "File content"}}, "required": ["path", "content"]}}, file_write),
        ({"description": "Edit a file by replacing text. Use for surgical edits, not for large rewrites.", "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "File path"}, "old_string": {"type": "string", "description": "Text to replace"}, "new_string": {"type": "string", "description": "Replacement text"}}, "required": ["path", "old_string", "new_string"]}}, file_edit),
        ({"description": "Search files by glob pattern", "parameters": {"type": "object", "properties": {"pattern": {"type": "string", "description": "Glob pattern (e.g. **/*.py)"}, "path": {"type": "string", "description": "Search directory (default cwd)"}}, "required": ["pattern"]}}, glob_tool),
        ({"description": "Search file contents with regex using ripgrep", "parameters": {"type": "object", "properties": {"pattern": {"type": "string", "description": "Regex pattern"}, "path": {"type": "string", "description": "Search directory"}, "include": {"type": "string", "description": "File glob filter (e.g. *.py)"}}, "required": ["pattern"]}}, grep_tool),
        ({"description": "Fetch content from a URL", "parameters": {"type": "object", "properties": {"url": {"type": "string", "description": "URL to fetch"}}, "required": ["url"]}}, web_fetch),
    ]:
        r.register(**td)(fn)
    return r


def create_app(db_path: str = "testcode.db", llm=None):
    store = SessionStore(db_path=db_path)
    registry = _build_registry()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await store.init()
        yield
        await store.close()

    app = FastAPI(title="TestCode API", version="0.1.0", lifespan=lifespan)
    app.state._store = store
    app.state._registry = registry
    if llm:
        app.state.llm = llm

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/api/sessions")
    async def create_session(body: SessionCreate):
        s = await store.create_session(model=body.model or "default", title=body.title)
        return {
            "id": s.id,
            "title": s.title,
            "model": s.model,
            "created_at": s.created_at.isoformat() if s.created_at else "",
        }

    @app.get("/api/sessions")
    async def list_sessions():
        sessions = await store.list_sessions()
        return [
            {
                "id": s.id,
                "title": s.title,
                "model": s.model,
                "created_at": s.created_at.isoformat() if s.created_at else "",
            }
            for s in sessions
        ]

    @app.get("/api/sessions/{session_id}")
    async def get_session(session_id: str):
        s = await store.get_session(session_id)
        if not s:
            raise HTTPException(status_code=404, detail="Session not found")
        return {
            "id": s.id,
            "title": s.title,
            "model": s.model,
            "created_at": s.created_at.isoformat() if s.created_at else "",
        }

    @app.delete("/api/sessions/{session_id}")
    async def delete_session(session_id: str):
        ok = await store.delete_session(session_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"status": "deleted"}

    @app.get("/api/sessions/{session_id}/messages")
    async def get_messages(session_id: str):
        s = await store.get_session(session_id)
        if not s:
            raise HTTPException(status_code=404, detail="Session not found")
        msgs = await store.get_messages(session_id)
        return [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "tool_name": m.tool_name,
                "created_at": m.created_at.isoformat() if m.created_at else "",
            }
            for m in msgs
        ]

    @app.get("/api/tools")
    async def list_tools():
        return [
            {"name": t.name, "description": t.description}
            for t in registry.list_defs()
        ]

    @app.post("/api/sessions/{session_id}/messages")
    async def send_message(session_id: str, body: MessageRequest, request: Request):
        s = await store.get_session(session_id)
        if not s:
            raise HTTPException(status_code=404, detail="Session not found")
        await store.add_message(session_id, role="user", content=body.text)

        llm = getattr(request.app.state, "llm", None)

        async def event_generator():
            if not llm:
                yield {"event": "message", "data": json.dumps({"type": "info", "content": "LLM not configured. Set llm on app.state or pass to create_app()"})}
                return

            loop = AgentLoop(llm=llm, tools=registry)
            async for event in loop.run(body.text):
                data = {"type": event.type, "content": event.content, "tool_name": event.tool_name}
                if event.tool_args:
                    data["tool_args"] = event.tool_args
                yield {"event": "message", "data": json.dumps(data)}
                if event.type == "text" and event.content:
                    await store.add_message(session_id, role="assistant", content=event.content)
                elif event.type == "done":
                    await store.add_message(session_id, role="assistant", content=event.content or "")

        return EventSourceResponse(event_generator())

    return app
