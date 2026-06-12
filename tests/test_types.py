from opencode_llm.types import Message, StreamEvent, ToolDef


def test_message_defaults():
    msg = Message(role="user", content="hello")
    assert msg.role == "user"
    assert msg.content == "hello"
    assert msg.tool_calls is None
    assert msg.tool_result is None


def test_message_with_tool_call():
    msg = Message(role="assistant", content="", tool_calls=[{"name": "bash", "args": {"command": "ls"}}])
    assert msg.tool_calls[0]["name"] == "bash"


def test_stream_event_text():
    event = StreamEvent(type="text", content="hello")
    assert event.type == "text"
    assert event.content == "hello"


def test_stream_event_tool_call():
    event = StreamEvent(type="tool_call", tool_name="bash", tool_args={"command": "ls"})
    assert event.tool_name == "bash"


def test_tool_def():
    tool = ToolDef(name="bash", description="Run a command", parameters={"type": "object"})
    assert tool.name == "bash"
    assert tool.description == "Run a command"
