import pytest
from unittest.mock import MagicMock, patch


def _make_speaker():
    from tts.speaker import Speaker
    return Speaker()


def test_speak_calls_engine():
    with patch("tts.speaker.pyttsx3") as mock_pyttsx3:
        mock_engine = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine
        mock_engine.getProperty.return_value = [MagicMock(), MagicMock()]
        speaker = _make_speaker()
        speaker.speak("hello")
        mock_engine.say.assert_called_once_with("hello")
        mock_engine.runAndWait.assert_called_once()


def test_empty_string_does_not_call_engine():
    with patch("tts.speaker.pyttsx3") as mock_pyttsx3:
        mock_engine = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine
        speaker = _make_speaker()
        speaker.speak("")
        mock_engine.say.assert_not_called()


def test_whitespace_does_not_call_engine():
    with patch("tts.speaker.pyttsx3") as mock_pyttsx3:
        mock_engine = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine
        speaker = _make_speaker()
        speaker.speak("   ")
        mock_engine.say.assert_not_called()


def test_speak_strips_whitespace():
    with patch("tts.speaker.pyttsx3") as mock_pyttsx3:
        mock_engine = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine
        mock_engine.getProperty.return_value = [MagicMock(), MagicMock()]
        speaker = _make_speaker()
        speaker.speak("  hello world  ")
        mock_engine.say.assert_called_once_with("hello world")


def test_speak_does_not_raise_on_engine_failure():
    with patch("tts.speaker.pyttsx3") as mock_pyttsx3:
        mock_engine = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine
        mock_engine.getProperty.return_value = [MagicMock(), MagicMock()]
        mock_engine.say.side_effect = Exception("engine crashed")
        speaker = _make_speaker()
        speaker.speak("hello")  # should not raise