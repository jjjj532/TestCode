import os
import tempfile
import pytest
from opencode_core.tools.registry import ToolRegistry
from opencode_core.tools.bash import bash
from opencode_core.tools.file_read import file_read
from opencode_core.tools.file_write import file_write
from opencode_core.tools.file_edit import file_edit
from opencode_core.tools.glob_tool import glob_tool
from opencode_core.tools.grep_tool import grep_tool
from opencode_core.tools.web_fetch import web_fetch


def test_register_and_execute():
    registry = ToolRegistry()

    @registry.register(description="Add two numbers", parameters={
        "type": "object",
        "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
        "required": ["a", "b"]
    })
    async def add(a: float, b: float) -> str:
        return str(a + b)

    tool = registry.get("add")
    assert tool is not None
    assert tool.description == "Add two numbers"


@pytest.mark.asyncio
async def test_execute_tool():
    registry = ToolRegistry()

    @registry.register(description="Echo", parameters={
        "type": "object", "properties": {"msg": {"type": "string"}}, "required": ["msg"]
    })
    async def echo(msg: str) -> str:
        return msg

    result = await registry.execute("echo", {"msg": "hello"})
    assert result == "hello"


@pytest.mark.asyncio
async def test_execute_nonexistent():
    registry = ToolRegistry()
    with pytest.raises(ValueError, match="Unknown tool"):
        await registry.execute("nope", {})


def test_list_defs():
    registry = ToolRegistry()

    @registry.register(description="Tool A", parameters={"type": "object", "properties": {}})
    async def tool_a() -> str: return "a"

    @registry.register(description="Tool B", parameters={"type": "object", "properties": {}})
    async def tool_b() -> str: return "b"

    defs = registry.list_defs()
    names = [d.name for d in defs]
    assert "tool_a" in names
    assert "tool_b" in names


@pytest.mark.asyncio
async def test_bash_echo():
    result = await bash(command="echo hello", timeout=10)
    assert "hello" in result


@pytest.mark.asyncio
async def test_bash_timeout():
    with pytest.raises(TimeoutError):
        await bash(command="sleep 5", timeout=1)


@pytest.mark.asyncio
async def test_file_read():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("hello world")
        path = f.name
    try:
        content = await file_read(path)
        assert "hello world" in content
    finally:
        os.unlink(path)


@pytest.mark.asyncio
async def test_file_read_nonexistent():
    content = await file_read("/tmp/nonexistent_file_xyz_test")
    assert "Error" in content


@pytest.mark.asyncio
async def test_file_write_and_read():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test.txt")
        result = await file_write(path, "hello world")
        assert "written" in result.lower()
        with open(path) as f:
            assert f.read() == "hello world"


@pytest.mark.asyncio
async def test_file_edit():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test.txt")
        with open(path, "w") as f:
            f.write("hello world\nfoo bar\n")
        result = await file_edit(path, "world", "there")
        assert "edited" in result.lower()
        with open(path) as f:
            content = f.read()
        assert "hello there" in content
        assert "foo bar" in content


@pytest.mark.asyncio
async def test_file_edit_not_found():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test.txt")
        with open(path, "w") as f:
            f.write("hello world\n")
        result = await file_edit(path, "nonexistent", "replacement")
        assert "not found" in result.lower()


@pytest.mark.asyncio
async def test_glob():
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "a.py"), "w").close()
        open(os.path.join(d, "b.py"), "w").close()
        open(os.path.join(d, "c.txt"), "w").close()
        result = await glob_tool(pattern="*.py", path=d)
        assert "a.py" in result
        assert "b.py" in result
        assert "c.txt" not in result


@pytest.mark.asyncio
async def test_grep():
    with tempfile.TemporaryDirectory() as d:
        f1 = os.path.join(d, "test1.py")
        f2 = os.path.join(d, "test2.py")
        with open(f1, "w") as f: f.write("def hello(): pass\n")
        with open(f2, "w") as f: f.write("def world(): pass\n")
        result = await grep_tool(pattern="def", path=d, include="*.py")
        assert "test1.py" in result
        assert "test2.py" in result


@pytest.mark.asyncio
async def test_web_fetch():
    result = await web_fetch("https://example.com")
    assert "Example Domain" in result
