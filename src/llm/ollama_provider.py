"""Ollama CLI backed LLM provider."""

import subprocess
from typing import Optional

from .base import LLMProvider


class OllamaProvider(LLMProvider):
    """Call the local Ollama CLI without making network requests directly."""

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> str:
        """Generate text using ``ollama run`` and return stdout."""
        if not model:
            raise ValueError("model is required for OllamaProvider")

        try:
            result = subprocess.run(
                ["ollama", "run", model, prompt],
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError("Ollama request timed out") from exc
        except OSError as exc:
            raise RuntimeError("Unable to execute Ollama CLI") from exc

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Ollama CLI failed")
        return result.stdout.strip()
