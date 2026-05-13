import pytest
from unittest.mock import patch, MagicMock
from executor.base import Executor
from llm.base import ActionPlan


@pytest.fixture
def executor():
    return Executor()


def _plan(action, **params):
    return ActionPlan(action=action, parameters=params, speech_response="")


def test_unknown_action_returns_message(executor):
    plan = _plan("unknown", reason="test reason")
    result = executor.run(plan)
    assert isinstance(result, str)
    assert len(result) > 0


def test_unregistered_action_returns_fallback(executor):
    plan = ActionPlan(action="nonexistent", parameters={}, speech_response="")
    result = executor.run(plan)
    assert "don't know" in result.lower()


def test_tell_time_returns_string(executor):
    plan = _plan("tell_time")
    result = executor.run(plan)
    assert isinstance(result, str)
    assert len(result) > 0


def test_take_note_writes_file(executor, tmp_path):
    import executor.actions.notes as notes_module
    notes_module.NOTES_FILE = tmp_path / "test_notes.txt"
    plan = _plan("take_note", content="test note content")
    result = executor.run(plan)
    assert result == "Note saved."
    assert "test note content" in notes_module.NOTES_FILE.read_text()


def test_open_url_called(executor):
    with patch("executor.actions.browser.webbrowser.open") as mock_open:
        plan = _plan("open_url", url="https://youtube.com")
        result = executor.run(plan)
        mock_open.assert_called_once_with("https://youtube.com")


def test_search_web_encodes_query(executor):
    with patch("executor.actions.browser.webbrowser.open") as mock_open:
        plan = _plan("search_web", query="python tutorials")
        executor.run(plan)
        called_url = mock_open.call_args[0][0]
        assert "python+tutorials" in called_url or "python%20tutorials" in called_url


def test_open_application_does_not_raise(executor):
    with patch("executor.actions.system.subprocess.Popen") as mock_popen:
        plan = _plan("open_application", name="notepad")
        result = executor.run(plan)
        assert isinstance(result, str)


def test_executor_catches_handler_exception(executor):
    with patch("executor.actions.browser.webbrowser.open", side_effect=Exception("boom")):
        plan = _plan("open_url", url="https://youtube.com")
        result = executor.run(plan)
        assert "could not open" in result.lower()