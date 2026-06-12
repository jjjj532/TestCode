import pytest
from opencode_tui.widgets.chat_view import ChatView
from opencode_tui.widgets.input_area import InputArea
from opencode_tui.widgets.status_bar import OpenCodeStatusBar
from opencode_tui.widgets.session_list import SessionList


def test_chat_view():
    cv = ChatView()
    cv.add_user_message("hello")
    cv.add_assistant_message("world")
    cv.add_tool_call("bash", {"command": "ls"})
    cv.add_tool_result("25 chars")
    assert cv is not None


def test_input_area():
    ia = InputArea()
    assert ia.id == "input-area"
    assert "Enter to send" in (ia.placeholder or "")


def test_status_bar():
    sb = OpenCodeStatusBar()
    sb.model_name = "claude"
    sb.session_count = 3
    text = sb._build_text()
    assert "claude" in text
    assert "3" in text


def test_session_list():
    sl = SessionList()
    assert sl.id == "session-list"


def test_cli_imports():
    from opencode_cli.main import app
    assert app is not None


def test_tui_app_import():
    from opencode_tui.app import OpenCodeApp
    assert OpenCodeApp is not None
