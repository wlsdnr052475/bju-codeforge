"""Check the packaged-app smoke path through real subprocess entry points."""

import subprocess
import sys
import textwrap

import pytest


def run_python(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *arguments],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )


def test_smoke_flag_completes_real_module_round_trip() -> None:
    result = run_python("-m", "bju_codeforge", "--smoke-test")

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "provider_result",
    [
        "return 'A response that is not the expected Mock result'",
        "return ''",
        "raise RuntimeError('Deliberate provider failure')",
    ],
    ids=["wrong-response", "invalid-response", "provider-error"],
)
def test_smoke_returns_failure_when_round_trip_is_unsuccessful(provider_result: str) -> None:
    script = textwrap.dedent(
        f"""
        import runpy
        import sys

        import bju_codeforge.gui.app as desktop

        class BadProvider:
            def generate(self, message):
                {provider_result}

        desktop.MockProvider = BadProvider
        sys.argv = ["bju_codeforge", "--smoke-test"]
        runpy.run_module("bju_codeforge", run_name="__main__")
        """
    )

    result = run_python("-c", script)

    assert result.returncode == 1, result.stderr
    assert "Traceback (most recent call last)" not in result.stderr


def test_smoke_waits_for_response_to_be_displayed_before_success() -> None:
    script = textwrap.dedent(
        """
        import runpy
        import sys
        from threading import Event

        from PySide6.QtCore import QTimer

        import bju_codeforge.gui.app as desktop
        from bju_codeforge.providers.mock import MOCK_RESPONSE

        started = Event()
        release = Event()
        completed = Event()
        observed = {"pending": False, "displayed": False}
        received = []

        class DelayedProvider:
            def generate(self, message):
                received.append(message)
                started.set()
                if not release.wait(timeout=5):
                    raise TimeoutError("The GUI did not release the request")
                completed.set()
                return MOCK_RESPONSE

        class ObservedWindow(desktop.MainWindow):
            def __init__(self, agent):
                super().__init__(agent)
                self.release_timer = QTimer(self)
                self.release_timer.timeout.connect(self.release_pending_request)
                self.release_timer.start(5)
                self.request_finished.connect(self.record_displayed_response)

            def release_pending_request(self):
                if started.is_set():
                    observed["pending"] = (
                        self.is_busy
                        and self.ai_responses.toPlainText() == ""
                        and self.isVisible()
                    )
                    self.release_timer.stop()
                    release.set()

            def record_displayed_response(self):
                observed["displayed"] = (
                    completed.is_set()
                    and not self.is_busy
                    and self.ai_responses.toPlainText() == MOCK_RESPONSE
                    and received == [self.user_messages.toPlainText()]
                    and bool(received[0].strip())
                )

        desktop.MockProvider = DelayedProvider
        desktop.MainWindow = ObservedWindow
        sys.argv = ["bju_codeforge", "--smoke-test"]
        try:
            runpy.run_module("bju_codeforge", run_name="__main__")
        except SystemExit as finished:
            assert finished.code == 0, finished.code
        else:
            raise AssertionError("The module did not exit normally")
        assert observed["pending"], "No live window was observed while awaiting the response"
        assert observed["displayed"], "Smoke succeeded before the response was displayed"
        print("delayed-round-trip-ok")
        """
    )

    result = run_python("-c", script)

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "delayed-round-trip-ok"
