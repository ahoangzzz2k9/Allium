"""Synthesizer agent implementation."""

from typing import Any

from .base_agent import BaseAgent
from .exceptions import AgentError


class SynthesizerAgent(BaseAgent):
    """Combine the initial plan and critique into a final plan."""

    def _build_prompt(self, **kwargs: Any) -> str:
        """Build the synthesis prompt."""
        return (
            "Bạn là Synthesizer Agent. Tổng hợp kế hoạch của Orchestrator và "
            "phản hồi của Critic để tạo plan cuối cùng. Xuất ra JSON đúng schema, "
            "bao gồm plan, confidence và decision.\n"
            f"Plan: {kwargs.get('plan', {})}\n"
            f"Critique: {kwargs.get('critique', {})}\n"
            f"Context: {kwargs.get('context', {})}"
        )

    def synthesize(
        self,
        plan: dict[str, Any],
        critique: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Synthesize and validate a final plan."""
        result = self.parse_output(
            self.call_llm(self._build_prompt(plan=plan, critique=critique, context=context))
        )
        required = {"plan", "confidence", "decision"}
        if not required.issubset(result):
            raise AgentError("Synthesizer response is missing required fields")
        if result["decision"] not in {"APPROVE", "REJECT"}:
            raise AgentError("Synthesizer decision must be APPROVE or REJECT")
        if not isinstance(result["confidence"], (int, float)) or not 0 <= result["confidence"] <= 1:
            raise AgentError("Synthesizer confidence must be between 0 and 1")
        return result
