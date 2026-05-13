import logging
from llm.base import ActionPlan
from executor.registry import ACTION_HANDLERS

logger = logging.getLogger(__name__)


class Executor:
    def run(self, plan: ActionPlan) -> str:
        handler = ACTION_HANDLERS.get(plan.action)
        if not handler:
            logger.error("No handler registered for action: %s", plan.action)
            return "I don't know how to do that yet."
        try:
            result = handler(plan.parameters)
            logger.info("Action '%s' executed: %s", plan.action, result)
            return result
        except Exception:
            logger.exception("Action '%s' failed", plan.action)
            return "Something went wrong while executing that."