from textual.app import App
from textual.binding import Binding

from testcode_tui.screens.main_screen import MainScreen
from testcode_core.session.store import SessionStore


class TestCodeApp(App):
    TITLE = "TestCode"
    SUB_TITLE = "AI Coding Agent"
    CSS = """
    Screen {
        layout: vertical;
    }
    #status-bar {
        height: 1;
        dock: top;
        background: $primary;
        color: $text;
        padding: 0 1;
    }
    Horizontal {
        height: 1fr;
    }
    #session-list {
        width: 25;
        border: solid $surface;
        margin: 0 1 0 0;
    }
    #chat-view {
        height: 1fr;
        border: solid $surface;
        margin: 0 0 0 0;
    }
    #input-area {
        height: 3;
        dock: bottom;
        border: solid $surface;
        margin: 0 0 0 0;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("ctrl+l", "clear_chat", "Clear Chat", show=False),
    ]

    def __init__(self, llm_provider, db_path: str = "testcode.db"):
        super().__init__()
        self.llm = llm_provider
        self.db_path = db_path
        self.store = SessionStore(db_path=db_path)

    async def on_mount(self) -> None:
        await self.store.init()
        await self.push_screen(MainScreen(store=self.store, llm_provider=self.llm))

    async def action_clear_chat(self) -> None:
        chat = self.query_one("#chat-view")
        if chat:
            chat.clear()

    async def _on_exit(self) -> None:
        await self.store.close()


if __name__ == "__main__":
    app = TestCodeApp(llm_provider=None)
    app.run()
