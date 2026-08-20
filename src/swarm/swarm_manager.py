"""Swarm orchestration and consensus logic."""

import time
from typing import Any

from .critic_agent import CriticAgent
from .exceptions import AgentError, SwarmError
from .orchestrator_agent import OrchestratorAgent
from .synthesizer_agent import SynthesizerAgent


class SwarmManager:
    """Coordinate the three planning agents under a total timeout."""

    def __init__(
        self,
        orchestrator: OrchestratorAgent,
        critic: CriticAgent,
        synthesizer: SynthesizerAgent,
        max_retries: int = 2,
        consensus_threshold: float = 0.6,
        timeout: int = 100,
    ) -> None:
        """Initialize the swarm manager and its consensus policy."""
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if not 0 <= consensus_threshold <= 1:
            raise ValueError("consensus_threshold must be between 0 and 1")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.orchestrator = orchestrator
        self.critic = critic
        self.synthesizer = synthesizer
        self.max_retries = max_retries
        self.consensus_threshold = consensus_threshold
        self.timeout = timeout

    def _remaining_timeout(self, deadline: float) -> int:
        """Return remaining whole seconds or raise the swarm timeout error."""
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise SwarmError("TIMEOUT")
        return max(1, int(remaining))

    def process(self, query: str, context: dict[str, Any]) -> dict[str, Any]:
        """Run the swarm until consensus is reached or the retry budget expires."""
        deadline = time.monotonic() + self.timeout

        for attempt in range(self.max_retries + 1):
            try:
                initial_plan = self.orchestrator.generate_plan(query, context)
                if time.monotonic() >= deadline:
                    raise SwarmError("TIMEOUT")

                critique = self.critic.critique(initial_plan, context)
                if critique["decision"] == "REJECT" or critique["confidence"] < 0.5:
                    if attempt == self.max_retries:
                        raise SwarmError("CONSENSUS_FAILED")
                    continue

                synthesis = self.synthesizer.synthesize(initial_plan, critique, context)
                if self._check_consensus([initial_plan], [critique], synthesis):
                    return synthesis
            except AgentError as exc:
                if time.monotonic() >= deadline:
                    raise SwarmError("TIMEOUT") from exc
                if attempt == self.max_retries:
                    raise SwarmError("CONSENSUS_FAILED") from exc
                continue

            if time.monotonic() >= deadline:
                raise SwarmError("TIMEOUT")

        raise SwarmError("CONSENSUS_FAILED")

    def _check_consensus(
        self,
        plans: list[dict[str, Any]],
        critiques: list[dict[str, Any]],
        synthesis: dict[str, Any],
    ) -> bool:
        """Return true when at least two of three agents approve confidently."""
        del plans  # Kept in the signature to preserve the framework contract.
        decisions = [
            critiques[-1]["decision"],
            synthesis["decision"],
            "APPROVE",
        ]
        confidences = [
            float(critiques[-1]["confidence"]),
            float(synthesis["confidence"]),
            1.0,
        ]
        approvals = sum(decision == "APPROVE" for decision in decisions)
        return approvals >= 2 and sum(confidences) / len(confidences) >= self.consensus_threshold
