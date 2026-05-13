import whisper
import numpy as np
from config.settings import WHISPER_MODEL
import logging

logger = logging.getLogger(__name__)


class Transcriber:
    def __init__(self):
        logger.debug("Loading Whisper model: %s", WHISPER_MODEL)
        self._model = whisper.load_model(WHISPER_MODEL)
        logger.info("Whisper model loaded")

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> str:
        """
        Accepts raw float32 numpy array at 16kHz mono.
        Returns stripped transcript string, empty string on failure.
        """
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        if audio.ndim > 1:
            audio = audio.mean(axis=1)

        if sample_rate != 16000:
            raise ValueError(
                f"Whisper requires 16000Hz audio, got {sample_rate}Hz"
            )

        try:
            result = self._model.transcribe(
                audio,
                language="en",
                fp16=False,  # CPU only, fp16 will warn and fallback anyway
                verbose=False,
            )
            transcript = result["text"].strip()
            logger.debug("Transcript: %s", transcript)
            return transcript
        except Exception:
            logger.exception("Transcription failed")
            return ""