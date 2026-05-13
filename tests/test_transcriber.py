import numpy as np
import pytest
from stt.transcriber import Transcriber


@pytest.fixture(scope="module")
def transcriber():
    return Transcriber()


def test_loads_without_error(transcriber):
    assert transcriber is not None


def test_transcribe_silence_returns_string(transcriber):
    silent_audio = np.zeros(16000, dtype=np.float32)
    result = transcriber.transcribe(silent_audio)
    assert isinstance(result, str)


def test_transcribe_converts_dtype(transcriber):
    int_audio = np.zeros(16000, dtype=np.int16)
    result = transcriber.transcribe(int_audio)
    assert isinstance(result, str)


def test_wrong_sample_rate_raises(transcriber):
    audio = np.zeros(8000, dtype=np.float32)
    with pytest.raises(ValueError):
        transcriber.transcribe(audio, sample_rate=8000)