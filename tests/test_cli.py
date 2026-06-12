import pytest
from typer.testing import CliRunner
from testcode_cli.main import app

runner = CliRunner()


def test_list_tools():
    result = runner.invoke(app, ["list-tools"])
    assert result.exit_code == 0
    assert "bash" in result.stdout
    assert "file_read" in result.stdout


def test_run_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = runner.invoke(app, ["run", "hello"])
    assert result.exit_code != 0
