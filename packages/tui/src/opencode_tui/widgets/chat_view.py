from textual.widgets import RichLog


class ChatView(RichLog):
    def __init__(self):
        super().__init__(highlight=True, markup=True, max_lines=10000)
        self.border_title = "Chat"

    def add_user_message(self, content: str):
        self.write(f"[bold blue]You:[/bold blue] {content}")

    def add_assistant_message(self, content: str):
        self.write(f"[bold green]Assistant:[/bold green] {content}")

    def add_tool_call(self, tool_name: str, args: dict = None):
        args_str = str(args) if args else ""
        self.write(f"[bold yellow]Tool:[/bold yellow] {tool_name}({args_str})")

    def add_tool_result(self, summary: str):
        self.write(f"[dim]{summary}[/dim]")

    def add_system_message(self, content: str):
        self.write(f"[bold magenta]System:[/bold magenta] {content}")
