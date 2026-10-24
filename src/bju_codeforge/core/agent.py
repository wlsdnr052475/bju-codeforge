"""Minimal chat orchestration independent of Qt and inference engines."""

from bju_codeforge.providers.base import LLMProvider


class ChatAgent:
    """Validate a message and delegate inference to an injected provider.

    This synchronous service runs without a GUI. GUI callers must invoke it from
    a worker thread. It treats all messages as data and provides no tool access.
    """

    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    def send_message(self, message: str) -> str:
        """Return a nonempty provider response; propagate provider failures."""
        normalized = message.strip()
        if not normalized:
            raise ValueError("메시지를 입력해 주세요.")

        response = self._provider.generate(normalized)
        if not isinstance(response, str) or not response.strip():
            raise ValueError("AI Provider가 유효한 응답을 반환하지 않았습니다.")
        return response
