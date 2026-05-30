"""Base Agent — all V4 agents extend this."""

import json
import logging
import re

from app.llm.client import LLMClient

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all V4 agents. Reuses existing LLMClient."""

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm = llm_client or LLMClient()

    async def think(self, state: dict) -> dict:
        """Agent reasoning — receives workflow state, returns state update dict."""
        raise NotImplementedError

    async def _call_llm(self, system_prompt: str, user_prompt: str, model: str = "deepseek/deepseek-v4-pro") -> str:
        """Call LLM and return response text."""
        return await self.llm.complete(system_prompt, user_prompt, model)

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Extract JSON object from LLM response."""
        try:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except (json.JSONDecodeError, AttributeError):
            pass
        # Try parsing the whole thing
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _parse_json_array(text: str) -> list:
        """Extract JSON array from LLM response."""
        try:
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except (json.JSONDecodeError, AttributeError):
            pass
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return []
