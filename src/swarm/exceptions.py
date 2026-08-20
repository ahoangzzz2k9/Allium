"""Exceptions raised by the swarm framework."""


class AgentError(RuntimeError):
    """Raised when an agent cannot obtain or parse a valid response."""


class SwarmError(RuntimeError):
    """Raised when swarm processing cannot produce an accepted result."""
