"""Base class shared by all swarm agents."""

import json
from abc import ABC, abstractmethod
from typing import Any, Optional

from src.llm.base import LLMProvider

from .exceptions import AgentError


class BaseAgent(ABC):
    """Provide common LLM invocation and JSON parsing behavior."""

    def __init__(self, llm_provider: LLMProvider, model_name: str, timeout: int) -> None:
        """Initialize an agent with its injected provider and timeout."""
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.timeout = timeout

    def call_llm(self, prompt: str, timeout: Optional[int] = None) -> str:
        """Call the injected provider using the configured model and timeout."""
        effective_timeout = self.timeout if timeout is None else timeout
        try:
            return self.llm_provider.generate(
                prompt,
                model=self.model_name,
                timeout=effective_timeout,
            )
        except (TimeoutError, RuntimeError, ValueError) as exc:
            raise AgentError(f"LLM call failed: {exc}") from exc

    def parse_output(self, text: str) -> dict[str, Any]:
        """Parse a JSON object returned by the LLM."""
        try:
            value = json.loads(text)
        except json.JSONDecodeError as exc:
            raise AgentError("LLM returned invalid JSON") from exc
        if not isinstance(value, dict):
            raise AgentError("LLM output must be a JSON object")
        return value

    @abstractmethod
    def _build_prompt(self, **kwargs: Any) -> str:
        """Build the agent-specific prompt."""
        raise NotImplementedError
