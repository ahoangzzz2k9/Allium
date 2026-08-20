"""Unit tests for Task 0.1 multi-agent swarm framework."""

from unittest.mock import patch

import pytest

from src.llm.mock_provider import MockLLMProvider
from src.swarm.critic_agent import CriticAgent
from src.swarm.exceptions import SwarmError
from src.swarm.orchestrator_agent import OrchestratorAgent
from src.swarm.swarm_manager import SwarmManager
from src.swarm.synthesizer_agent import SynthesizerAgent


PLAN = {"plan": [{"action": "open_app", "params": {"app": "notepad"}}], "decision": "APPROVE", "confidence": 0.9, "rationale": "safe"}
CRITIQUE = {"decision": "APPROVE", "confidence": 0.9, "risks": [], "suggestions": []}
SYNTHESIS = {"plan": PLAN["plan"], "decision": "APPROVE", "confidence": 0.9}


def build_agents(provider: MockLLMProvider) -> tuple[OrchestratorAgent, CriticAgent, SynthesizerAgent]:
    """Build all three agents from the same mock provider."""
    return (
        OrchestratorAgent(provider, "mock-orchestrator", 50),
        CriticAgent(provider, "mock-critic", 25),
        SynthesizerAgent(provider, "mock-synthesizer", 25),
    )


def test_orchestrator_agent_returns_plan() -> None:
    """OrchestratorAgent parses a valid plan response."""
    provider = MockLLMProvider({"Orchestrator Agent": PLAN})
    agent, _, _ = build_agents(provider)

    result = agent.generate_plan("open Notepad", {})

    assert result == PLAN
    assert len(provider.calls) == 1


def test_critic_agent_returns_critique() -> None:
    """CriticAgent parses a valid critique response."""
    provider = MockLLMProvider({"Critic Agent": CRITIQUE})
    _, agent, _ = build_agents(provider)

    result = agent.critique(PLAN, {})

    assert result == CRITIQUE


def test_synthesizer_agent_returns_final_plan() -> None:
    """SynthesizerAgent parses a valid synthesis response."""
    provider = MockLLMProvider({"Synthesizer Agent": SYNTHESIS})
    _, _, agent = build_agents(provider)

    result = agent.synthesize(PLAN, CRITIQUE, {})

    assert result == SYNTHESIS


def test_swarm_manager_succeeds_when_consensus_is_reached() -> None:
    """SwarmManager accepts two-of-three approval with sufficient confidence."""
    provider = MockLLMProvider(
        {
            "Orchestrator Agent": PLAN,
            "Critic Agent": CRITIQUE,
            "Synthesizer Agent": SYNTHESIS,
        }
    )
    orchestrator, critic, synthesizer = build_agents(provider)
    manager = SwarmManager(orchestrator, critic, synthesizer)

    result = manager.process("open Notepad", {})

    assert result == SYNTHESIS
    assert len(provider.calls) == 3


def test_swarm_manager_retries_and_then_succeeds() -> None:
    """A low-confidence critique causes one retry before consensus succeeds."""
    low = {"decision": "REJECT", "confidence": 0.4, "risks": ["risk"], "suggestions": ["fix"]}
    provider = MockLLMProvider(
        {
            "Orchestrator Agent": [PLAN, PLAN],
            "Critic Agent": [low, CRITIQUE],
            "Synthesizer Agent": SYNTHESIS,
        }
    )
    orchestrator, critic, synthesizer = build_agents(provider)
    manager = SwarmManager(orchestrator, critic, synthesizer)

    result = manager.process("open Notepad", {})

    assert result == SYNTHESIS
    assert len(provider.calls) == 5


def test_swarm_manager_fails_after_retry_budget() -> None:
    """Repeated low-confidence critiques exhaust the retry budget."""
    low = {"decision": "REJECT", "confidence": 0.4, "risks": ["risk"], "suggestions": ["fix"]}
    provider = MockLLMProvider(
        {
            "Orchestrator Agent": PLAN,
            "Critic Agent": [low, low, low],
        }
    )
    orchestrator, critic, synthesizer = build_agents(provider)
    manager = SwarmManager(orchestrator, critic, synthesizer, max_retries=2)

    with pytest.raises(SwarmError, match="CONSENSUS_FAILED"):
        manager.process("open Notepad", {})

    assert len(provider.calls) == 6


def test_swarm_manager_timeout() -> None:
    """The manager stops when its total deadline expires."""
    provider = MockLLMProvider({"Orchestrator Agent": PLAN})
    orchestrator, critic, synthesizer = build_agents(provider)
    manager = SwarmManager(orchestrator, critic, synthesizer, timeout=100)

    with patch("src.swarm.swarm_manager.time.monotonic", side_effect=[0.0, 0.0, 101.0]):
        with pytest.raises(SwarmError, match="TIMEOUT"):
            manager.process("open Notepad", {})


def test_unit_tests_never_invoke_ollama() -> None:
    """The test suite's provider is the local mock provider only."""
    provider = MockLLMProvider({"Orchestrator Agent": PLAN})
    agent, _, _ = build_agents(provider)

    with patch("src.llm.ollama_provider.subprocess.run") as ollama_run:
        agent.generate_plan("open Notepad", {})
        ollama_run.assert_not_called()
