from testcode_core.database.engine import DatabaseEngine
from testcode_core.database.models import SessionModel, MessageModel


class SessionStore:
    def __init__(self, db_path: str = "testcode.db"):
        self.db = DatabaseEngine(db_path=db_path)

    async def init(self):
        await self.db.init()

    async def close(self):
        await self.db.close()

    async def create_session(self, model: str = "", title: str = "") -> SessionModel:
        return await self.db.create_session(title=title, model=model)

    async def get_session(self, session_id: str) -> SessionModel | None:
        return await self.db.get_session(session_id)

    async def list_sessions(self) -> list[SessionModel]:
        return await self.db.list_sessions()

    async def update_session(self, session_id: str, **kwargs) -> SessionModel | None:
        return await self.db.update_session(session_id, **kwargs)

    async def delete_session(self, session_id: str) -> bool:
        return await self.db.delete_session(session_id)

    async def add_message(self, session_id: str, role: str, content: str, tool_name: str | None = None, tool_result: str | None = None) -> MessageModel:
        return await self.db.add_message(session_id, role, content, tool_name, tool_result)

    async def get_messages(self, session_id: str) -> list[MessageModel]:
        return await self.db.get_messages(session_id)
