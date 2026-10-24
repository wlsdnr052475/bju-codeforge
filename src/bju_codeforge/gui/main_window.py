"""A small desktop chat view with Provider calls outside the GUI thread."""

from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from bju_codeforge.core.agent import ChatAgent


class _ResponseThread(QThread):
    """Execute one agent request without reading or changing any widgets."""

    response_received = Signal(str)
    failed = Signal(str)

    def __init__(self, agent: ChatAgent, message: str, parent: QWidget) -> None:
        super().__init__(parent)
        self._agent = agent
        self._message = message

    def run(self) -> None:
        try:
            response = self._agent.send_message(self._message)
        except Exception as error:
            self.failed.emit(str(error) or type(error).__name__)
        else:
            self.response_received.emit(response)


class MainWindow(QMainWindow):
    """Present messages and coordinate the lifetime of one background request."""

    request_finished = Signal()

    def __init__(self, agent: ChatAgent) -> None:
        super().__init__()
        self._agent = agent
        self._worker: _ResponseThread | None = None
        self._close_pending = False
        self._request_error: str | None = None

        self.setWindowTitle("BJU CodeForge")
        self.resize(820, 600)
        self.setMinimumSize(520, 400)

        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("BJU CodeForge")
        title_font = title.font()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        layout.addWidget(QLabel("MVP 1 · Mock AI 대화"))

        self.user_messages = QPlainTextEdit()
        self.user_messages.setReadOnly(True)
        self.user_messages.setAccessibleName("사용자 메시지")
        self.user_messages.setPlaceholderText("보낸 메시지가 여기에 표시됩니다.")
        self.ai_responses = QPlainTextEdit()
        self.ai_responses.setReadOnly(True)
        self.ai_responses.setAccessibleName("AI 응답")
        self.ai_responses.setPlaceholderText("Mock AI 응답이 여기에 표시됩니다.")
        layout.addWidget(QLabel("사용자 메시지"))
        layout.addWidget(self.user_messages, 1)
        layout.addWidget(QLabel("AI 응답"))
        layout.addWidget(self.ai_responses, 2)

        self.message_input = QLineEdit()
        self.message_input.setAccessibleName("메시지 입력")
        self.message_input.setPlaceholderText("메시지를 입력하고 Enter 또는 전송을 누르세요.")
        self.send_button = QPushButton("전송")
        self.send_button.setEnabled(False)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input, 1)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        self.status_label = QLabel("준비 · Mock Provider")
        self.status_label.setTextFormat(Qt.TextFormat.PlainText)
        self.status_label.setWordWrap(True)
        self.status_label.setAccessibleName("작업 상태")
        layout.addWidget(self.status_label)
        self.setCentralWidget(central)

        self.message_input.textChanged.connect(self._update_send_button)
        self.message_input.returnPressed.connect(self.send_message)
        self.send_button.clicked.connect(self.send_message)
        self.message_input.setFocus()

    @property
    def is_busy(self) -> bool:
        """Whether a request still owns a live background thread."""
        return self._worker is not None

    @Slot()
    def _update_send_button(self) -> None:
        self.send_button.setEnabled(
            not self.is_busy and not self._close_pending and bool(self.message_input.text().strip())
        )

    @Slot()
    def send_message(self) -> None:
        """Submit a nonblank message, refusing duplicate in-flight requests."""
        if self.is_busy or self._close_pending:
            return
        message = self.message_input.text().strip()
        if not message:
            self.status_label.setText("메시지를 입력해 주세요.")
            return

        worker = _ResponseThread(self._agent, message, self)
        self._worker = worker
        self._request_error = None
        worker.response_received.connect(self._show_response)
        worker.failed.connect(self._show_error)
        worker.finished.connect(self._finish_request)

        self.user_messages.appendPlainText(message)
        self.message_input.clear()
        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.status_label.setText("응답을 기다리는 중…")
        worker.start()

    @Slot(str)
    def _show_response(self, response: str) -> None:
        self.ai_responses.appendPlainText(response)

    @Slot(str)
    def _show_error(self, message: str) -> None:
        self._request_error = message

    @Slot()
    def _finish_request(self) -> None:
        worker = self._worker
        self._worker = None
        if worker is not None:
            worker.deleteLater()
        if self._close_pending:
            self.request_finished.emit()
            self.close()
            return

        self.message_input.setEnabled(True)
        self._update_send_button()
        self.status_label.setText(
            f"오류: {self._request_error} · 다시 시도해 주세요."
            if self._request_error is not None
            else "응답 완료 · Mock Provider"
        )
        self.message_input.setFocus()
        self.request_finished.emit()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Defer closing until the thread exits; never forcibly terminate it."""
        if self.is_busy:
            self._close_pending = True
            self.message_input.setEnabled(False)
            self.send_button.setEnabled(False)
            self.status_label.setText("응답 처리 중입니다. 작업이 끝나면 창을 닫습니다.")
            event.ignore()
            return
        super().closeEvent(event)
