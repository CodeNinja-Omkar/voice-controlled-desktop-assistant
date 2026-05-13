import pyttsx3
import logging

logger = logging.getLogger(__name__)


class Speaker:
    def speak(self, text: str) -> None:
        if not text or not text.strip():
            logger.warning("speak() called with empty text")
            return
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            if len(voices) > 1:
                engine.setProperty("voice", voices[1].id)
            engine.setProperty("rate", 175)
            engine.setProperty("volume", 0.9)
            engine.say(text.strip())
            engine.runAndWait()
            engine.stop()
            del engine
        except Exception:
            logger.exception("TTS failed for text: %s", text)