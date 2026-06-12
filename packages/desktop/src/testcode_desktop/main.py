import os
import sys
import webbrowser

from textual_serve.server import Server


def _app_command() -> str:
    python = sys.executable
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
    env_parts = []
    if not api_key:
        env_parts.append("ANTHROPIC_API_KEY=dummy")
    env_prefix = " ".join(env_parts)
    cmd = f"{python} -m testcode_tui.app"
    if env_parts:
        return f"{env_prefix} {cmd}"
    return cmd


def run_tui():
    """Run the TUI app directly in the terminal."""
    from testcode_tui.app import TestCodeApp

    app = TestCodeApp(llm_provider=None)
    app.run()


def serve_tui(host: str = "127.0.0.1", port: int = 8001, open_browser: bool = False):
    """Serve the TUI as a web application via textual-serve."""
    title = "TestCode Desktop"
    command = _app_command()
    server = Server(command=command, host=host, port=port, title=title)
    if open_browser:
        webbrowser.open(f"http://{host}:{port}")
    print(f"TestCode Desktop running at http://{host}:{port}")
    server.serve()
