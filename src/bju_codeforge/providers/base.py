"""The small contract implemented by inference providers."""

from typing import Protocol


class LLMProvider(Protocol):
    """Generate plain text from a user message.

    Implementations may raise exceptions on failure. Future network providers
    must use bounded timeouts so a request can finish safely during app shutdown.
    """

    def generate(self, message: str) -> str:
        """Return a nonempty response without executing commands or tools."""
        ...
