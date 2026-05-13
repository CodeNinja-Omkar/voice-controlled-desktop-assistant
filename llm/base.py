from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ActionPlan:
    action: str
    parameters: dict
    speech_response: str


class BaseLLM(ABC):
    @abstractmethod
    def parse_intent(self, transcript: str) -> ActionPlan:
        """
        Takes a transcript string.
        Returns a structured ActionPlan.
        Must never raise — return unknown action on any failure.
        """
        pass