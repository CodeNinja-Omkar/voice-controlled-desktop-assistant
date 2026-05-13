import pytest
from unittest.mock import MagicMock, patch
from llm.gemini import GeminiLLM
from llm.base import ActionPlan


@pytest.fixture
def mock_gemini():
    with patch("llm.gemini.genai") as mock_genai:
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        llm = GeminiLLM()
        llm._client = mock_client
        yield llm, mock_client


def _set_response(mock_client, text):
    mock_response = MagicMock()
    mock_response.text = text
    mock_client.models.generate_content.return_value = mock_response


def test_valid_response_parsed(mock_gemini):
    llm, mock_client = mock_gemini
    _set_response(mock_client, '{"action": "open_url", "parameters": {"url": "https://youtube.com"}, "speech_response": "Opening YouTube."}')
    result = llm.parse_intent("open youtube")
    assert result.action == "open_url"
    assert result.parameters["url"] == "https://youtube.com"


def test_empty_transcript_returns_fallback(mock_gemini):
    llm, mock_client = mock_gemini
    result = llm.parse_intent("")
    assert result.action == "unknown"


def test_non_json_response_returns_fallback(mock_gemini):
    llm, mock_client = mock_gemini
    _set_response(mock_client, "sure I will open youtube for you")
    result = llm.parse_intent("open youtube")
    assert result.action == "unknown"


def test_markdown_fenced_json_parsed(mock_gemini):
    llm, mock_client = mock_gemini
    _set_response(mock_client, '```json\n{"action": "tell_time", "parameters": {}, "speech_response": "Checking time."}\n```')
    result = llm.parse_intent("what time is it")
    assert result.action == "tell_time"


def test_unregistered_action_returns_unknown(mock_gemini):
    llm, mock_client = mock_gemini
    _set_response(mock_client, '{"action": "launch_rocket", "parameters": {}, "speech_response": "Launching."}')
    result = llm.parse_intent("launch the rocket")
    assert result.action == "unknown"


def test_returns_action_plan_type(mock_gemini):
    llm, mock_client = mock_gemini
    _set_response(mock_client, '{"action": "tell_time", "parameters": {}, "speech_response": "Checking time."}')
    result = llm.parse_intent("what time is it")
    assert isinstance(result, ActionPlan)