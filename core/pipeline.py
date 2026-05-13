import logging
from stt.transcriber import Transcriber
from llm.gemini import GeminiLLM
from executor.base import Executor
from tts.speaker import Speaker
from core.state import SessionState

logger = logging.getLogger(__name__)

SPOKEN_RESULT_ACTIONS = {"tell_time", "take_note", "unknown"}


class Pipeline:
    def __init__(self):
        logger.info("Initializing pipeline...")
        self.transcriber = Transcriber()
        self.llm = GeminiLLM()
        self.executor = Executor()
        self.speaker = Speaker()
        self.state = SessionState()
        logger.info("Pipeline ready")


    def run_once(self, audio) -> None:
        transcript = self.transcriber.transcribe(audio)

        if not transcript.strip():
            logger.warning("Empty transcript, skipping")
            self.speaker.speak("I didn't catch that. Could you repeat?")
            return

        logger.info("Transcript: %s", transcript)

        plan = self.llm.parse_intent(transcript)
        logger.info("Action: %s | Params: %s", plan.action, plan.parameters)

        result = self.executor.run(plan)
        self.state.record(transcript, plan.action)

        if plan.action in SPOKEN_RESULT_ACTIONS:
            self.speaker.speak(result)
        else:
            self.speaker.speak(plan.speech_response)