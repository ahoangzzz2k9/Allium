"""Orchestrator agent implementation."""

from typing import Any

from .base_agent import BaseAgent


class OrchestratorAgent(BaseAgent):
    """Propose an initial action plan for a user request."""

    def _build_prompt(self, **kwargs: Any) -> str:
        """Build the planning prompt from query and context."""
        return (
            "Bạn là Orchestrator Agent. Nhiệm vụ: đề xuất kế hoạch hành động "
            "dựa trên yêu cầu của người dùng và ngữ cảnh. Trả về JSON với "
            "plan (list actions), decision (mặc định là APPROVE), confidence "
            "(0-1) và rationale.\n"
            f"User query: {kwargs.get('query', '')}\n"
            f"Context: {kwargs.get('context', {})}"
        )

    def generate_plan(self, query: str, context: dict[str, Any]) -> dict[str, Any]:
        """Generate and validate an initial plan."""
        result = self.parse_output(self.call_llm(self._build_prompt(query=query, context=context)))
        required = {"plan", "decision", "confidence", "rationale"}
        if not required.issubset(result):
            raise ValueError("Orchestrator response is missing required fields")
        if result["decision"] != "APPROVE":
            raise ValueError("Orchestrator decision must be APPROVE")
        if not isinstance(result["confidence"], (int, float)) or not 0 <= result["confidence"] <= 1:
            raise ValueError("Orchestrator confidence must be between 0 and 1")
        return result
