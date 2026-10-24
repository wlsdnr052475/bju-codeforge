"""Deterministic local provider for MVP 1; no model or network is used."""

MOCK_RESPONSE = (
    "안녕하세요! BJU CodeForge Mock AI입니다. 메시지를 정상적으로 받았습니다. "
    "현재는 테스트 모드이며 실제 AI 모델은 연결되어 있지 않습니다."
)


class MockProvider:
    """Return the same test response for every message."""

    def generate(self, message: str) -> str:
        """Satisfy the provider contract without performing inference."""
        return MOCK_RESPONSE
