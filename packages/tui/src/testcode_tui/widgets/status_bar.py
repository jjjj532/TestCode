from textual.widgets import Static
from textual.reactive import var


class TestCodeStatusBar(Static):
    model_name = var("")
    session_count = var(0)

    def watch_model_name(self, name: str) -> None:
        self.update(self._build_text())

    def watch_session_count(self, count: int) -> None:
        self.update(self._build_text())

    def _build_text(self) -> str:
        parts = []
        if self.model_name:
            parts.append(f"Model: {self.model_name}")
        if self.session_count:
            parts.append(f"Sessions: {self.session_count}")
        return " | ".join(parts) if parts else "Ready"
