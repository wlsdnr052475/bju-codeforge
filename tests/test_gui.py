"""Exercise real Qt widgets and asynchronous work in an offscreen event loop."""

from collections.abc import Callable, Iterator
from threading import Event, get_ident

import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from bju_codeforge.core.agent import ChatAgent
from bju_codeforge.gui.main_window import MainWindow
from bju_codeforge.providers.base import LLMProvider
from bju_codeforge.providers.mock import MOCK_RESPONSE, MockProvider


class ControlledProvider:
    """Hold a request until a test releases it, without blocking the Qt thread."""

    def __init__(self, *, fail_first: bool = False) -> None:
        self.started = Event()
        self.release = Event()
        self.messages: list[str] = []
        self.thread_id: int | None = None
        self.fail_first = fail_first

    def generate(self, message: str) -> str:
        self.thread_id = get_ident()
        self.messages.append(message)
        self.started.set()
        if not self.release.wait(timeout=5):
            raise TimeoutError("Test did not release the controlled provider")
        if self.fail_first and len(self.messages) == 1:
            raise RuntimeError("테스트 연결 실패 <b>일반 텍스트</b>")
        return "응답 <b>실행하지 않음</b>\n두 번째 줄"


@pytest.fixture
def make_window(
    qapp: QApplication, wait_until: Callable[[Callable[[], bool]], None]
) -> Iterator[Callable[[LLMProvider], MainWindow]]:
    windows: list[tuple[MainWindow, LLMProvider]] = []

    def make(provider: LLMProvider) -> MainWindow:
        window = MainWindow(ChatAgent(provider))
        windows.append((window, provider))
        window.show()
        qapp.processEvents()
        return window

    yield make

    for window, provider in windows:
        if isinstance(provider, ControlledProvider):
            provider.release.set()
        wait_until(lambda window=window: not window.is_busy)
        window.close()
        window.deleteLater()
    qapp.processEvents()


def test_basic_widgets_are_created(make_window: Callable[[LLMProvider], MainWindow]) -> None:
    window = make_window(MockProvider())

    assert "BJU CodeForge" in window.windowTitle()
    assert window.user_messages.isReadOnly()
    assert window.ai_responses.isReadOnly()
    assert window.message_input.isEnabled()
    assert not window.send_button.isEnabled()
    assert not window.is_busy
    assert window.user_messages.toPlainText() == ""
    assert window.ai_responses.toPlainText() == ""


@pytest.mark.parametrize("use_enter", [False, True], ids=["button", "enter"])
def test_message_submission_and_mock_response(
    make_window: Callable[[LLMProvider], MainWindow],
    wait_until: Callable[[Callable[[], bool]], None],
    use_enter: bool,
) -> None:
    window = make_window(MockProvider())
    window.message_input.setText("  안녕하세요 <b>사용자 입력</b>  ")

    if use_enter:
        QTest.keyClick(window.message_input, Qt.Key.Key_Return)
    else:
        QTest.mouseClick(window.send_button, Qt.MouseButton.LeftButton)
    wait_until(lambda: not window.is_busy and MOCK_RESPONSE in window.ai_responses.toPlainText())

    assert "안녕하세요 <b>사용자 입력</b>" in window.user_messages.toPlainText()
    assert window.message_input.text() == ""
    assert window.message_input.isEnabled()


def test_blank_input_is_not_submitted(make_window: Callable[[LLMProvider], MainWindow]) -> None:
    provider = ControlledProvider()
    window = make_window(provider)
    window.message_input.setText("   \t  ")

    assert not window.send_button.isEnabled()
    QTest.keyClick(window.message_input, Qt.Key.Key_Return)

    assert not window.is_busy
    assert provider.messages == []
    assert window.user_messages.toPlainText() == ""


def test_long_request_preserves_responsiveness_and_prevents_duplicate_submission(
    make_window: Callable[[LLMProvider], MainWindow],
    wait_until: Callable[[Callable[[], bool]], None],
) -> None:
    provider = ControlledProvider()
    window = make_window(provider)
    window.message_input.setText("작업 하나")
    QTest.mouseClick(window.send_button, Qt.MouseButton.LeftButton)
    wait_until(provider.started.is_set)

    assert window.is_busy
    assert not window.send_button.isEnabled()
    assert not window.message_input.isEnabled()
    assert provider.thread_id != get_ident()
    QTest.mouseClick(window.send_button, Qt.MouseButton.LeftButton)
    timer_fired = Event()
    QTimer.singleShot(0, timer_fired.set)
    wait_until(timer_fired.is_set)
    assert window.is_busy
    assert provider.messages == ["작업 하나"]

    provider.release.set()
    wait_until(lambda: not window.is_busy)

    assert "응답 <b>실행하지 않음</b>\n두 번째 줄" in window.ai_responses.toPlainText()
    assert window.message_input.isEnabled()


def test_provider_error_allows_retry(
    make_window: Callable[[LLMProvider], MainWindow],
    wait_until: Callable[[Callable[[], bool]], None],
) -> None:
    provider = ControlledProvider(fail_first=True)
    provider.release.set()
    window = make_window(provider)
    window.message_input.setText("첫 요청")
    QTest.mouseClick(window.send_button, Qt.MouseButton.LeftButton)
    wait_until(lambda: not window.is_busy)

    assert "테스트 연결 실패" in window.status_label.text()
    assert window.ai_responses.toPlainText() == ""
    assert window.message_input.isEnabled()

    window.message_input.setText("재시도")
    QTest.mouseClick(window.send_button, Qt.MouseButton.LeftButton)
    wait_until(lambda: not window.is_busy)

    assert provider.messages == ["첫 요청", "재시도"]
    assert "응답 <b>실행하지 않음</b>" in window.ai_responses.toPlainText()
    assert "테스트 연결 실패" not in window.status_label.text()


def test_close_during_request_waits_for_worker_without_blocking_gui(
    make_window: Callable[[LLMProvider], MainWindow],
    wait_until: Callable[[Callable[[], bool]], None],
) -> None:
    provider = ControlledProvider()
    window = make_window(provider)
    window.message_input.setText("종료 전 요청")
    QTest.mouseClick(window.send_button, Qt.MouseButton.LeftButton)
    wait_until(provider.started.is_set)

    window.close()

    assert window.isVisible()
    assert window.is_busy
    timer_fired = Event()
    QTimer.singleShot(0, timer_fired.set)
    wait_until(timer_fired.is_set)

    provider.release.set()
    wait_until(lambda: not window.is_busy and not window.isVisible())
