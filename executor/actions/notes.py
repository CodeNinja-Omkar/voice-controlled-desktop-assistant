import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

NOTES_FILE = Path.home() / "jarvis_notes.txt"


def take_note(content: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"[{timestamp}] {content.strip()}\n"
    try:
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
        return "Note saved."
    except Exception as e:
        logger.error("Failed to save note: %s", e)
        return "Could not save the note."