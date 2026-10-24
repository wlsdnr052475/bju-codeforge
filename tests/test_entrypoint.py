"""The installed module entry point must show a window and shut down cleanly."""

import subprocess
import sys
import textwrap


def test_module_entrypoint_opens_window_and_exits_normally() -> None:
    script = textwrap.dedent(
        """
        import runpy
        import sys

        from PySide6 import QtWidgets
        from PySide6.QtCore import QTimer

        window_verified = False

        class CheckedApplication(QtWidgets.QApplication):
            def __init__(self, argv):
                super().__init__(argv)
                QTimer.singleShot(0, self.verify_and_close)

            def verify_and_close(self):
                global window_verified
                windows = [
                    window for window in self.topLevelWidgets()
                    if window.isVisible() and window.windowTitle() == "BJU CodeForge"
                ]
                window_verified = len(windows) == 1
                if not window_verified:
                    self.exit(2)
                    return
                windows[0].close()

        QtWidgets.QApplication = CheckedApplication
        sys.argv = ["bju_codeforge"]
        try:
            runpy.run_module("bju_codeforge", run_name="__main__")
        except SystemExit as finished:
            assert finished.code == 0, finished.code
        else:
            raise AssertionError("The module did not return through SystemExit")
        assert window_verified, "The entry point did not show the main window"
        print("module-entrypoint-ok")
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
    assert result.stdout.strip() == "module-entrypoint-ok"
