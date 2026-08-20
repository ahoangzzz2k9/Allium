"""Abstract LLM provider contract."""

from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """Provide a common interface for local language-model backends."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> str:
        """Generate a text response for ``prompt``."""
        raise NotImplementedError
