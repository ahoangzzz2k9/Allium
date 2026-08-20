"""Critic agent implementation."""

from typing import Any

from .base_agent import BaseAgent
from .exceptions import AgentError


class CriticAgent(BaseAgent):
    """Evaluate an initial plan for safety, risks, and feasibility."""

    def _build_prompt(self, **kwargs: Any) -> str:
        """Build the critique prompt from a plan and context."""
        return (
            "Bạn là Critic Agent. Đánh giá kế hoạch sau: "
            f"{kwargs.get('plan', {})}. Tìm lỗ hổng, rủi ro, khả năng thất bại. "
            "Trả về decision (APPROVE/REJECT), confidence (0-1), risks, suggestions.\n"
            f"Context: {kwargs.get('context', {})}"
        )

    def critique(self, plan: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Critique a plan and validate the required response fields."""
        result = self.parse_output(self.call_llm(self._build_prompt(plan=plan, context=context)))
        required = {"decision", "confidence", "risks", "suggestions"}
        if not required.issubset(result):
            raise AgentError("Critic response is missing required fields")
        if result["decision"] not in {"APPROVE", "REJECT"}:
            raise AgentError("Critic decision must be APPROVE or REJECT")
        if not isinstance(result["confidence"], (int, float)) or not 0 <= result["confidence"] <= 1:
            raise AgentError("Critic confidence must be between 0 and 1")
        return result
