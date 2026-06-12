import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from testcode_core.database.models import Base, SessionModel, MessageModel


class DatabaseEngine:
    def __init__(self, db_path: str = "testcode.db"):
        self.db_path = db_path
        self._engine = None
        self._session_factory = None

    async def init(self):
        url = f"sqlite+aiosqlite:///{self.db_path}"
        self._engine = create_async_engine(url)
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        if self._engine:
            await self._engine.dispose()

    async def create_session(self, title: str = "", model: str = "") -> SessionModel:
        async with self._session_factory() as session:
            s = SessionModel(id=str(uuid.uuid4()), title=title, model=model)
            session.add(s)
            await session.commit()
            await session.refresh(s)
            return s

    async def get_session(self, session_id: str) -> SessionModel | None:
        async with self._session_factory() as session:
            result = await session.execute(select(SessionModel).where(SessionModel.id == session_id))
            return result.scalar_one_or_none()

    async def list_sessions(self) -> list[SessionModel]:
        async with self._session_factory() as session:
            result = await session.execute(select(SessionModel).order_by(SessionModel.updated_at.desc()))
            return list(result.scalars().all())

    async def update_session(self, session_id: str, **kwargs) -> SessionModel | None:
        async with self._session_factory() as session:
            result = await session.execute(select(SessionModel).where(SessionModel.id == session_id))
            s = result.scalar_one_or_none()
            if s:
                for k, v in kwargs.items():
                    setattr(s, k, v)
                s.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(s)
            return s

    async def delete_session(self, session_id: str) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(select(SessionModel).where(SessionModel.id == session_id))
            s = result.scalar_one_or_none()
            if s:
                await session.delete(s)
                await session.commit()
                return True
            return False

    async def add_message(self, session_id: str, role: str, content: str, tool_name: str | None = None, tool_result: str | None = None) -> MessageModel:
        async with self._session_factory() as session:
            m = MessageModel(session_id=session_id, role=role, content=content, tool_name=tool_name, tool_result=tool_result)
            session.add(m)
            await session.commit()
            await session.refresh(m)
            return m

    async def get_messages(self, session_id: str) -> list[MessageModel]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(MessageModel).where(MessageModel.session_id == session_id).order_by(MessageModel.created_at)
            )
            return list(result.scalars().all())
