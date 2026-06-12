import pytest
import tempfile
import os
from testcode_core.database.engine import DatabaseEngine
from testcode_core.database.models import SessionModel, MessageModel


@pytest.mark.asyncio
async def test_create_session():
    with tempfile.TemporaryDirectory() as d:
        db = DatabaseEngine(db_path=os.path.join(d, "test.db"))
        await db.init()
        session = await db.create_session(title="test", model="claude")
        assert session.id is not None
        assert session.title == "test"
        assert session.model == "claude"
        await db.close()


@pytest.mark.asyncio
async def test_list_sessions():
    with tempfile.TemporaryDirectory() as d:
        db = DatabaseEngine(db_path=os.path.join(d, "test.db"))
        await db.init()
        await db.create_session(title="s1", model="m1")
        await db.create_session(title="s2", model="m2")
        sessions = await db.list_sessions()
        assert len(sessions) == 2
        await db.close()


@pytest.mark.asyncio
async def test_add_and_get_messages():
    with tempfile.TemporaryDirectory() as d:
        db = DatabaseEngine(db_path=os.path.join(d, "test.db"))
        await db.init()
        session = await db.create_session(title="test", model="m")
        msg = await db.add_message(session.id, role="user", content="hello")
        assert msg.id is not None
        assert msg.role == "user"
        msgs = await db.get_messages(session.id)
        assert len(msgs) == 1
        assert msgs[0].content == "hello"
        await db.close()


@pytest.mark.asyncio
async def test_delete_session():
    with tempfile.TemporaryDirectory() as d:
        db = DatabaseEngine(db_path=os.path.join(d, "test.db"))
        await db.init()
        s1 = await db.create_session(title="s1", model="m")
        s2 = await db.create_session(title="s2", model="m")
        await db.add_message(s1.id, role="user", content="msg")
        await db.delete_session(s1.id)
        sessions = await db.list_sessions()
        assert len(sessions) == 1
        assert sessions[0].id == s2.id
        await db.close()


@pytest.mark.asyncio
async def test_update_session():
    with tempfile.TemporaryDirectory() as d:
        db = DatabaseEngine(db_path=os.path.join(d, "test.db"))
        await db.init()
        s = await db.create_session(title="old", model="m")
        await db.update_session(s.id, title="new")
        updated = await db.get_session(s.id)
        assert updated.title == "new"
        await db.close()
