"""SDK tests using a test server.

Since the SDK creates its own HTTP client internally, we test by
running uvicorn on a random port in a background task.
"""
import asyncio
import socket

import pytest
import uvicorn
from testcode_sdk.client import TestCodeClient
from testcode_server.app import create_app


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture
async def server():
    app = create_app(db_path=":memory:")
    await app.state._store.init()
    port = _free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())
    await asyncio.sleep(0.3)
    yield port
    server.should_exit = True
    await task


@pytest.mark.asyncio
async def test_sdk_health(server):
    port = server
    sdk = TestCodeClient(base_url=f"http://127.0.0.1:{port}")
    try:
        result = await sdk.health()
        assert result["status"] == "ok"
    finally:
        await sdk.close()


@pytest.mark.asyncio
async def test_sdk_create_session(server):
    port = server
    sdk = TestCodeClient(base_url=f"http://127.0.0.1:{port}")
    try:
        session = await sdk.create_session(model="claude")
        assert session.id is not None
        assert session.model == "claude"
    finally:
        await sdk.close()


@pytest.mark.asyncio
async def test_sdk_list_tools(server):
    port = server
    sdk = TestCodeClient(base_url=f"http://127.0.0.1:{port}")
    try:
        tools = await sdk.list_tools()
        assert len(tools) > 0
        assert any(t.name == "bash" for t in tools)
    finally:
        await sdk.close()


@pytest.mark.asyncio
async def test_sdk_list_sessions(server):
    port = server
    sdk = TestCodeClient(base_url=f"http://127.0.0.1:{port}")
    try:
        await sdk.create_session(model="gpt")
        sessions = await sdk.list_sessions()
        assert len(sessions) == 1
    finally:
        await sdk.close()


@pytest.mark.asyncio
async def test_sdk_get_messages(server):
    port = server
    sdk = TestCodeClient(base_url=f"http://127.0.0.1:{port}")
    try:
        session = await sdk.create_session(model="m")
        msgs = await sdk.get_messages(session.id)
        assert msgs == []
    finally:
        await sdk.close()


@pytest.mark.asyncio
async def test_sdk_delete_session(server):
    port = server
    sdk = TestCodeClient(base_url=f"http://127.0.0.1:{port}")
    try:
        session = await sdk.create_session(model="m")
        ok = await sdk.delete_session(session.id)
        assert ok is True
        sessions = await sdk.list_sessions()
        assert len(sessions) == 0
    finally:
        await sdk.close()


@pytest.mark.asyncio
async def test_sdk_send_message(server):
    port = server
    sdk = TestCodeClient(base_url=f"http://127.0.0.1:{port}")
    try:
        session = await sdk.create_session(model="m")
        events = []
        async for event in sdk.send_message(session.id, "hello"):
            events.append(event)
        assert len(events) > 0
    finally:
        await sdk.close()
