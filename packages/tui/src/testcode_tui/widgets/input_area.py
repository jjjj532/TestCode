from textual.widgets import TextArea
from textual.binding import Binding
from textual.message import Message


class InputArea(TextArea):
    class Submitted(Message):
        def __init__(self, text: str) -> None:
            self.text = text
            super().__init__()

    BINDINGS = [
        Binding("enter", "submit", "Send", show=False),
    ]

    def __init__(self):
        super().__init__(
            id="input-area",
            placeholder="Type your message... (Enter to send)",
            soft_wrap=True,
        )
        self.border_title = "Input"

    def action_submit(self):
        text = self.text.strip()
        if text:
            self.post_message(self.Submitted(text))
            self.text = ""
