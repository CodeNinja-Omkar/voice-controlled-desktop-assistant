import logging
import numpy as np
import sounddevice as sd
from openwakeword.model import Model

logger = logging.getLogger(__name__)

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280
ACTIVATION_THRESHOLD = 0.5


class WakeWordDetector:
    def __init__(self):
        self._model = Model(
            inference_framework="onnx",
            wakeword_models=["hey_jarvis"],
        )
        logger.info("Wake word detector initialized")

    def reset(self) -> None:
        """
        Clears model prediction buffer.
        Must be called after each activation before re-entering detection loop
        to prevent TTS audio from triggering a false positive.
        """
        for model_name in self._model.prediction_buffer:
            self._model.prediction_buffer[model_name].clear()

    def listen_for_wake_word(self) -> bool:
        logger.debug("Listening for wake word...")

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=CHUNK_SIZE,
        ) as stream:
            while True:
                chunk, _ = stream.read(CHUNK_SIZE)
                chunk = chunk.flatten()
                prediction = self._model.predict(chunk)

                scores = list(prediction.values())
                if any(score > ACTIVATION_THRESHOLD for score in scores):
                    logger.info("Wake word detected")
                    return True