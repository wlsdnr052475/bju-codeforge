"""Provider contracts and agent logic must work without Qt or an LLM server."""

import subprocess
import sys
import textwrap
from typing import cast

import pytest

from bju_codeforge.core.agent import ChatAgent
from bju_codeforge.providers.mock import MOCK_RESPONSE, MockProvider


class RecordingProvider:
    def __init__(self, response: object = "테스트 응답") -> None:
        self.response = response
        self.messages: list[str] = []

    def generate(self, message: str) -> str:
        self.messages.append(message)
        return cast(str, self.response)


def test_mock_returns_documented_fixed_response() -> None:
    provider = MockProvider()

    assert MOCK_RESPONSE.strip()
    assert provider.generate("안녕하세요") == MOCK_RESPONSE
    assert provider.generate("다른 메시지") == MOCK_RESPONSE


def test_agent_delivers_normalized_message_and_preserves_response() -> None:
    provider = RecordingProvider("  줄바꿈\n응답 <b>그대로</b>  ")
    agent = ChatAgent(provider)

    response = agent.send_message("  사용자 질문\n둘째 줄 \t")

    assert provider.messages == ["사용자 질문\n둘째 줄"]
    assert response == "  줄바꿈\n응답 <b>그대로</b>  "


@pytest.mark.parametrize("message", ["", " ", "\n\t\r"])
def test_blank_messages_do_not_reach_provider(message: str) -> None:
    provider = RecordingProvider()

    with pytest.raises(ValueError):
        ChatAgent(provider).send_message(message)

    assert provider.messages == []


@pytest.mark.parametrize("response", ["", " \n\t", None, 123])
def test_agent_rejects_invalid_provider_responses(response: object) -> None:
    provider = RecordingProvider(response)

    with pytest.raises(ValueError):
        ChatAgent(provider).send_message("메시지")

    assert provider.messages == ["메시지"]


def test_provider_exception_is_available_to_calling_layer() -> None:
    failure = RuntimeError("Provider unavailable")

    class FailingProvider:
        def generate(self, message: str) -> str:
            raise failure

    with pytest.raises(RuntimeError) as caught:
        ChatAgent(FailingProvider()).send_message("메시지")

    assert caught.value is failure


def test_core_runs_in_separate_python_process_with_qt_imports_blocked() -> None:
    script = textwrap.dedent(
        """
        import importlib.abc
        import sys

        class NoQt(importlib.abc.MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                if fullname == "PySide6" or fullname.startswith("PySide6."):
                    raise ImportError("Qt is forbidden in the core layer")
                return None

        sys.meta_path.insert(0, NoQt())
        from bju_codeforge.core.agent import ChatAgent
        from bju_codeforge.providers.mock import MOCK_RESPONSE, MockProvider

        assert ChatAgent(MockProvider()).send_message("독립 실행") == MOCK_RESPONSE
        assert not any(name.startswith("PySide6") for name in sys.modules)
        print("core-without-qt-ok")
        """
    )

    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "core-without-qt-ok"
