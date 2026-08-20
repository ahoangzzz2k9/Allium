"""Deterministic LLM provider used by unit tests."""

import json
from typing import Mapping, Optional

from .base import LLMProvider


class MockLLMProvider(LLMProvider):
    """Return deterministic JSON responses without contacting a model."""

    def __init__(self, responses: Optional[Mapping[str, object]] = None) -> None:
        """Initialize the provider with optional keyword-to-response mappings."""
        self.responses = dict(responses or {})
        self.calls: list[tuple[str, Optional[str], Optional[int]]] = []

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> str:
        """Return a JSON response selected from the prompt keywords."""
        self.calls.append((prompt, model, timeout))
        prompt_lower = prompt.lower()
        for keyword, response in self.responses.items():
            if keyword.lower() in prompt_lower:
                return response if isinstance(response, str) else json.dumps(response)
        return json.dumps(
            {
                "plan": [{"action": "noop", "params": {}}],
                "decision": "APPROVE",
                "confidence": 0.9,
                "rationale": "Deterministic mock response",
            }
        )
