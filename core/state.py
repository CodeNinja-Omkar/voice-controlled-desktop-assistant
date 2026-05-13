from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SessionState:
    started_at: datetime = field(default_factory=datetime.now)
    commands_processed: int = 0
    last_transcript: str = ""
    last_action: str = ""

    def record(self, transcript: str, action: str) -> None:
        self.commands_processed += 1
        self.last_transcript = transcript
        self.last_action = action