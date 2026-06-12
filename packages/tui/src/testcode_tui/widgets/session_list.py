from textual.widgets import ListView, ListItem, Label


class SessionList(ListView):
    def __init__(self):
        super().__init__(id="session-list")
        self.border_title = "Sessions"
        self._session_map: dict[str, str] = {}

    def set_sessions(self, sessions: list) -> None:
        self.clear()
        self._session_map.clear()
        for s in sessions:
            title = s.title or s.id[:8]
            self._session_map[s.id] = title
            self.append(ListItem(Label(f"{title}")))
