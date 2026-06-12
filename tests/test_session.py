import pytest
import tempfile
import os
from testcode_core.session.store import SessionStore


@pytest.mark.asyncio
async def test_session_store_create():
    with tempfile.TemporaryDirectory() as d:
        store = SessionStore(db_path=os.path.join(d, "test.db"))
        await store.init()
        session = await store.create_session(model="claude")
        assert session.id is not None
        assert session.title == ""
        sessions = await store.list_sessions()
        assert len(sessions) == 1
        await store.close()


@pytest.mark.asyncio
async def test_session_store_persist_message():
    with tempfile.TemporaryDirectory() as d:
        store = SessionStore(db_path=os.path.join(d, "test.db"))
        await store.init()
        session = await store.create_session(model="claude")
        await store.add_message(session.id, role="user", content="hello")
        await store.add_message(session.id, role="assistant", content="world")
        msgs = await store.get_messages(session.id)
        assert len(msgs) == 2
        assert msgs[0].content == "hello"
        assert msgs[1].content == "world"
        await store.close()


@pytest.mark.asyncio
async def test_session_store_delete():
    with tempfile.TemporaryDirectory() as d:
        store = SessionStore(db_path=os.path.join(d, "test.db"))
        await store.init()
        s1 = await store.create_session(model="m")
        s2 = await store.create_session(model="m")
        await store.delete_session(s1.id)
        sessions = await store.list_sessions()
        assert len(sessions) == 1
        assert sessions[0].id == s2.id
        await store.close()
