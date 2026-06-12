import pytest
from testcode_tui.widgets.chat_view import ChatView
from testcode_tui.widgets.input_area import InputArea
from testcode_tui.widgets.status_bar import TestCodeStatusBar
from testcode_tui.widgets.session_list import SessionList


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
    sb = TestCodeStatusBar()
    sb.model_name = "claude"
    sb.session_count = 3
    text = sb._build_text()
    assert "claude" in text
    assert "3" in text


def test_session_list():
    sl = SessionList()
    assert sl.id == "session-list"


def test_cli_imports():
    from testcode_cli.main import app
    assert app is not None


def test_tui_app_import():
    from testcode_tui.app import TestCodeApp
    assert TestCodeApp is not None
