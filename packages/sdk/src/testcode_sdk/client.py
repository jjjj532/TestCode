import json
from collections.abc import AsyncGenerator

import httpx

from testcode_sdk.types import Session, Message, ToolInfo


class TestCodeClient:
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str | None = None):
        self.base_url = base_url.rstrip("/")
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.AsyncClient(headers=headers)

    async def close(self):
        await self._client.aclose()

    async def health(self) -> dict:
        resp = await self._client.get(f"{self.base_url}/health")
        resp.raise_for_status()
        return resp.json()

    async def create_session(self, model: str = "", title: str = "") -> Session:
        resp = await self._client.post(f"{self.base_url}/api/sessions", json={"model": model, "title": title})
        resp.raise_for_status()
        return Session(**resp.json())

    async def list_sessions(self) -> list[Session]:
        resp = await self._client.get(f"{self.base_url}/api/sessions")
        resp.raise_for_status()
        return [Session(**s) for s in resp.json()]

    async def get_session(self, session_id: str) -> Session:
        resp = await self._client.get(f"{self.base_url}/api/sessions/{session_id}")
        resp.raise_for_status()
        return Session(**resp.json())

    async def delete_session(self, session_id: str) -> bool:
        resp = await self._client.delete(f"{self.base_url}/api/sessions/{session_id}")
        return resp.status_code == 200

    async def get_messages(self, session_id: str) -> list[Message]:
        resp = await self._client.get(f"{self.base_url}/api/sessions/{session_id}/messages")
        resp.raise_for_status()
        return [Message(**m) for m in resp.json()]

    async def send_message(self, session_id: str, text: str) -> AsyncGenerator[dict, None]:
        async with self._client.stream("POST", f"{self.base_url}/api/sessions/{session_id}/messages", json={"text": text}) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                line = line.strip()
                if line.startswith("data: "):
                    yield json.loads(line[6:])

    async def list_tools(self) -> list[ToolInfo]:
        resp = await self._client.get(f"{self.base_url}/api/tools")
        resp.raise_for_status()
        return [ToolInfo(**t) for t in resp.json()]
