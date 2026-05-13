import numpy as np
import pytest
from unittest.mock import MagicMock, patch, call


@pytest.fixture
def mock_detector():
    with patch("wake_word.detector.Model") as mock_model_cls, \
         patch("wake_word.detector.sd") as mock_sd:

        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model

        mock_stream = MagicMock()
        mock_sd.InputStream.return_value.__enter__.return_value = mock_stream

        from wake_word.detector import WakeWordDetector
        detector = WakeWordDetector()
        yield detector, mock_model, mock_stream


def test_initializes_without_error(mock_detector):
    detector, _, _ = mock_detector
    assert detector is not None


def test_returns_true_on_detection(mock_detector):
    detector, mock_model, mock_stream = mock_detector
    mock_stream.read.return_value = (
        np.zeros(1280, dtype="int16").reshape(-1, 1), None
    )
    # first call below threshold, second call above
    mock_model.predict.side_effect = [
        {"hey_jarvis": 0.1},
        {"hey_jarvis": 0.9},
    ]
    result = detector.listen_for_wake_word()
    assert result is True


def test_stays_listening_below_threshold(mock_detector):
    detector, mock_model, mock_stream = mock_detector
    mock_stream.read.return_value = (
        np.zeros(1280, dtype="int16").reshape(-1, 1), None
    )
    # 4 calls below threshold, 5th triggers
    mock_model.predict.side_effect = [
        {"hey_jarvis": 0.1},
        {"hey_jarvis": 0.2},
        {"hey_jarvis": 0.0},
        {"hey_jarvis": 0.3},
        {"hey_jarvis": 0.8},
    ]
    result = detector.listen_for_wake_word()
    assert result is True
    assert mock_model.predict.call_count == 5


def test_threshold_boundary(mock_detector):
    detector, mock_model, mock_stream = mock_detector
    mock_stream.read.return_value = (
        np.zeros(1280, dtype="int16").reshape(-1, 1), None
    )
    # exactly at threshold should not trigger, just above should
    mock_model.predict.side_effect = [
        {"hey_jarvis": 0.5},   # equal — should not trigger per > check
        {"hey_jarvis": 0.51},
    ]
    result = detector.listen_for_wake_word()
    assert result is True
    assert mock_model.predict.call_count == 2

    
def test_reset_clears_prediction_buffer(mock_detector):
    detector, mock_model, _ = mock_detector
    mock_model.prediction_buffer = {"hey_jarvis": [0.9, 0.8, 0.7]}
    detector.reset()
    assert len(mock_model.prediction_buffer["hey_jarvis"]) == 0