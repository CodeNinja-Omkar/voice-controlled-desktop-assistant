import time
import logging
from config.settings import LOG_LEVEL
from audio.recorder import record_until_silence
from core.pipeline import Pipeline
from wake_word.detector import WakeWordDetector

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    pipeline = Pipeline()
    detector = WakeWordDetector()

    print("\nJARVIS ready. Say 'Hey Jarvis' to activate. Ctrl+C to exit.\n")

    while True:
        try:
            detector.listen_for_wake_word()
            pipeline.speaker.speak("Yes?")

            print("Listening...")
            audio = record_until_silence()
            print("Processing...")
            pipeline.run_once(audio)

            # wait for TTS response to finish and microphone to settle
            # before resetting and re-entering wake word detection
            time.sleep(1.5)
            detector.reset()

        except KeyboardInterrupt:
            print("\nShutting down.")
            break
        except Exception:
            logger.exception("Unexpected error in main loop")


if __name__ == "__main__":
    main()