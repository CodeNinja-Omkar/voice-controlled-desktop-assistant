import json
import logging
from google import genai
from google.genai import types
from llm.base import BaseLLM, ActionPlan
from llm.prompts import SYSTEM_PROMPT
from config.settings import GEMINI_API_KEY

logger = logging.getLogger(__name__)

_FALLBACK_PLAN = ActionPlan(
    action="unknown",
    parameters={"reason": "llm parse failure"},
    speech_response="Sorry, I did not understand that.",
)


class GeminiLLM(BaseLLM):
    def __init__(self):
        self._client = genai.Client(api_key=GEMINI_API_KEY)
        self._config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1,
            max_output_tokens=512,
        )
        logger.info("Gemini LLM initialized")

    def parse_intent(self, transcript: str) -> ActionPlan:
        if not transcript.strip():
            logger.warning("Empty transcript passed to LLM")
            return _FALLBACK_PLAN

        try:
            response = self._client.models.generate_content(
                model="gemini-2.5-flash",
                contents=transcript,
                config=self._config,
            )
            raw = response.text.strip()
            logger.debug("Raw LLM response: %s", raw)

            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1]
                raw = raw.rsplit("```", 1)[0].strip()

            data = json.loads(raw)
            return self._validate(data)

        except json.JSONDecodeError:
            logger.error("LLM returned non-JSON response: %s", raw)
            return _FALLBACK_PLAN
        except Exception:
            logger.exception("LLM call failed")
            return _FALLBACK_PLAN

    def _validate(self, data: dict) -> ActionPlan:
        from executor.registry import SUPPORTED_ACTIONS

        action = data.get("action", "unknown")
        parameters = data.get("parameters", {})
        speech_response = data.get("speech_response", "Done.")

        if not isinstance(action, str) or action not in SUPPORTED_ACTIONS:
            logger.warning("LLM returned unregistered action: %s", action)
            action = "unknown"
            parameters = {"reason": f"unregistered action: {action}"}

        if not isinstance(parameters, dict):
            parameters = {}

        if not isinstance(speech_response, str):
            speech_response = "Done."

        return ActionPlan(
            action=action,
            parameters=parameters,
            speech_response=speech_response,
        )