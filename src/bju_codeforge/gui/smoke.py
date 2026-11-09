"""Internal packaged-app check using the production window and message flow."""

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from bju_codeforge.gui.main_window import MainWindow
from bju_codeforge.providers.mock import MOCK_RESPONSE

SMOKE_MESSAGE = "안녕하세요, BJU CodeForge 실행 검증입니다."


def run_smoke_test(app: QApplication, window: MainWindow, timeout_ms: int = 15_000) -> int:
    """Return zero only after a validated message round trip and normal close.

    A timeout fails the check and requests safe closure. A stuck worker still
    needs the caller's process timeout; terminating Qt worker threads is unsafe.
    """
    outcome = 1
    submitted = False
    expired = False
    completed = False
    previous_quit_policy = app.quitOnLastWindowClosed()
    app.setQuitOnLastWindowClosed(False)
    deadline = QTimer(window)
    deadline.setSingleShot(True)

    def finish(code: int) -> None:
        nonlocal outcome, completed
        if completed:
            return
        outcome = code
        # MainWindow defers closure while a worker runs. Wait for its completion
        # signal rather than destroying a live QThread during process shutdown.
        accepted = window.close()
        if window.is_busy:
            return
        completed = True
        deadline.stop()
        if not accepted or window.isVisible():
            outcome = 1
        app.exit(outcome)

    def check_response() -> None:
        valid = (
            submitted
            and not expired
            and window.isVisible()
            and window.windowTitle() == "BJU CodeForge"
            and window.user_messages.toPlainText() == SMOKE_MESSAGE
            and window.ai_responses.toPlainText() == MOCK_RESPONSE
            and not window.is_busy
            and window.message_input.isEnabled()
            and window.message_input.text() == ""
            and not window.send_button.isEnabled()
            and window.status_label.text() == "응답 완료 · Mock Provider"
        )
        finish(0 if valid else 1)

    def submit_message() -> None:
        nonlocal submitted
        if not window.isVisible() or window.windowTitle() != "BJU CodeForge":
            finish(1)
            return
        window.message_input.setText(SMOKE_MESSAGE)
        if not window.message_input.isEnabled() or not window.send_button.isEnabled():
            finish(1)
            return
        submitted = True
        window.send_button.click()

    def time_out() -> None:
        nonlocal expired
        expired = True
        finish(1)

    window.request_finished.connect(check_response)
    deadline.timeout.connect(time_out)
    deadline.start(timeout_ms)
    QTimer.singleShot(0, submit_message)
    exit_code = app.exec()
    deadline.stop()
    window.request_finished.disconnect(check_response)
    app.setQuitOnLastWindowClosed(previous_quit_policy)
    return 0 if completed and outcome == 0 and exit_code == 0 else 1
