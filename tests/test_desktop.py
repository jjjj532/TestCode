import inspect
import pytest
from testcode_desktop.main import _app_command, run_tui, serve_tui


def test_app_command_contains_python():
    cmd = _app_command()
    assert "python" in cmd
    assert "testcode_tui.app" in cmd


def test_app_command_sets_env_if_no_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    cmd = _app_command()
    assert "ANTHROPIC_API_KEY=dummy" in cmd


def test_app_command_skips_env_if_key_set(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    cmd = _app_command()
    assert "ANTHROPIC_API_KEY=dummy" not in cmd


def test_run_tui_signature():
    sig = inspect.signature(run_tui)
    assert sig.return_annotation is inspect.Signature.empty


def test_serve_tui_signature():
    sig = inspect.signature(serve_tui)
    assert "host" in sig.parameters
    assert "port" in sig.parameters
    assert "open_browser" in sig.parameters
