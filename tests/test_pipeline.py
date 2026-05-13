import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from llm.base import ActionPlan


@pytest.fixture
def pipeline():
    with patch("core.pipeline.Transcriber") as mock_stt, \
         patch("core.pipeline.GeminiLLM") as mock_llm, \
         patch("core.pipeline.Executor") as mock_executor, \
         patch("core.pipeline.Speaker") as mock_speaker:

        mock_stt.return_value.transcribe.return_value = "open youtube"
        mock_llm.return_value.parse_intent.return_value = ActionPlan(
            action="open_url",
            parameters={"url": "https://youtube.com"},
            speech_response="Opening YouTube.",
        )
        mock_executor.return_value.run.return_value = "Opened."
        mock_speaker.return_value.speak.return_value = None

        from core.pipeline import Pipeline
        p = Pipeline()
        yield p, mock_stt, mock_llm, mock_executor, mock_speaker


def _silent_audio():
    return np.zeros(16000, dtype=np.float32)


def test_full_pipeline_runs(pipeline):
    p, *_ = pipeline
    p.run_once(_silent_audio())  # should not raise


def test_transcript_passed_to_llm(pipeline):
    p, mock_stt, mock_llm, *_ = pipeline
    p.run_once(_silent_audio())
    mock_llm.return_value.parse_intent.assert_called_once_with("open youtube")


def test_plan_passed_to_executor(pipeline):
    p, _, mock_llm, mock_executor, _ = pipeline
    p.run_once(_silent_audio())
    plan = mock_llm.return_value.parse_intent.return_value
    mock_executor.return_value.run.assert_called_once_with(plan)


def test_speech_response_spoken(pipeline):
    p, _, mock_llm, _, mock_speaker = pipeline
    p.run_once(_silent_audio())
    mock_speaker.return_value.speak.assert_called_once_with("Opening YouTube.")


def test_empty_transcript_speaks_fallback(pipeline):
    p, mock_stt, mock_llm, mock_executor, mock_speaker = pipeline
    mock_stt.return_value.transcribe.return_value = ""
    p.run_once(_silent_audio())
    mock_llm.return_value.parse_intent.assert_not_called()
    mock_executor.return_value.run.assert_not_called()
    mock_speaker.return_value.speak.assert_called_once()


def test_state_updated_after_command(pipeline):
    p, *_ = pipeline
    p.run_once(_silent_audio())
    assert p.state.commands_processed == 1
    assert p.state.last_transcript == "open youtube"
    assert p.state.last_action == "open_url"

def test_tell_time_speaks_executor_result(pipeline):
    p, mock_stt, mock_llm, mock_executor, mock_speaker = pipeline
    mock_stt.return_value.transcribe.return_value = "what time is it"
    mock_llm.return_value.parse_intent.return_value = ActionPlan(
        action="tell_time",
        parameters={},
        speech_response="Let me check the time.",
    )
    mock_executor.return_value.run.return_value = "It's 03:45 PM on Wednesday, May 13."
    p.run_once(np.zeros(16000, dtype=np.float32))
    mock_speaker.return_value.speak.assert_called_once_with(
        "It's 03:45 PM on Wednesday, May 13."
    )