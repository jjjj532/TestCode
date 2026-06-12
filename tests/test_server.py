import pytest
from httpx import AsyncClient, ASGITransport
from testcode_server.app import create_app


@pytest.fixture
async def app():
    a = create_app(db_path=":memory:")
    await a.state._store.init()
    return a


@pytest.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_create_and_list_sessions(client):
    resp = await client.post("/api/sessions", json={"model": "claude"})
    assert resp.status_code == 200
    sid = resp.json()["id"]
    assert resp.json()["model"] == "claude"

    resp = await client.get("/api/sessions")
    assert len(resp.json()) == 1

    resp = await client.get(f"/api/sessions/{sid}")
    assert resp.status_code == 200
    assert resp.json()["model"] == "claude"


@pytest.mark.asyncio
async def test_delete_session(client):
    resp = await client.post("/api/sessions", json={"model": "m"})
    sid = resp.json()["id"]

    resp = await client.delete(f"/api/sessions/{sid}")
    assert resp.status_code == 200

    resp = await client.get(f"/api/sessions/{sid}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_messages(client):
    resp = await client.post("/api/sessions", json={"model": "m"})
    sid = resp.json()["id"]

    resp = await client.get(f"/api/sessions/{sid}/messages")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_tools(client):
    resp = await client.get("/api/tools")
    assert resp.status_code == 200
    tools = resp.json()
    assert len(tools) > 0
    names = [t["name"] for t in tools]
    assert "bash" in names


@pytest.mark.asyncio
async def test_send_message_no_llm(client):
    resp = await client.post("/api/sessions", json={"model": "m"})
    sid = resp.json()["id"]

    resp = await client.post(f"/api/sessions/{sid}/messages", json={"text": "hello"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_nonexistent_session(client):
    resp = await client.get("/api/sessions/nonexistent")
    assert resp.status_code == 404

    resp = await client.delete("/api/sessions/nonexistent")
    assert resp.status_code == 404

    resp = await client.get("/api/sessions/nonexistent/messages")
    assert resp.status_code == 404

    resp = await client.post("/api/sessions/nonexistent/messages", json={"text": "hi"})
    assert resp.status_code == 404
