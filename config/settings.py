from dotenv import load_dotenv
import os

load_dotenv()

def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Required config '{key}' is missing from .env")
    return value

GEMINI_API_KEY = _require("GEMINI_API_KEY")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
WAKE_WORD = os.getenv("WAKE_WORD", "hey_jarvis")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")